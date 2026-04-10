"""
Convert subcommand - Convert ER diagrams to code
"""
import click
import logging
import sys
import os
import tempfile
import zipfile
from pathlib import Path
from x007007007.er.version import get_version
from x007007007.er.parser.antlr.plantuml_antlr_parser import PlantUMLAntlrParser
from x007007007.er.parser.antlr.mermaid_antlr_parser import MermaidAntlrParser
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.db_parser import DBParser
from x007007007.er.renderers import DjangoRenderer, SQLAlchemyRenderer, DjangoPackageRenderer
from x007007007.er.converters import MermaidConverter, PlantUMLConverter

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def _extract_zip_toml_files(input_source: str) -> tuple[str, list[str], str]:
    assert isinstance(input_source, str), "input_source must be a string"
    tmp_dir = tempfile.mkdtemp(prefix='er_gen_zip_')
    toml_files: list[str] = []
    with zipfile.ZipFile(input_source, 'r') as zf:
        zf.extractall(tmp_dir)
        for name in sorted(zf.namelist()):
            if name.endswith('.toml') and not name.startswith('__MACOSX'):
                toml_files.append(os.path.join(tmp_dir, name))

    if not toml_files:
        logger.error(f"No .toml files found in ZIP archive: {input_source}")
        sys.exit(1)

    main_file = toml_files[0]
    extra_files = toml_files[1:]
    logger.info(f"Extracted {len(toml_files)} TOML file(s) from ZIP: {[os.path.basename(f) for f in toml_files]}")
    return main_file, extra_files, tmp_dir


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


