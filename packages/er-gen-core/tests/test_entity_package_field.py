"""
Unit tests for Entity.package field (Task 3.1)

Tests verify that the package field:
- Can be set and retrieved correctly
- Defaults to None (backward compatible)
- Works with dataclass serialization
"""

import pytest
from dataclasses import asdict
from x007007007.er.models import Entity, Column


def test_entity_package_field_default_none():
    """Test that package field defaults to None for backward compatibility."""
    entity = Entity(name="User", table_name="user")
    assert entity.package is None


def test_entity_package_field_can_be_set():
    """Test that package field can be set to a module path."""
    entity = Entity(
        name="User",
            table_name="user",
        package="kinkotech.common.domains.account.models"
    )
    assert entity.package == "kinkotech.common.domains.account.models"


def test_entity_package_field_with_columns():
    """Test that package field works alongside other Entity fields."""
    entity = Entity(
        name="User",
            table_name="user",
        package="myapp.models",
        columns=[
            Column(name="id", db_column="id", type="int", is_pk=True),
            Column(name="username", db_column="username", type="str")
        ],
        comment="User model"
    )
    
    assert entity.name == "User"
    assert entity.package == "myapp.models"
    assert len(entity.columns) == 2
    assert entity.comment == "User model"


def test_entity_package_field_serialization():
    """Test that package field is included in dataclass serialization."""
    entity = Entity(
        name="Profile",
            table_name="profile",
        package="src.aaa.bbb.ccc.models",
        extends=["BaseModel"],
        export_path="/path/to/models.toml"
    )
    
    entity_dict = asdict(entity)
    
    assert "package" in entity_dict
    assert entity_dict["package"] == "src.aaa.bbb.ccc.models"
    assert entity_dict["extends"] == ["BaseModel"]
    assert entity_dict["export_path"] == "/path/to/models.toml"


def test_entity_package_field_none_serialization():
    """Test that package field with None value is included in serialization."""
    entity = Entity(name="Product", table_name="product")
    entity_dict = asdict(entity)
    
    assert "package" in entity_dict
    assert entity_dict["package"] is None


def test_entity_with_all_fields():
    """Test Entity with all fields including package."""
    entity = Entity(
        name="Order",
            table_name="order",
        columns=[Column(name="id", db_column="id", type="int", is_pk=True)],
        comment="Order entity",
        extends=["TimestampedModel", "SoftDeleteModel"],
        export_path="src/orders/models.toml",
        package="myproject.orders.models"
    )
    
    assert entity.name == "Order"
    assert len(entity.columns) == 1
    assert entity.comment == "Order entity"
    assert entity.extends == ["TimestampedModel", "SoftDeleteModel"]
    assert entity.export_path == "src/orders/models.toml"
    assert entity.package == "myproject.orders.models"
