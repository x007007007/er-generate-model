import click
import logging
import sys
import os
from pathlib import Path
from x007007007.er.version import get_version
from x007007007.er.parser.antlr.plantuml_antlr_parser import PlantUMLAntlrParser
from x007007007.er.parser.antlr.mermaid_antlr_parser import MermaidAntlrParser
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.db_parser import DBParser
from x007007007.er.renderers import DjangoRenderer, SQLAlchemyRenderer
from x007007007.er.converters import MermaidConverter, PlantUMLConverter

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def get_default_app_label(input_source: str) -> str:
    """Get default app label from input file name."""
    assert isinstance(input_source, str), "input_source must be a string"
    if os.path.isfile(input_source):
        # Get filename without extension
        filename = Path(input_source).stem
        # Convert to lowercase and replace special chars with underscores
        app_label = filename.lower().replace('-', '_').replace(' ', '_')
        return app_label
    return 'app'

def get_default_table_prefix(input_source: str) -> str:
    """Get default table prefix from input file name."""
    assert isinstance(input_source, str), "input_source must be a string"
    if os.path.isfile(input_source):
        # Get filename without extension
        filename = Path(input_source).stem
        # Convert to lowercase and replace special chars with underscores
        prefix = filename.lower().replace('-', '_').replace(' ', '_')
        return prefix
    return ''

@click.group()
@click.version_option(version=get_version(), prog_name="er-convert")
def main():
    """ER Diagram Converter and Code Generator."""
    pass

@main.command()
@click.argument('input_source')
@click.option('--input-type', '-t', type=click.Choice(['mermaid', 'plantuml', 'db', 'toml']), default='mermaid', help='Input type')
@click.option('--format', '-f', type=click.Choice(['django', 'sqlalchemy', 'mermaid', 'plantuml']), default='django', help='Output format')
@click.option('--output', '-o', type=click.Path(), default=None, help='Output file path (default: stdout, UTF-8 encoded)')
@click.option('--app-label', '-a', type=str, default=None, help='Django app label (default: filename without extension)')
@click.option('--table-prefix', '-p', type=str, default=None, help='Table name prefix (default: filename without extension)')
def convert(input_source, input_type, format, output, app_label, table_prefix):
    """Convert ER diagram file to code."""
    assert isinstance(input_source, str), "input_source must be a string"
    assert len(input_source) > 0, "input_source cannot be empty"
    assert input_type in ['mermaid', 'plantuml', 'db', 'toml'], "Invalid input_type"
    assert format in ['django', 'sqlalchemy', 'mermaid', 'plantuml'], "Invalid format"
    
    # Determine app_label and table_prefix
    if app_label is None:
        app_label = get_default_app_label(input_source)
    if table_prefix is None:
        table_prefix = get_default_table_prefix(input_source)
    
    # Parse input
    if input_type == 'db':
        parser = DBParser()
        model = parser.parse(input_source)
    else:
        # File operations may fail, so we need try-except here
        try:
            with open(input_source, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            logger.error(f"File not found: {input_source}")
            sys.exit(1)
        except IOError as e:
            logger.error(f"Error reading file {input_source}: {e}")
            sys.exit(1)
        
        assert len(content) > 0, f"File {input_source} is empty"
        
        if input_type == 'mermaid':
            parser = MermaidAntlrParser()
        elif input_type == 'plantuml':
            parser = PlantUMLAntlrParser()
        elif input_type == 'toml':
            parser = TomlERParser()
        else:
            raise ValueError(f"Unknown input type: {input_type}")
        
        model = parser.parse(content)
    
    # Render or convert output
    if format == 'django':
        renderer = DjangoRenderer(app_label=app_label, table_prefix=table_prefix)
        result = renderer.render(model)
    elif format == 'sqlalchemy':
        renderer = SQLAlchemyRenderer(table_prefix=table_prefix)
        result = renderer.render(model)
    elif format == 'mermaid':
        converter = MermaidConverter()
        result = converter.convert(model)
    elif format == 'plantuml':
        converter = PlantUMLConverter()
        result = converter.convert(model)
    else:
        raise ValueError(f"Unknown format: {format}")
    
    # 处理输出文件（使用UTF-8编码）
    if output:
        # 如果指定了输出文件，使用UTF-8编码打开
        with open(output, 'w', encoding='utf-8') as output_file:
            output_file.write(result)
    else:
        # 使用标准输出
        sys.stdout.write(result)
    
    logger.info(f"Successfully converted {input_source} to {format}")

if __name__ == '__main__':
    main()
