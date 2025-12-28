import pytest
from x007007007.er.parsers import MermaidParser
from x007007007.er.plantuml_parser import PlantUMLParser
from x007007007.er.db_parser import DBParser
from x007007007.er.renderers import DjangoRenderer, SQLAlchemyRenderer
from x007007007.er.models import ERModel

MERMAID_SAMPLE = """
erDiagram
    USER {
        int id PK
        string name "User Name"
        string email
    }
    POST {
        int id PK
        string title
        int user_id FK
    }
    USER ||--o{ POST : writes
"""

PLANTUML_SAMPLE = """
@startuml
entity USER as "User Table" {
    * id : int
    name : string
    email : string
}
entity POST {
    * id : int
    title : string
    user_id : int
}
USER -- POST : writes
@enduml
"""

def test_mermaid_parser():
    parser = MermaidParser()
    model = parser.parse(MERMAID_SAMPLE)
    
    assert "USER" in model.entities
    assert "POST" in model.entities
    assert len(model.entities["USER"].columns) == 3
    assert model.entities["USER"].columns[0].is_pk is True
    assert model.entities["USER"].columns[1].comment == "User Name"
    assert len(model.relationships) == 1
    assert model.relationships[0].left_entity == "USER"
    assert model.relationships[0].right_entity == "POST"

def test_plantuml_parser():
    parser = PlantUMLParser()
    model = parser.parse(PLANTUML_SAMPLE)
    
    assert "USER" in model.entities
    assert model.entities["USER"].comment == "User Table"
    assert model.entities["USER"].columns[0].is_pk is True
    assert len(model.relationships) == 1

def test_db_parser():
    # Using sqlite memory for test
    parser = DBParser()
    model = parser.parse("sqlite:///:memory:")
    assert len(model.entities) == 0 # Memory DB is empty
    
def test_django_renderer():
    parser = MermaidParser()
    model = parser.parse(MERMAID_SAMPLE)
    renderer = DjangoRenderer()
    result = renderer.render(model)
    
    assert "class USER(models.Model):" in result
    assert "id = models.IntegerField(primary_key=True, null=True)" in result
    assert 'name = models.CharField(max_length=255, primary_key=False, null=True, help_text="User Name")' in result

import os

def test_complex_assets():
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    mermaid_file = os.path.join(assets_dir, "complex.mermaid")
    puml_file = os.path.join(assets_dir, "complex.puml")
    
    # Test Mermaid
    with open(mermaid_file, "r", encoding="utf-8") as f:
        mermaid_content = f.read()
    
    m_parser = MermaidParser()
    m_model = m_parser.parse(mermaid_content)
    
    assert "USER" in m_model.entities
    assert "POST_TAGS" in m_model.entities
    
    # Check relationships
    rels = { (r.left_entity, r.right_entity): r.relation_type for r in m_model.relationships }
    assert rels.get(("USER", "PROFILE")) == "one-to-one"
    assert rels.get(("USER", "POST")) == "one-to-many"
    assert rels.get(("POST", "TAG")) == "many-to-many"

    # Test PlantUML
    with open(puml_file, "r", encoding="utf-8") as f:
        puml_content = f.read()
        
    p_parser = PlantUMLParser()
    p_model = p_parser.parse(puml_content)
    
    assert "User" in p_model.entities
    assert "Post" in p_model.entities
    
    # Check relationships
    p_rels = { (r.left_entity, r.right_entity): r.relation_type for r in p_model.relationships }
    assert p_rels.get(("User", "Profile")) == "one-to-one"
    assert p_rels.get(("User", "Post")) == "one-to-many"
    assert p_rels.get(("Post", "Tag")) == "many-to-many"
