"""
Test for Task 2.3: 确保带 max_length 字段的参数完整性

This test verifies that fields with max_length (like String(255)) correctly include
all field attributes after the type parameter.

Validates Requirements: 3.1, 3.2, 6.4
"""

import pytest
from x007007007.er.models import ERModel, Entity, Column
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer


def test_max_length_field_with_nullable():
    """Test that a field with max_length includes nullable parameter"""
    model = ERModel()
    entity = Entity(name="User", table_name="users")
    
    # Create a field with max_length and nullable=False
    col = Column(
        name="username",
        type="CharField",
        db_column="username",
        max_length=255,
        nullable=False
    )
    entity.columns.append(col)
    model.entities["User"] = entity
    
    renderer = SQLAlchemyRenderer()
    result = renderer.render(model)
    
    # Verify the generated code includes both String(255) and nullable=False
    assert "username = Column(String(255), nullable=False)" in result


def test_max_length_field_with_unique():
    """Test that a field with max_length includes unique parameter"""
    model = ERModel()
    entity = Entity(name="User", table_name="users")
    
    # Create a field with max_length and unique=True
    col = Column(
        name="email",
        type="CharField",
        db_column="email",
        max_length=255,
        unique=True
    )
    entity.columns.append(col)
    model.entities["User"] = entity
    
    renderer = SQLAlchemyRenderer()
    result = renderer.render(model)
    
    # Verify the generated code includes both String(255) and unique=True
    assert "email = Column(String(255), unique=True)" in result


def test_max_length_field_with_index():
    """Test that a field with max_length includes index parameter"""
    model = ERModel()
    entity = Entity(name="User", table_name="users")
    
    # Create a field with max_length and indexed=True
    col = Column(
        name="username",
        type="CharField",
        db_column="username",
        max_length=100,
        indexed=True
    )
    entity.columns.append(col)
    model.entities["User"] = entity
    
    renderer = SQLAlchemyRenderer()
    result = renderer.render(model)
    
    # Verify the generated code includes both String(100) and index=True
    assert "username = Column(String(100), index=True)" in result


def test_max_length_field_with_multiple_attributes():
    """Test that a field with max_length includes all attributes"""
    model = ERModel()
    entity = Entity(name="User", table_name="users")
    
    # Create a field with max_length and multiple attributes
    col = Column(
        name="email",
        type="CharField",
        db_column="email",
        max_length=255,
        nullable=False,
        unique=True,
        indexed=True,
        comment="User email address"
    )
    entity.columns.append(col)
    model.entities["User"] = entity
    
    renderer = SQLAlchemyRenderer()
    result = renderer.render(model)
    
    # Verify the generated code includes String(255) and all attributes
    assert "email = Column(String(255), nullable=False, unique=True, index=True, comment=\"User email address\")" in result


def test_max_length_field_with_default():
    """Test that a field with max_length includes default parameter"""
    model = ERModel()
    entity = Entity(name="User", table_name="users")
    
    # Create a field with max_length and default value
    col = Column(
        name="status",
        type="CharField",
        db_column="status",
        max_length=20,
        default="'active'",
        nullable=False
    )
    entity.columns.append(col)
    model.entities["User"] = entity
    
    renderer = SQLAlchemyRenderer()
    result = renderer.render(model)
    
    # Verify the generated code includes String(20), nullable, and default
    assert "status = Column(String(20), nullable=False, default=\"'active'\")" in result


def test_max_length_field_without_extra_attributes():
    """Test that a field with only max_length doesn't include unnecessary parameters"""
    model = ERModel()
    entity = Entity(name="User", table_name="users")
    
    # Create a field with only max_length (nullable=True by default)
    col = Column(
        name="bio",
        type="CharField",
        db_column="bio",
        max_length=500,
        nullable=True  # Default value
    )
    entity.columns.append(col)
    model.entities["User"] = entity
    
    renderer = SQLAlchemyRenderer()
    result = renderer.render(model)
    
    # Verify the generated code only includes String(500) without nullable parameter
    assert "bio = Column(String(500))" in result
    assert "nullable=True" not in result  # Should not include default values


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
