"""
使用LangChain和DeepSeek进行ER建模。
"""
import os
import logging
from pathlib import Path
from typing import Optional, Iterator, Callable
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from x007007007.er_ai.prompts import get_er_modeling_prompt, get_error_feedback_prompt
from x007007007.er_ai.validator import validate_toml_syntax, extract_toml_from_markdown

# 尝试导入 langchain-deepseek，如果不存在则回退到 langchain-community
try:
    from langchain_deepseek import ChatDeepSeek
    USE_DEEPSEEK_PACKAGE = True
except ImportError:
    try:
        from langchain_community.chat_models import ChatOpenAI as ChatDeepSeek
        USE_DEEPSEEK_PACKAGE = False
        import warnings
        warnings.warn(
            "langchain-deepseek not found, using langchain-community.ChatOpenAI. "
            "Install langchain-deepseek for better support: pip install langchain-deepseek",
            UserWarning
        )
    except ImportError:
        raise ImportError(
            "Neither langchain-deepseek nor langchain-community is available. "
            "Please install langchain-deepseek: pip install langchain-deepseek"
        )

logger = logging.getLogger(__name__)

# 加载.env文件（从项目根目录或当前工作目录）
_env_file = Path(__file__).parent.parent.parent.parent / ".env"
if _env_file.exists():
    load_dotenv(_env_file)
else:
    # 如果项目根目录没有.env，尝试从当前工作目录加载
    load_dotenv()


