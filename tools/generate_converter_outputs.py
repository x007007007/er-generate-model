"""
Generate expected output files for converter test cases.
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from x007007007.er.parser.antlr.mermaid_antlr_parser import MermaidAntlrParser
from x007007007.er.parser.antlr.plantuml_antlr_parser import PlantUMLAntlrParser
from x007007007.er.converters import MermaidConverter, PlantUMLConverter

def get_asset_path(case_name: str, filename: str) -> Path:
    """Get path to asset file."""
    assets_dir = Path(__file__).parent.parent / "tests" / "assets"
    return assets_dir / case_name / filename

def generate_outputs():
    """Generate expected output files for converter test cases."""
    mermaid_parser = MermaidAntlrParser()
    plantuml_parser = PlantUMLAntlrParser()
    mermaid_converter = MermaidConverter()
    plantuml_converter = PlantUMLConverter()
    
    # Test case 1: Mermaid to PlantUML
    print("Generating convert_mermaid_to_plantuml/output.puml...")
    input_file = get_asset_path("convert_mermaid_to_plantuml", "input.mermaid")
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()
    model = mermaid_parser.parse(content)
    output = plantuml_converter.convert(model)
    output_file = get_asset_path("convert_mermaid_to_plantuml", "output.puml")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"Generated: {output_file}")
    
    # Test case 2: PlantUML to Mermaid
    print("Generating convert_plantuml_to_mermaid/output.mermaid...")
    input_file = get_asset_path("convert_plantuml_to_mermaid", "input.puml")
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()
    model = plantuml_parser.parse(content)
    output = mermaid_converter.convert(model)
    output_file = get_asset_path("convert_plantuml_to_mermaid", "output.mermaid")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"Generated: {output_file}")
    
    # Test case 3: Round-trip Mermaid
    print("Generating round_trip_mermaid/output.mermaid...")
    input_file = get_asset_path("round_trip_mermaid", "input.mermaid")
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()
    model1 = mermaid_parser.parse(content)
    plantuml_output = plantuml_converter.convert(model1)
    model2 = plantuml_parser.parse(plantuml_output)
    mermaid_output = mermaid_converter.convert(model2)
    output_file = get_asset_path("round_trip_mermaid", "output.mermaid")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(mermaid_output)
    print(f"Generated: {output_file}")
    
    # Test case 4: Round-trip PlantUML
    print("Generating round_trip_plantuml/output.puml...")
    input_file = get_asset_path("round_trip_plantuml", "input.puml")
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()
    model1 = plantuml_parser.parse(content)
    mermaid_output = mermaid_converter.convert(model1)
    model2 = mermaid_parser.parse(mermaid_output)
    plantuml_output = plantuml_converter.convert(model2)
    output_file = get_asset_path("round_trip_plantuml", "output.puml")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(plantuml_output)
    print(f"Generated: {output_file}")

if __name__ == "__main__":
    generate_outputs()
    print("\nAll converter output files generated successfully!")

