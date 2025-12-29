"""
ER AI SDK - 提供简单的API接口。
"""
from typing import Optional, Iterator, Callable
from x007007007.er_ai.modeler import ERModeler


def generate_er_model(
    requirement: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    max_retries: int = 3,
    stream: bool = False,
    on_chunk: Optional[Callable[[str], None]] = None
) -> str:
    """
    根据需求描述生成TOML格式的ER配置（SDK接口）。
    
    Args:
        requirement: 需求描述，例如"设计一个博客系统，包含用户、文章、标签等实体"
        api_key: DeepSeek API密钥，如果不提供则从环境变量DEEPSEEK_API_KEY读取
        base_url: DeepSeek API基础URL，默认使用官方API
        max_retries: 最大重试次数（默认3次）
        stream: 是否使用流式输出（默认False）
        on_chunk: 流式输出时的回调函数，接收每个chunk作为参数
        
    Returns:
        str: TOML格式的ER配置
        
    Example:
        >>> toml_config = generate_er_model(
        ...     "设计一个博客系统，包含用户、文章、标签等实体"
        ... )
        >>> print(toml_config)
        
        >>> # 使用流式输出
        >>> def on_chunk(chunk):
        ...     print(chunk, end='', flush=True)
        >>> toml_config = generate_er_model(
        ...     "设计一个博客系统",
        ...     stream=True,
        ...     on_chunk=on_chunk
        ... )
    """
    assert isinstance(requirement, str), "requirement must be a string"
    assert len(requirement.strip()) > 0, "requirement cannot be empty"
    
    modeler = ERModeler(api_key=api_key, base_url=base_url)
    return modeler.generate_toml(
        requirement=requirement,
        max_retries=max_retries,
        stream=stream,
        on_chunk=on_chunk
    )


def refine_er_model(
    existing_toml: str,
    modification_request: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    max_retries: int = 3,
    stream: bool = False,
    on_chunk: Optional[Callable[[str], None]] = None
) -> str:
    """
    基于现有TOML配置进行修改和完善（SDK接口）。
    
    Args:
        existing_toml: 现有的TOML ER配置内容
        modification_request: 修改需求描述，例如"添加一个评论实体，与文章建立一对多关系"
        api_key: DeepSeek API密钥，如果不提供则从环境变量DEEPSEEK_API_KEY读取
        base_url: DeepSeek API基础URL，默认使用官方API
        max_retries: 最大重试次数（默认3次）
        stream: 是否使用流式输出（默认False）
        on_chunk: 流式输出时的回调函数，接收每个chunk作为参数
        
    Returns:
        str: 修改后的TOML格式的ER配置
        
    Example:
        >>> # 读取现有TOML
        >>> with open('existing.toml', 'r') as f:
        ...     existing = f.read()
        >>> 
        >>> # 进行修改
        >>> refined = refine_er_model(
        ...     existing,
        ...     "添加一个评论实体，与文章建立一对多关系"
        ... )
        >>> 
        >>> # 保存修改后的配置
        >>> with open('refined.toml', 'w') as f:
        ...     f.write(refined)
    """
    assert isinstance(existing_toml, str), "existing_toml must be a string"
    assert len(existing_toml.strip()) > 0, "existing_toml cannot be empty"
    assert isinstance(modification_request, str), "modification_request must be a string"
    assert len(modification_request.strip()) > 0, "modification_request cannot be empty"
    
    modeler = ERModeler(api_key=api_key, base_url=base_url)
    return modeler.refine_toml(
        existing_toml=existing_toml,
        modification_request=modification_request,
        max_retries=max_retries,
        stream=stream,
        on_chunk=on_chunk
    )

