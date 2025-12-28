import click
import logging
import sys
from x007007007.er.parsers import MermaidParser
from x007007007.er.plantuml_parser import PlantUMLParser
from x007007007.er.db_parser import DBParser
from x007007007.er.renderers import DjangoRenderer, SQLAlchemyRenderer

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@click.group()
def main():
    """ER Diagram Converter and Code Generator."""
    pass

@main.command()
@click.argument('input_source')
@click.option('--input-type', '-t', type=click.Choice(['mermaid', 'plantuml', 'db']), default='mermaid', help='Input type')
@click.option('--format', '-f', type=click.Choice(['django', 'sqlalchemy']), default='django', help='Output format')
@click.option('--output', '-o', type=click.File('w'), default=sys.stdout, help='Output file')
def convert(input_source, input_type, format, output):
    """Convert ER diagram file to code."""
    try:
        if input_type == 'db':
            parser = DBParser()
            model = parser.parse(input_source)
        else:
            with open(input_source, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if input_type == 'mermaid':
                parser = MermaidParser()
            else:
                parser = PlantUMLParser()
            model = parser.parse(content)
        
        if format == 'django':
            renderer = DjangoRenderer()
        else:
            renderer = SQLAlchemyRenderer()
            
        result = renderer.render(model)
        output.write(result)
        logger.info(f"Successfully converted {input_source} to {format}")
        
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
