"""
CLI plugin for AI-assisted ER modeling.
This module is imported by er-gen-tool when the AI package is installed.
"""
import sys
import click
from pathlib import Path
from typing import Optional
from .modeler import ERModeler


@click.group()
def ai_assist_cmd():
    """AI-powered ER modeling (requires AI dependencies)"""
    pass


@ai_assist_cmd.command()
@click.argument('requirement', required=False)
@click.option('--api-key', envvar='DEEPSEEK_API_KEY', help='DeepSeek API key (or set DEEPSEEK_API_KEY env var)')
@click.option('--output', '-o', type=click.Path(), help='Output file path for generated TOML')
@click.option('--stream/--no-stream', default=False, help='Enable streaming output')
@click.option('--max-retries', default=3, type=int, help='Maximum retry attempts for validation')
def generate(requirement: Optional[str], api_key: Optional[str], output: Optional[str], stream: bool, max_retries: int):
    """Generate ER model from requirements.
    
    Examples:
        er-gen-tool ai-assist generate "设计一个博客系统"
        er-gen-tool ai-assist generate "设计一个电商系统" -o output.toml
        echo "设计一个博客系统" | er-gen-tool ai-assist generate
    """
    # 如果没有提供requirement参数，尝试从stdin读取
    if not requirement:
        if not sys.stdin.isatty():
            requirement = sys.stdin.read().strip()
        else:
            click.echo("Error: requirement is required. Provide it as an argument or via stdin.", err=True)
            click.echo("Usage: er-gen-tool ai-assist generate <requirement>", err=True)
            sys.exit(1)
    
    if not requirement:
        click.echo("Error: requirement cannot be empty", err=True)
        sys.exit(1)
    
    try:
        # 初始化modeler
        modeler = ERModeler(api_key=api_key)
        
        # 生成TOML
        if stream:
            click.echo("Generating ER model (streaming)...", err=True)
            
            def on_chunk(chunk: str):
                click.echo(chunk, nl=False)
            
            toml_content = modeler.generate_toml(
                requirement=requirement,
                max_retries=max_retries,
                stream=True,
                on_chunk=on_chunk
            )
            click.echo()  # 换行
        else:
            click.echo("Generating ER model...", err=True)
            toml_content = modeler.generate_toml(
                requirement=requirement,
                max_retries=max_retries,
                stream=False
            )
        
        # 输出结果
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(toml_content, encoding='utf-8')
            click.echo(f"Generated TOML saved to: {output}", err=True)
        else:
            click.echo(toml_content)
        
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@ai_assist_cmd.command()
@click.argument('existing_toml_file', type=click.Path(exists=True))
@click.argument('modification_request', required=False)
@click.option('--api-key', envvar='DEEPSEEK_API_KEY', help='DeepSeek API key (or set DEEPSEEK_API_KEY env var)')
@click.option('--output', '-o', type=click.Path(), help='Output file path for refined TOML')
@click.option('--stream/--no-stream', default=False, help='Enable streaming output')
@click.option('--max-retries', default=3, type=int, help='Maximum retry attempts for validation')
def refine(existing_toml_file: str, modification_request: Optional[str], api_key: Optional[str], 
           output: Optional[str], stream: bool, max_retries: int):
    """Refine existing TOML configuration.
    
    Examples:
        er-gen-tool ai-assist refine existing.toml "添加评论功能"
        er-gen-tool ai-assist refine existing.toml "添加评论功能" -o refined.toml
        echo "添加评论功能" | er-gen-tool ai-assist refine existing.toml
    """
    # 读取现有TOML文件
    try:
        existing_toml = Path(existing_toml_file).read_text(encoding='utf-8')
    except Exception as e:
        click.echo(f"Error reading file {existing_toml_file}: {e}", err=True)
        sys.exit(1)
    
    # 如果没有提供modification_request参数，尝试从stdin读取
    if not modification_request:
        if not sys.stdin.isatty():
            modification_request = sys.stdin.read().strip()
        else:
            click.echo("Error: modification_request is required. Provide it as an argument or via stdin.", err=True)
            click.echo("Usage: er-gen-tool ai-assist refine <existing_toml_file> <modification_request>", err=True)
            sys.exit(1)
    
    if not modification_request:
        click.echo("Error: modification_request cannot be empty", err=True)
        sys.exit(1)
    
    try:
        # 初始化modeler
        modeler = ERModeler(api_key=api_key)
        
        # 修改TOML
        if stream:
            click.echo("Refining TOML configuration (streaming)...", err=True)
            
            def on_chunk(chunk: str):
                click.echo(chunk, nl=False)
            
            toml_content = modeler.refine_toml(
                existing_toml=existing_toml,
                modification_request=modification_request,
                max_retries=max_retries,
                stream=True,
                on_chunk=on_chunk
            )
            click.echo()  # 换行
        else:
            click.echo("Refining TOML configuration...", err=True)
            toml_content = modeler.refine_toml(
                existing_toml=existing_toml,
                modification_request=modification_request,
                max_retries=max_retries,
                stream=False
            )
        
        # 输出结果
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(toml_content, encoding='utf-8')
            click.echo(f"Refined TOML saved to: {output}", err=True)
        else:
            click.echo(toml_content)
        
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@ai_assist_cmd.command()
@click.argument('existing_toml_file', type=click.Path(exists=True))
@click.option('--api-key', envvar='DEEPSEEK_API_KEY', help='DeepSeek API key (or set DEEPSEEK_API_KEY env var)')
@click.option('--output', '-o', type=click.Path(), help='Output file path for refined TOML')
@click.option('--max-retries', default=3, type=int, help='Maximum retry attempts for validation')
def chat(existing_toml_file: str, api_key: Optional[str], output: Optional[str], max_retries: int):
    """Interactive refinement of TOML configuration.
    
    Examples:
        er-gen-tool ai-assist chat existing.toml
        er-gen-tool ai-assist chat existing.toml -o refined.toml
    """
    # 读取现有TOML文件
    try:
        existing_toml = Path(existing_toml_file).read_text(encoding='utf-8')
    except Exception as e:
        click.echo(f"Error reading file {existing_toml_file}: {e}", err=True)
        sys.exit(1)
    
    try:
        # 初始化modeler
        modeler = ERModeler(api_key=api_key)
        
        click.echo("Interactive TOML refinement mode. Type your modification requests.")
        click.echo("Type 'quit' or 'exit' to finish and save.")
        click.echo("=" * 60)
        
        current_toml = existing_toml
        
        while True:
            # 获取用户输入
            try:
                modification_request = click.prompt("\nModification request", type=str)
            except (EOFError, KeyboardInterrupt):
                click.echo("\nExiting chat mode...")
                break
            
            # 检查退出命令
            if modification_request.lower() in ['quit', 'exit', 'q']:
                break
            
            if not modification_request.strip():
                click.echo("Error: modification request cannot be empty", err=True)
                continue
            
            # 执行修改
            try:
                click.echo("Refining TOML configuration...", err=True)
                current_toml = modeler.refine_toml(
                    existing_toml=current_toml,
                    modification_request=modification_request,
                    max_retries=max_retries,
                    stream=False
                )
                click.echo("\n--- Updated TOML ---")
                click.echo(current_toml)
                click.echo("--- End of TOML ---\n")
            except ValueError as e:
                click.echo(f"Error: {e}", err=True)
                click.echo("Please try a different modification request.", err=True)
                continue
        
        # 保存最终结果
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(current_toml, encoding='utf-8')
            click.echo(f"\nFinal TOML saved to: {output}", err=True)
        else:
            click.echo("\n=== Final TOML ===")
            click.echo(current_toml)
        
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)
