"""
Tests for Mermaid and PlantUML converters.
"""
import pytest
import os
from x007007007.er.parser.antlr.mermaid_antlr_parser import MermaidAntlrParser
from x007007007.er.parser.antlr.plantuml_antlr_parser import PlantUMLAntlrParser
from x007007007.er.converters import MermaidConverter, PlantUMLConverter


def get_asset_path(case_name: str, filename: str) -> str:
    """Get path to asset file."""
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    return os.path.join(assets_dir, case_name, filename)


def test_mermaid_to_plantuml():
    """Test converting Mermaid to PlantUML."""
    # Parse Mermaid input
    mermaid_file = get_asset_path("convert_mermaid_to_plantuml", "input.mermaid")
    with open(mermaid_file, "r", encoding="utf-8") as f:
        mermaid_content = f.read()
    
    parser = MermaidAntlrParser()
    model = parser.parse(mermaid_content)
    
    # Convert to PlantUML
    converter = PlantUMLConverter()
    plantuml_output = converter.convert(model)
    
    # Compare with expected output
    expected_file = get_asset_path("convert_mermaid_to_plantuml", "output.puml")
    with open(expected_file, "r", encoding="utf-8") as f:
        expected_output = f.read()
    
    assert plantuml_output == expected_output, "Mermaid to PlantUML conversion does not match expected file"


def test_plantuml_to_mermaid():
    """Test converting PlantUML to Mermaid."""
    # Parse PlantUML input
    plantuml_file = get_asset_path("convert_plantuml_to_mermaid", "input.puml")
    with open(plantuml_file, "r", encoding="utf-8") as f:
        plantuml_content = f.read()
    
    parser = PlantUMLAntlrParser()
    model = parser.parse(plantuml_content)
    
    # Convert to Mermaid
    converter = MermaidConverter()
    mermaid_output = converter.convert(model)
    
    # Compare with expected output
    expected_file = get_asset_path("convert_plantuml_to_mermaid", "output.mermaid")
    with open(expected_file, "r", encoding="utf-8") as f:
        expected_output = f.read()
    
    assert mermaid_output == expected_output, "PlantUML to Mermaid conversion does not match expected file"


def test_round_trip_mermaid():
    """Test round-trip conversion: Mermaid -> PlantUML -> Mermaid."""
    # Parse original Mermaid
    mermaid_file = get_asset_path("round_trip_mermaid", "input.mermaid")
    with open(mermaid_file, "r", encoding="utf-8") as f:
        original_mermaid = f.read()
    
    parser = MermaidAntlrParser()
    model1 = parser.parse(original_mermaid)
    
    # Convert to PlantUML and back
    plantuml_converter = PlantUMLConverter()
    plantuml_output = plantuml_converter.convert(model1)
    
    plantuml_parser = PlantUMLAntlrParser()
    model2 = plantuml_parser.parse(plantuml_output)
    
    mermaid_converter = MermaidConverter()
    converted_mermaid = mermaid_converter.convert(model2)
    
    # Compare with expected output
    expected_file = get_asset_path("round_trip_mermaid", "output.mermaid")
    with open(expected_file, "r", encoding="utf-8") as f:
        expected_output = f.read()
    
    assert converted_mermaid == expected_output, "Round-trip Mermaid conversion does not match expected file"


def test_round_trip_plantuml():
    """Test round-trip conversion: PlantUML -> Mermaid -> PlantUML."""
    # Parse original PlantUML
    plantuml_file = get_asset_path("round_trip_plantuml", "input.puml")
    with open(plantuml_file, "r", encoding="utf-8") as f:
        original_plantuml = f.read()
    
    parser = PlantUMLAntlrParser()
    model1 = parser.parse(original_plantuml)
    
    # Convert to Mermaid and back
    mermaid_converter = MermaidConverter()
    mermaid_output = mermaid_converter.convert(model1)
    
    mermaid_parser = MermaidAntlrParser()
    model2 = mermaid_parser.parse(mermaid_output)
    
    plantuml_converter = PlantUMLConverter()
    converted_plantuml = plantuml_converter.convert(model2)
    
    # Compare with expected output
    expected_file = get_asset_path("round_trip_plantuml", "output.puml")
    with open(expected_file, "r", encoding="utf-8") as f:
        expected_output = f.read()
    
    assert converted_plantuml == expected_output, "Round-trip PlantUML conversion does not match expected file"