@click.command()
@click.argument('input_source')
@click.option('--input-type', '-t', type=click.Choice(['mermaid', 'plantuml', 'db', 'toml']), default=None, help='Input type (auto-detected for .zip files)')
@click.option('--format', '-f', type=click.Choice(['django', 'sqlalchemy', 'mermaid', 'plantuml']), default='django', help='Output format')
@click.option('--framework', type=click.Choice(['django', 'sqlalchemy']), default=None, help='Target framework (alias for --format)')
@click.option('--output', '-o', type=click.Path(), default=None, help='Output file path (default: stdout, UTF-8 encoded)')
@click.option('--output-dir', '-d', type=click.Path(), default=None, help='Output directory for multi-file output (Django package mode)')
@click.option('--app-label', '-a', type=str, default=None, help='Django app label (default: filename without extension)')
@click.option('--table-prefix', '-p', type=str, default=None, help='Table name prefix (default: filename without extension)')
@click.option('--split-models', is_flag=True, help='Split Django models into separate files (one per model)')
@click.option('--inheritance-mode', '-i', type=click.Choice(['reference', 'flatten'], case_sensitive=False), default='reference', help='Inheritance handling mode: reference (generate mixin files, use Python inheritance) or flatten (expand all inherited fields directly into entity classes)')
@click.option('--base-model-import', type=str, default=None, help='Custom base model import path for SQLAlchemy (e.g., kinkotech.base_sqlalchemy)')
@click.option('--toml-files', multiple=True, type=click.Path(exists=True), help='Additional TOML files for cross-file template references (can be specified multiple times)')
def convert_cmd(input_source, input_type, format, framework, output, output_dir, app_label, table_prefix, split_models, inheritance_mode, base_model_import, toml_files):
    """Convert ER diagram file to code."""
    assert isinstance(input_source, str), "input_source must be a string"
    assert len(input_source) > 0, "input_source cannot be empty"

    zip_tmp_dir = None
    zip_extra_files: list[str] = []

    if input_source.endswith('.zip'):
        if input_type in ('mermaid', 'plantuml', 'db'):
            logger.error(f"ZIP input is only supported with --input-type toml (got: {input_type})")
            sys.exit(1)
        input_source, zip_extra_files, zip_tmp_dir = _extract_zip_toml_files(input_source)
        input_type = 'toml'
        logger.info(f"Using ZIP-extracted TOML as input: {os.path.basename(input_source)}")

    if zip_extra_files:
        toml_files = list(toml_files) + zip_extra_files

    if input_type is None:
        if input_source.endswith('.toml'):
            input_type = 'toml'
        elif input_source.endswith('.mmd'):
            input_type = 'mermaid'
        elif input_source.endswith('.puml') or input_source.endswith('.plantuml'):
            input_type = 'plantuml'
        else:
            input_type = 'mermaid'

    assert input_type in ['mermaid', 'plantuml', 'db', 'toml'], "Invalid input_type"
    assert format in ['django', 'sqlalchemy', 'mermaid', 'plantuml'], "Invalid format"
    
    # Handle --framework as alias for --format
    if framework:
        format = framework
    
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
            parser = TomlERParser(inheritance_mode=inheritance_mode)
        else:
            raise ValueError(f"Unknown input type: {input_type}")
        
        model = parser.parse(content)
    
    # Process templates if TOML input with templates and output directory specified
    # The MixinOrchestrator will generate mixin files and update export_paths
    # Check if we have additional TOML files or if the main file has templates
    if input_type == 'toml' and output_dir and inheritance_mode == 'reference' and (model.templates or toml_files):
        from x007007007.er.mixin_orchestrator import MixinOrchestrator
        from x007007007.er.renderers.python.utils import to_snake_case
        
        # Build list of TOML files (main input + additional files)
        all_toml_files = [input_source]
        if toml_files:
            all_toml_files.extend(toml_files)
        
        # Use MixinOrchestrator to process templates
        orchestrator = MixinOrchestrator()
        try:
            templates = orchestrator.process_templates(
                toml_files=all_toml_files,
                output_dir=output_dir,
                inheritance_mode=inheritance_mode
            )
            # Convert TemplateInfo objects back to dictionary format for renderer compatibility
            # Update export_path to include the module name for correct imports
            model.templates = {
                name: {
                    'columns': [],  # Empty columns so renderer skips mixin generation
                    'export_path': f"{info.export_path}.{to_snake_case(name)}",  # Add module name
                    'package': info.package
                }
                for name, info in templates.items()
            }
            logger.info(f"Processed {len(templates)} template(s) from {len(all_toml_files)} TOML file(s)")
        except Exception as e:
            logger.error(f"Failed to process templates: {e}")
            sys.exit(1)
    
    # Render or convert output
    if format == 'django':
        if split_models or output_dir:
            # Multi-file mode
            if not output_dir:
                logger.error("--output-dir is required when using --split-models")
                sys.exit(1)
            renderer = DjangoPackageRenderer(app_label=app_label, table_prefix=table_prefix, inheritance_mode=inheritance_mode)
            renderer.write_to_directory(model, output_dir)
            logger.info(f"Successfully generated Django models package in {output_dir}")
            return
        else:
            # Single file mode
            renderer = DjangoRenderer(app_label=app_label, table_prefix=table_prefix, inheritance_mode=inheritance_mode)
            result = renderer.render(model)
    elif format == 'sqlalchemy':
        if output_dir:
            # Multi-file mode for SQLAlchemy
            renderer = SQLAlchemyRenderer(
                table_prefix=table_prefix, 
                base_model_import=base_model_import,
                inheritance_mode=inheritance_mode
            )
            files = renderer.render_multi_file(model)
            
            # Write files to output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # IMPORTANT: third-party files should be written to global src/third/ directory
            # while entity files should be written to the module-specific output_dir
            for filename, content in files.items():
                if filename.startswith('third/'):
                    # Third-party files go to global src/third/ directory
                    # Find the src/ root by going up from output_path
                    current = output_path
                    src_root = None
                    while current.parent != current:  # Stop at filesystem root
                        if current.name == 'src':
                            src_root = current
                            break
                        current = current.parent
                    
                    if src_root is None:
                        # Fallback: assume output_path is relative to current directory
                        # and try to find src/ in the path
                        if 'src' in output_path.parts:
                            src_index = output_path.parts.index('src')
                            src_root = Path(*output_path.parts[:src_index+1])
                        else:
                            # Last resort: use output_path's parent as src root
                            src_root = output_path.parent
                    
                    file_path = src_root / filename
                else:
                    # Entity and mixin files go to module-specific output_path
                    file_path = output_path / filename
                
                # Create parent directories if needed (for mixin files)
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Generated: {file_path}")
            
            logger.info(f"Successfully generated SQLAlchemy models in {output_dir}")
            return
        else:
            # Single file mode
            renderer = SQLAlchemyRenderer(
                table_prefix=table_prefix,
                base_model_import=base_model_import,
                inheritance_mode=inheritance_mode
            )
            result = renderer.render(model)
    elif format == 'mermaid':
        converter = MermaidConverter()
        result = converter.convert(model)
    elif format == 'plantuml':
        converter = PlantUMLConverter()
        result = converter.convert(model)
    else:
        raise ValueError(f"Unknown format: {format}")
    
    # Handle output file (using UTF-8 encoding)
    if output:
        # If output file is specified, open with UTF-8 encoding
        with open(output, 'w', encoding='utf-8') as output_file:
            output_file.write(result)
    else:
        # Use standard output
        sys.stdout.write(result)
    
    logger.info(f"Successfully converted {input_source} to {format}")
