"""
Test for Task 2.3: Verify both templates handle max_length fields correctly

This test verifies that both sqlalchemy_model.j2 and sqlalchemy_single_model.j2
templates correctly handle fields with max_length.

Validates Requirements: 3.1, 3.2, 6.4
"""

import pytest
from x007007007.er.models import ERModel, Entity, Column
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer


def test_both_templates_max_length_with_attributes():
    """Test that both templates handle max_length fields with attributes correctly"""
    model = ERModel()
    entity = Entity(name="User", table_name="users")
    
    # Create fields with max_length and various attributes
    col1 = Column(
        name="username",
        type="CharField",
        db_column="username",
        max_length=100,
        nullable=False,
        unique=True
    )
    col2 = Column(
        name="email",
        type="CharField",
        db_column="email",
        max_length=255,
        nullable=False,
        indexed=True
    )
    col3 = Column(
        name="bio",
        type="CharField",
        db_column="bio",
        max_length=500,
        nullable=True  # Should not appear in output
    )
    
    entity.columns.append(col1)
    entity.columns.append(col2)
    entity.columns.append(col3)
    model.entities["User"] = entity
    
    # Test with default renderer (uses sqlalchemy_model.j2)
    renderer = SQLAlchemyRenderer()
    result = renderer.render(model)
    
    # Verify all fields are correctly rendered
    assert "username = Column(String(100), nullable=False, unique=True)" in result
    assert "email = Column(String(255), nullable=False, index=True)" in result
    assert "bio = Column(String(500))" in result
    assert "nullable=True" not in result  # Should not include default values


def test_single_model_template_max_length():
    """Test that single model template handles max_length correctly"""
    model = ERModel()
    entity = Entity(name="Product", table_name="products")
    
    # Create a field with max_length and multiple attributes
    col = Column(
        name="sku",
        type="CharField",
        db_column="sku",
        max_length=50,
        nullable=False,
        unique=True,
        indexed=True,
        comment="Product SKU"
    )
    entity.columns.append(col)
    model.entities["Product"] = entity
    
    # Render using multi-file mode (which uses single model template)
    renderer = SQLAlchemyRenderer()
    files = renderer.render_multi_file(model)
    result = files['product.py']
    
    # Verify the field is correctly rendered with all attributes
    assert "sku = Column(String(50), nullable=False, unique=True, index=True, comment=\"Product SKU\")" in result


def test_template_consistency():
    """Test that both templates produce consistent output for the same model"""
    model = ERModel()
    entity = Entity(name="Article", table_name="articles")
    
    # Create a field with max_length and attributes
    col = Column(
        name="title",
        type="CharField",
        db_column="title",
        max_length=200,
        nullable=False,
        indexed=True
    )
    entity.columns.append(col)
    model.entities["Article"] = entity
    
    # Render with both templates
    renderer = SQLAlchemyRenderer()
    full_result = renderer.render(model)
    files = renderer.render_multi_file(model)
    single_result = files['article.py']
    
    # Both should contain the same field definition
    field_def = "title = Column(String(200), nullable=False, index=True)"
    assert field_def in full_result
    assert field_def in single_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
