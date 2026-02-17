"""
Unit tests for Column and Entity model basic functionality.

These tests verify specific examples and edge cases for the Column and Entity models.

Feature: field-db-column-and-path-separation
Requirements: 1.1, 1.2
"""
import pytest
from x007007007.er.models import Column, Entity


class TestColumnModelBasicFunctionality:
    """Unit tests for Column model basic functionality."""
    
    def test_db_column_is_required_field(self):
        """Test that db_column is a required field."""
        # db_column must be provided when creating a Column
        with pytest.raises(TypeError, match="missing 1 required positional argument: 'db_column'"):
            Column(name="username", db_column="username", type="CharField")
    
    def test_database_column_name_returns_db_column(self):
        """Test that database_column_name property returns db_column value."""
        column = Column(
            name="username",
            type="CharField",
            db_column="user_name"
        )
        
        assert column.database_column_name == "user_name"
        assert column.database_column_name == column.db_column
    
    def test_database_column_name_when_same_as_name(self):
        """Test database_column_name when db_column equals name."""
        column = Column(
            name="email",
            type="EmailField",
            db_column="email"
        )
        
        assert column.database_column_name == "email"
        assert column.database_column_name == column.db_column
    
    def test_column_with_all_fields(self):
        """Test Column creation with all fields specified."""
        column = Column(
            name="age",
            type="IntegerField",
            db_column="user_age",
            is_pk=False,
            is_fk=False,
            nullable=False,
            comment="User's age",
            default="0",
            max_length=None,
            precision=None,
            scale=None,
            unique=True,
            indexed=True
        )
        
        assert column.name == "age"
        assert column.type == "IntegerField"
        assert column.db_column == "user_age"
        assert column.database_column_name == "user_age"
        assert column.nullable is False
        assert column.unique is True
        assert column.indexed is True


class TestEntityModelBasicFunctionality:
    """Unit tests for Entity model basic functionality."""
    
    def test_table_name_is_required_field(self):
        """Test that table_name is a required field."""
        # table_name must be provided when creating an Entity
        with pytest.raises(TypeError, match="missing 1 required positional argument: 'table_name'"):
            Entity(name="User")
    
    def test_entity_with_table_name(self):
        """Test Entity creation with table_name."""
        entity = Entity(
            name="User",
            table_name="auth_user"
        )
        
        assert entity.name == "User"
        assert entity.table_name == "auth_user"
    
    def test_entity_with_columns(self):
        """Test Entity with columns."""
        columns = [
            Column(name="id", type="IntegerField", db_column="id", is_pk=True),
            Column(name="username", type="CharField", db_column="user_name"),
            Column(name="email", type="EmailField", db_column="email")
        ]
        
        entity = Entity(
            name="User",
            table_name="auth_user",
            columns=columns
        )
        
        assert entity.name == "User"
        assert entity.table_name == "auth_user"
        assert len(entity.columns) == 3
        assert entity.columns[0].database_column_name == "id"
        assert entity.columns[1].database_column_name == "user_name"
        assert entity.columns[2].database_column_name == "email"