class ERModeler:
    """
    使用AI进行ER建模的工具类。
    
    支持使用DeepSeek等LLM根据需求描述生成TOML格式的ER配置。
    优先使用 langchain-deepseek 专用包，如果不存在则回退到 langchain-community。
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化ER建模器。
        
        Args:
            api_key: DeepSeek API密钥，如果不提供则从环境变量DEEPSEEK_API_KEY读取
            base_url: DeepSeek API基础URL，默认为 https://api.deepseek.com/v1
        """
        # 获取API密钥（优先使用参数，其次环境变量，最后.env文件）
        if api_key is None:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError(
                    "DeepSeek API key is required. "
                    "Please set DEEPSEEK_API_KEY in .env file, environment variable, or pass api_key parameter."
                )
        
        # 初始化Chat Model
        if USE_DEEPSEEK_PACKAGE:
            # 使用 langchain-deepseek 专用包
            self.llm = ChatDeepSeek(
                model="deepseek-chat",
                temperature=0.3,  # 较低温度以获得更稳定的输出
                api_key=api_key,
            )
        else:
            # 使用 langchain-community 的 ChatOpenAI（兼容模式）
            # 默认使用DeepSeek官方API，也可以从环境变量或.env文件读取
            if base_url is None:
                base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
            
            self.llm = ChatDeepSeek(
                model="deepseek-chat",
                temperature=0.3,  # 较低温度以获得更稳定的输出
                api_key=api_key,
                base_url=base_url,
            )
        
        # 创建Prompt模板（转换为ChatPromptTemplate）
        # 使用Jinja2模板直接获取prompt文本
        from x007007007.er_ai.prompts import get_er_modeling_prompt_text
        
        # 获取系统消息和用户消息模板
        # 系统消息固定
        system_message = "你是一个专业的数据库ER建模专家。"
        
        # 用户消息从Jinja2模板加载（使用占位符，实际渲染在调用时完成）
        prompt_template = get_er_modeling_prompt()
        user_message_template = prompt_template.template
        
        # 创建ChatPromptTemplate
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", user_message_template)
        ])
        
        # 创建错误反馈的Prompt模板
        error_prompt_template = get_error_feedback_prompt()
        self.error_prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", error_prompt_template.template)
        ])
        
        # 创建基于现有TOML修改的Prompt模板
        from x007007007.er_ai.prompts import get_refine_prompt
        refine_prompt_template = get_refine_prompt()
        self.refine_prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", refine_prompt_template.template)
        ])
    
    def refine_toml(
        self,
        existing_toml: str,
        modification_request: str,
        max_retries: int = 3,
        stream: bool = False,
        on_chunk: Optional[Callable[[str], None]] = None
    ) -> str:
        """
        基于现有TOML配置进行修改和完善。
        
        Args:
            existing_toml: 现有的TOML ER配置内容
            modification_request: 修改需求描述，例如"添加一个评论实体，与文章建立一对多关系"
            max_retries: 最大重试次数（默认3次）
            stream: 是否使用流式输出（默认False）
            on_chunk: 流式输出时的回调函数，接收每个chunk作为参数
            
        Returns:
            str: 修改后的TOML格式的ER配置
            
        Raises:
            ValueError: 如果输入为空或生成失败（超过最大重试次数）
        """
        assert isinstance(existing_toml, str), "existing_toml must be a string"
        assert len(existing_toml.strip()) > 0, "existing_toml cannot be empty"
        assert isinstance(modification_request, str), "modification_request must be a string"
        assert len(modification_request.strip()) > 0, "modification_request cannot be empty"
        assert max_retries > 0, "max_retries must be greater than 0"
        
        logger.info(f"Refining TOML configuration (max_retries={max_retries})...")
        
        attempt = 0
        last_error = None
        
        while attempt <= max_retries:
            try:
                if attempt == 0:
                    # 第一次尝试：使用refine prompt
                    chain = self.refine_prompt | self.llm
                    prompt_vars = {
                        "existing_toml": existing_toml,
                        "modification_request": modification_request
                    }
                else:
                    # 重试：使用错误反馈prompt（但保留原始需求）
                    logger.info(f"Retry attempt {attempt}/{max_retries}")
                    chain = self.error_prompt | self.llm
                    prompt_vars = {
                        "requirement": f"基于现有TOML配置进行修改：{modification_request}",
                        "error_message": last_error
                    }
                
                if stream:
                    # 流式输出
                    content_parts = []
                    try:
                        # 使用astream_events或stream方法
                        # 注意：LangChain的stream可能返回不同类型的对象
                        stream_iter = chain.stream(prompt_vars)
                        for chunk in stream_iter:
                            # 处理不同类型的chunk
                            chunk_content = None
                            if hasattr(chunk, 'content'):
                                # AIMessageChunk对象
                                chunk_content = chunk.content
                            elif isinstance(chunk, dict):
                                # 字典格式
                                if 'content' in chunk:
                                    chunk_content = chunk['content']
                                elif 'delta' in chunk and 'content' in chunk['delta']:
                                    chunk_content = chunk['delta']['content']
                            elif isinstance(chunk, str):
                                chunk_content = chunk
                            else:
                                # 尝试转换为字符串
                                chunk_content = str(chunk) if chunk else None
                            
                            if chunk_content:
                                content_parts.append(chunk_content)
                                if on_chunk:
                                    try:
                                        on_chunk(chunk_content)
                                    except Exception as callback_error:
                                        logger.warning(f"Error in on_chunk callback: {callback_error}")
                    except Exception as stream_error:
                        # 如果流式输出失败，记录错误但继续处理已收集的内容
                        logger.error(f"Stream error: {stream_error}", exc_info=True)
                        # 如果没有任何内容，抛出异常
                        if not content_parts:
                            raise
                    
                    content = "".join(content_parts)
                    # 如果流式输出后内容为空，记录警告
                    if not content.strip():
                        logger.warning("Stream completed but no content was received")
                else:
                    # 非流式输出
                    result = chain.invoke(prompt_vars)
                    content = result.content if hasattr(result, 'content') else str(result)
                
                # 清理输出，移除可能的markdown代码块标记
                toml_content = self._clean_output(content)
                
                # 提取TOML内容（如果包含在markdown代码块中）
                toml_content = extract_toml_from_markdown(toml_content)
                
                # 验证TOML语法
                is_valid, error_msg = validate_toml_syntax(toml_content)
                
                if is_valid:
                    logger.info("TOML validation passed")
                    return toml_content
                else:
                    # 验证失败，记录错误并重试
                    last_error = error_msg
                    logger.warning(f"TOML validation failed (attempt {attempt + 1}/{max_retries + 1}): {error_msg}")
                    attempt += 1
                    continue
                    
            except Exception as e:
                logger.error(f"Error refining TOML (attempt {attempt + 1}): {e}")
                if attempt >= max_retries:
                    raise ValueError(f"Failed to refine TOML after {max_retries + 1} attempts: {e}") from e
                attempt += 1
                last_error = f"生成过程中出现异常: {str(e)}"
                continue
        
        # 如果所有重试都失败
        raise ValueError(
            f"Failed to refine valid TOML after {max_retries + 1} attempts. "
            f"Last error: {last_error}"
        )
    
    def generate_toml(
        self,
        requirement: str,
        max_retries: int = 3,
        stream: bool = False,
        on_chunk: Optional[Callable[[str], None]] = None
    ) -> str:
        """
        根据需求描述生成TOML格式的ER配置，支持语法验证和重试。
        
        Args:
            requirement: 需求描述，例如"设计一个博客系统，包含用户、文章、标签等实体"
            max_retries: 最大重试次数（默认3次）
            stream: 是否使用流式输出（默认False）
            on_chunk: 流式输出时的回调函数，接收每个chunk作为参数
            
        Returns:
            str: TOML格式的ER配置
            
        Raises:
            ValueError: 如果需求为空或生成失败（超过最大重试次数）
        """
        assert isinstance(requirement, str), "requirement must be a string"
        assert len(requirement.strip()) > 0, "requirement cannot be empty"
        assert max_retries > 0, "max_retries must be greater than 0"
        
        logger.info(f"Generating ER model from requirement (max_retries={max_retries})...")
        
        current_requirement = requirement
        attempt = 0
        last_error = None
        
        while attempt <= max_retries:
            try:
                if attempt == 0:
                    # 第一次尝试：使用原始prompt
                    chain = self.prompt | self.llm
                    prompt_vars = {"requirement": current_requirement}
                else:
                    # 重试：使用错误反馈prompt
                    logger.info(f"Retry attempt {attempt}/{max_retries}")
                    chain = self.error_prompt | self.llm
                    prompt_vars = {
                        "requirement": requirement,
                        "error_message": last_error
                    }
                
                if stream:
                    # 流式输出
                    content_parts = []
                    try:
                        # 使用astream_events或stream方法
                        # 注意：LangChain的stream可能返回不同类型的对象
                        stream_iter = chain.stream(prompt_vars)
                        for chunk in stream_iter:
                            # 处理不同类型的chunk
                            chunk_content = None
                            if hasattr(chunk, 'content'):
                                # AIMessageChunk对象
                                chunk_content = chunk.content
                            elif isinstance(chunk, dict):
                                # 字典格式
                                if 'content' in chunk:
                                    chunk_content = chunk['content']
                                elif 'delta' in chunk and 'content' in chunk['delta']:
                                    chunk_content = chunk['delta']['content']
                            elif isinstance(chunk, str):
                                chunk_content = chunk
                            else:
                                # 尝试转换为字符串
                                chunk_content = str(chunk) if chunk else None
                            
                            if chunk_content:
                                content_parts.append(chunk_content)
                                if on_chunk:
                                    try:
                                        on_chunk(chunk_content)
                                    except Exception as callback_error:
                                        logger.warning(f"Error in on_chunk callback: {callback_error}")
                    except Exception as stream_error:
                        # 如果流式输出失败，记录错误但继续处理已收集的内容
                        logger.error(f"Stream error: {stream_error}", exc_info=True)
                        # 如果没有任何内容，抛出异常
                        if not content_parts:
                            raise
                    
                    content = "".join(content_parts)
                    # 如果流式输出后内容为空，记录警告
                    if not content.strip():
                        logger.warning("Stream completed but no content was received")
                else:
                    # 非流式输出
                    result = chain.invoke(prompt_vars)
                    content = result.content if hasattr(result, 'content') else str(result)
                
                # 清理输出，移除可能的markdown代码块标记
                toml_content = self._clean_output(content)
                
                # 提取TOML内容（如果包含在markdown代码块中）
                toml_content = extract_toml_from_markdown(toml_content)
                
                # 验证TOML语法
                is_valid, error_msg = validate_toml_syntax(toml_content)
                
                if is_valid:
                    logger.info("TOML validation passed")
                    return toml_content
                else:
                    # 验证失败，记录错误并重试
                    last_error = error_msg
                    logger.warning(f"TOML validation failed (attempt {attempt + 1}/{max_retries + 1}): {error_msg}")
                    attempt += 1
                    continue
                    
            except Exception as e:
                logger.error(f"Error generating ER model (attempt {attempt + 1}): {e}")
                if attempt >= max_retries:
                    raise ValueError(f"Failed to generate ER model after {max_retries + 1} attempts: {e}") from e
                attempt += 1
                last_error = f"生成过程中出现异常: {str(e)}"
                continue
        
        # 如果所有重试都失败
        raise ValueError(
            f"Failed to generate valid TOML after {max_retries + 1} attempts. "
            f"Last error: {last_error}"
        )
    
    def generate_toml_stream(
        self,
        requirement: str,
        max_retries: int = 3,
        on_chunk: Optional[Callable[[str], None]] = None
    ) -> Iterator[str]:
        """
        流式生成TOML格式的ER配置（生成器版本）。
        
        Args:
            requirement: 需求描述
            max_retries: 最大重试次数
            on_chunk: 每个chunk的回调函数
            
        Yields:
            str: TOML内容的chunk
            
        Note:
            由于需要验证完整内容，流式输出会在生成完成后进行验证。
            如果验证失败，会触发重试（但不会流式输出重试过程）。
        """
        assert isinstance(requirement, str), "requirement must be a string"
        assert len(requirement.strip()) > 0, "requirement cannot be empty"
        
        # 先收集所有chunk
        chunks = []
        
        def collect_chunk(chunk: str):
            chunks.append(chunk)
            if on_chunk:
                on_chunk(chunk)
        
        # 使用流式生成
        result = self.generate_toml(
            requirement=requirement,
            max_retries=max_retries,
            stream=True,
            on_chunk=collect_chunk
        )
        
        # 返回结果（如果需要，也可以yield chunks）
        yield result
    
    def _clean_output(self, output: str) -> str:
        """
        清理LLM输出，移除可能的markdown代码块标记。
        
        Args:
            output: LLM的原始输出
            
        Returns:
            str: 清理后的TOML内容
        """
        # 移除可能的markdown代码块标记
        output = output.strip()
        
        # 如果包含```toml或```，移除这些标记
        if output.startswith("```"):
            lines = output.split("\n")
            # 移除第一行（```toml或```）
            if lines[0].startswith("```"):
                lines = lines[1:]
            # 移除最后一行（```）
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            output = "\n".join(lines)
        
        return output.strip()

