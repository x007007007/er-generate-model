"""
ER AI命令行工具。
"""
import click
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
from x007007007.er.version import get_version
from x007007007.er_ai.modeler import ERModeler

# 加载.env文件（从项目根目录或当前工作目录）
_env_file = Path(__file__).parent.parent.parent.parent / ".env"
if _env_file.exists():
    load_dotenv(_env_file)
else:
    # 如果项目根目录没有.env，尝试从当前工作目录加载
    load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version=get_version(), prog_name="er-ai")
def main():
    """AI-powered ER modeling tool using LangChain and DeepSeek."""
    pass


@main.command()
@click.argument('requirement', required=False)
@click.option('--api-key', envvar='DEEPSEEK_API_KEY', help='DeepSeek API key (or set DEEPSEEK_API_KEY env var)')
@click.option('--base-url', help='DeepSeek API base URL (optional)')
@click.option('--output', '-o', type=click.Path(), default=None, help='Output file path (default: stdout)')
@click.option('--input-file', '-i', type=click.File('r', encoding='utf-8'), help='Read requirement from file')
@click.option('--max-retries', '-r', type=int, default=3, help='Maximum number of retries on validation failure (default: 3)')
@click.option('--stream', is_flag=True, help='Enable streaming output')
def generate(requirement, api_key, base_url, output, input_file, max_retries, stream):
    """
    根据需求描述生成TOML格式的ER配置。
    
    REQUIREMENT: 需求描述（如果提供了--input-file，则从文件读取）
    """
    # 获取需求内容
    if input_file:
        requirement_text = input_file.read().strip()
    elif requirement:
        requirement_text = requirement
    else:
        # 从标准输入读取
        logger.info("Reading requirement from stdin...")
        requirement_text = sys.stdin.read().strip()
    
    if not requirement_text:
        logger.error("Requirement is empty. Please provide requirement via argument, file, or stdin.")
        sys.exit(1)
    
    try:
        # 创建建模器
        modeler = ERModeler(api_key=api_key, base_url=base_url)
        
        # 生成TOML配置
        logger.info(f"Generating ER model (max_retries={max_retries}, stream={stream})...")
        
        # 处理输出文件
        if output:
            # 如果指定了输出文件，使用UTF-8编码打开
            output_file = open(output, 'w', encoding='utf-8')
            should_close = True
        else:
            # 使用标准输出
            output_file = sys.stdout
            should_close = False
        
        try:
            if stream:
                # 流式输出
                def on_chunk(chunk):
                    output_file.write(chunk)
                    output_file.flush()
                
                toml_config = modeler.generate_toml(
                    requirement_text,
                    max_retries=max_retries,
                    stream=True,
                    on_chunk=on_chunk
                )
                # 确保最后有换行
                if not toml_config.endswith('\n'):
                    output_file.write('\n')
            else:
                # 非流式输出
                toml_config = modeler.generate_toml(
                    requirement_text,
                    max_retries=max_retries,
                    stream=False
                )
                output_file.write(toml_config)
                if not toml_config.endswith('\n'):
                    output_file.write('\n')
            
            logger.info("ER model generated and validated successfully!")
        finally:
            if should_close:
                output_file.close()
        
    except ValueError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


@main.command()
@click.argument('existing_toml_file', type=click.Path(exists=True))
@click.argument('modification_request', required=False)
@click.option('--api-key', envvar='DEEPSEEK_API_KEY', help='DeepSeek API key (or set DEEPSEEK_API_KEY env var)')
@click.option('--base-url', help='DeepSeek API base URL (optional)')
@click.option('--output', '-o', type=click.Path(), default=None, help='Output file path (default: stdout)')
@click.option('--modification-file', '-m', type=click.File('r', encoding='utf-8'), help='Read modification request from file')
@click.option('--max-retries', '-r', type=int, default=3, help='Maximum number of retries on validation failure (default: 3)')
@click.option('--stream', is_flag=True, help='Enable streaming output')
def refine(existing_toml_file, modification_request, api_key, base_url, output, modification_file, max_retries, stream):
    """
    基于现有TOML文件进行修改和完善。
    
    EXISTING_TOML_FILE: 现有的TOML ER配置文件路径
    MODIFICATION_REQUEST: 修改需求描述（如果提供了--modification-file，则从文件读取）
    """
    # 读取现有TOML文件（使用UTF-8编码）
    try:
        with open(existing_toml_file, 'r', encoding='utf-8') as f:
            existing_toml = f.read()
    except UnicodeDecodeError:
        # 如果UTF-8失败，尝试GBK（Windows常见编码）
        try:
            with open(existing_toml_file, 'r', encoding='gbk') as f:
                existing_toml = f.read()
            logger.warning(f"File {existing_toml_file} is not UTF-8 encoded, read as GBK. Consider converting to UTF-8.")
        except Exception as e:
            logger.error(f"Error reading TOML file {existing_toml_file}: {e}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading TOML file {existing_toml_file}: {e}")
        sys.exit(1)
    
    # 获取修改需求
    if modification_file:
        modification_text = modification_file.read().strip()
    elif modification_request:
        modification_text = modification_request
    else:
        # 从标准输入读取
        logger.info("Reading modification request from stdin...")
        modification_text = sys.stdin.read().strip()
    
    if not modification_text:
        logger.error("Modification request is empty. Please provide modification request via argument, file, or stdin.")
        sys.exit(1)
    
    try:
        # 创建建模器
        modeler = ERModeler(api_key=api_key, base_url=base_url)
        
        # 修改TOML配置
        logger.info(f"Refining TOML configuration (max_retries={max_retries}, stream={stream})...")
        
        # 处理输出文件
        if output:
            # 如果指定了输出文件，使用UTF-8编码打开
            output_file = open(output, 'w', encoding='utf-8')
            should_close = True
        else:
            # 使用标准输出
            output_file = sys.stdout
            should_close = False
        
        try:
            if stream:
                # 流式输出
                def on_chunk(chunk):
                    output_file.write(chunk)
                    output_file.flush()
                
                refined_toml = modeler.refine_toml(
                    existing_toml,
                    modification_text,
                    max_retries=max_retries,
                    stream=True,
                    on_chunk=on_chunk
                )
                # 确保最后有换行
                if not refined_toml.endswith('\n'):
                    output_file.write('\n')
            else:
                # 非流式输出
                refined_toml = modeler.refine_toml(
                    existing_toml,
                    modification_text,
                    max_retries=max_retries,
                    stream=False
                )
                output_file.write(refined_toml)
                if not refined_toml.endswith('\n'):
                    output_file.write('\n')
            
            logger.info("TOML configuration refined and validated successfully!")
        finally:
            if should_close:
                output_file.close()
        
    except ValueError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

