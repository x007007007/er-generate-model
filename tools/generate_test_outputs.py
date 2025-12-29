"""
Generate expected output files for all test cases.
This script generates Django and SQLAlchemy output files for test cases that produce renderer output.
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from x007007007.er.parser.antlr.mermaid_antlr_parser import MermaidAntlrParser
from x007007007.er.parser.antlr.plantuml_antlr_parser import PlantUMLAntlrParser
from x007007007.er.renderers import DjangoRenderer, SQLAlchemyRenderer
from x007007007.er.models import ERModel, Entity

def get_asset_path(case_name: str, filename: str) -> str:
    """Get path to asset file."""
    assets_dir = Path(__file__).parent.parent / "tests" / "assets"
    return assets_dir / case_name / filename

def generate_outputs():
    """Generate expected output files for all test cases."""
    parser = MermaidAntlrParser()
    plantuml_parser = PlantUMLAntlrParser()
    
    # Test cases that need output files
    test_cases = [
        # CLI test cases
        {
            "name": "cli_django",
            "input": "input.mermaid",
            "app_label": "cli_django",
            "table_prefix": "cli_django",
            "parser": parser
        },
        {
            "name": "cli_sqlalchemy",
            "input": "input.mermaid",
            "app_label": None,
            "table_prefix": "cli_sqlalchemy",
            "parser": parser
        },
        # Renderer test cases
        {
            "name": "mermaid_sample",
            "input": "input.mermaid",
            "app_label": None,
            "table_prefix": "",
            "parser": parser
        },
        # Empty model test case
        {
            "name": "renderer_empty",
            "input": None,
            "app_label": None,
            "table_prefix": "",
            "parser": None,
            "model": ERModel()
        },
        # Entity with no columns test case
        {
            "name": "renderer_no_columns",
            "input": None,
            "app_label": None,
            "table_prefix": "",
            "parser": None,
            "model": ERModel()
        },
        # Complex test case
        {
            "name": "complex",
            "input": "input.mermaid",
            "app_label": "complex",
            "table_prefix": "complex",
            "parser": parser
        }
    ]
    
    # Create renderer_no_columns model
    empty_entity = Entity(name="EMPTY")
    test_cases[4]["model"].add_entity(empty_entity)
    
    for case in test_cases:
        case_dir = get_asset_path(case["name"], "").parent / case["name"]
        case_dir.mkdir(parents=True, exist_ok=True)
        
        # Get model
        if case.get("model"):
            model = case["model"]
        else:
            input_file = case_dir / case["input"]
            if not input_file.exists():
                print(f"Warning: Input file not found: {input_file}")
                continue
            with open(input_file, "r", encoding="utf-8") as f:
                content = f.read()
            model = case["parser"].parse(content)
        
        # Generate Django output
        # For CLI test cases, use the actual CLI behavior (auto-detect from filename)
        if case["name"].startswith("cli_"):
            # CLI auto-detects app_label and table_prefix from filename stem
            # For input.mermaid, stem is "input"
            input_file = case_dir / case["input"]
            if input_file.exists():
                filename_stem = input_file.stem
                app_label = filename_stem.lower().replace('-', '_').replace(' ', '_')
                table_prefix = filename_stem.lower().replace('-', '_').replace(' ', '_')
            else:
                app_label = "app"
                table_prefix = ""
        elif case.get("app_label") is not None:
            app_label = case["app_label"]
            table_prefix = case.get("table_prefix") or ""
        else:
            # Default behavior for renderer tests
            app_label = "app"
            table_prefix = ""
        
        django_renderer = DjangoRenderer(app_label=app_label, table_prefix=table_prefix)
        django_output = django_renderer.render(model)
        
        django_file = case_dir / "django.py"
        with open(django_file, "w", encoding="utf-8") as f:
            f.write(django_output)
        print(f"Generated: {django_file}")
        
        # Generate SQLAlchemy output
        sqlalchemy_renderer = SQLAlchemyRenderer(table_prefix=table_prefix)
        sqlalchemy_output = sqlalchemy_renderer.render(model)
        
        sqlalchemy_file = case_dir / "sqlalchemy.py"
        with open(sqlalchemy_file, "w", encoding="utf-8") as f:
            f.write(sqlalchemy_output)
        print(f"Generated: {sqlalchemy_file}")

if __name__ == "__main__":
    generate_outputs()
    print("\nAll output files generated successfully!")

