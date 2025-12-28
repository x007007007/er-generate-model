"""
Unit tests for ANTLR-based Mermaid ER parser.
These tests drive the development of the MermaidER.g4 grammar file.
"""
import pytest
import os
from x007007007.er.parser.antlr.mermaid_antlr_parser import MermaidAntlrParser
from x007007007.er.models import ERModel, Entity, Column, Relationship


def get_asset_path(case_name: str, filename: str) -> str:
    """Get path to asset file."""
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    return os.path.join(assets_dir, case_name, filename)


def test_antlr_parser_simple():
    """Test parsing a simple ER diagram."""
    parser = MermaidAntlrParser()
    with open(get_asset_path("simple", "input.mermaid"), "r", encoding="utf-8") as f:
        content = f.read()
    model = parser.parse(content)
    
    assert isinstance(model, ERModel)
    assert "USER" in model.entities
    assert len(model.entities["USER"].columns) == 2
    assert model.entities["USER"].columns[0].is_pk is True
    assert model.entities["USER"].columns[0].name == "id"
    assert model.entities["USER"].columns[1].name == "name"


def test_antlr_parser_with_relationship():
    """Test parsing ER diagram with relationships."""
    parser = MermaidAntlrParser()
    with open(get_asset_path("with_relationship", "input.mermaid"), "r", encoding="utf-8") as f:
        content = f.read()
    model = parser.parse(content)
    
    assert "USER" in model.entities
    assert "POST" in model.entities
    assert len(model.relationships) == 1
    assert model.relationships[0].left_entity == "USER"
    assert model.relationships[0].right_entity == "POST"
    assert model.relationships[0].relation_type == "one-to-many"


def test_antlr_parser_complex():
    """Test parsing complex ER diagram."""
    parser = MermaidAntlrParser()
    with open(get_asset_path("complex", "input.mermaid"), "r", encoding="utf-8") as f:
        content = f.read()
    model = parser.parse(content)
    
    assert "USER" in model.entities
    assert "PROFILE" in model.entities
    assert len(model.relationships) >= 1
    
    # Check one-to-one relationship
    rels = {r.left_entity + "-" + r.right_entity: r for r in model.relationships}
    assert "USER-PROFILE" in rels
    assert rels["USER-PROFILE"].relation_type == "one-to-one"


def test_antlr_parser_column_with_comment():
    """Test parsing column with comment."""
    parser = MermaidAntlrParser()
    with open(get_asset_path("column_with_comment", "input.mermaid"), "r", encoding="utf-8") as f:
        content = f.read()
    model = parser.parse(content)
    
    assert "USER" in model.entities
    name_col = model.entities["USER"].columns[0]
    assert name_col.name == "name"
    assert name_col.comment == "User Name"


def test_antlr_parser_foreign_key():
    """Test parsing foreign key columns."""
    parser = MermaidAntlrParser()
    with open(get_asset_path("with_relationship", "input.mermaid"), "r", encoding="utf-8") as f:
        content = f.read()
    model = parser.parse(content)
    
    post_entity = model.entities["POST"]
    user_id_col = next((c for c in post_entity.columns if c.name == "user_id"), None)
    assert user_id_col is not None
    assert user_id_col.is_fk is True


def test_antlr_parser_requires_antlr():
    """Test that parser works when ANTLR is available."""
    parser = MermaidAntlrParser()
    with open(get_asset_path("simple", "input.mermaid"), "r", encoding="utf-8") as f:
        content = f.read()
    # Should parse successfully when ANTLR is available
    model = parser.parse(content)
    assert isinstance(model, ERModel)


def test_antlr_parser_empty_content():
    """Test parsing empty content."""
    parser = MermaidAntlrParser()
    # Should handle gracefully
    content = "erDiagram"
    model = parser.parse(content)
    assert isinstance(model, ERModel)
    assert len(model.entities) == 0


def test_antlr_parser_relationship_types():
    """Test different relationship types."""
    parser = MermaidAntlrParser()
    with open(get_asset_path("relationship_types", "input.mermaid"), "r", encoding="utf-8") as f:
        content = f.read()
    model = parser.parse(content)
    
    rels = {(r.left_entity, r.right_entity): r.relation_type for r in model.relationships}
    assert rels.get(("A", "B")) == "one-to-one"
    assert rels.get(("A", "C")) == "one-to-many"
    assert rels.get(("A", "D")) == "many-to-many"
