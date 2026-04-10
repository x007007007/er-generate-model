"""
Tests to verify TOMLWriter produces correct TOML format matching examples
"""

import os
import tempfile
import shutil
import toml
import pytest

from x007007007.er.toml_writer import TOMLWriter
from x007007007.er.namespace_models import (
    EntityDefinition,
    TemplateDefinition,
    ColumnDefinition,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


def test_entity_format_matches_example(temp_dir):
    """Test that entity format matches the example format"""
    writer = TOMLWriter(base_dir=temp_dir)
    
    # Create entity similar to examples/toml-to-output/django/01-simple-model/input.toml
    entity = EntityDefinition(
        name="USER",
        namespace="myapp.models",
        table_name="user",
        columns=[
            ColumnDefinition(
                name="id",
                type="int",
                db_column="id",
                is_pk=True,
                comment="Primary key"
            ),
            ColumnDefinition(
                name="username",
                type="string",
                db_column="username",
                unique=True,
                comment="Unique username"
            ),
            ColumnDefinition(
                name="email",
                type="string",
                db_column="email",
                comment="User email address"
            ),
            ColumnDefinition(
                name="created_at",
                type="datetime",
                db_column="created_at",
                comment="Account creation timestamp"
            ),
        ],
        comment="User entity with basic fields"
    )
    
    file_path = writer.write_entity("myapp.models", entity)
    
    # Read and verify format
    with open(file_path, 'r') as f:
        data = toml.load(f)
    
    # Verify structure
    assert 'entities' in data
    assert 'USER' in data['entities']
    
    user_entity = data['entities']['USER']
    assert user_entity['comment'] == "User entity with basic fields"
    assert 'columns' in user_entity
    assert len(user_entity['columns']) == 4
    
    # Verify column format
    id_col = user_entity['columns'][0]
    assert id_col['name'] == 'id'
    assert id_col['type'] == 'int'
    assert id_col['primary_key'] is True
    assert id_col['comment'] == "Primary key"
    
    username_col = user_entity['columns'][1]
    assert username_col['name'] == 'username'
    assert username_col['type'] == 'string'
    assert username_col['unique'] is True
    assert username_col['comment'] == "Unique username"


def test_template_format_matches_example(temp_dir):
    """Test that template format matches the example format"""
    writer = TOMLWriter(base_dir=temp_dir)
    
    # Create template similar to base_templates.toml example
    template = TemplateDefinition(
        name="KinkoTechModelBase",
        namespace="kinkotech.common.infrastructure.models.base",
        columns=[
            ColumnDefinition(
                name="id",
                type="bigint",
                db_column="id",
                is_pk=True,
                nullable=False
            ),
        ],
        package="kinkotech.common.infrastructure.models.base"
    )
    
    file_path = writer.write_template(
        "kinkotech.common.infrastructure.models.base",
        template
    )
    
    # Read and verify format
    with open(file_path, 'r') as f:
        data = toml.load(f)
    
    # Verify structure
    assert 'templates' in data
    assert 'KinkoTechModelBase' in data['templates']
    
    template_data = data['templates']['KinkoTechModelBase']
    assert template_data['package'] == "kinkotech.common.infrastructure.models.base"
    assert 'columns' in template_data
    assert len(template_data['columns']) == 1
    
    # Verify column format
    id_col = template_data['columns'][0]
    assert id_col['name'] == 'id'
    assert id_col['type'] == 'bigint'
    assert id_col['primary_key'] is True
    assert id_col['nullable'] is False


def test_mixed_entities_and_templates(temp_dir):
    """Test that entities and templates can coexist in same file"""
    writer = TOMLWriter(base_dir=temp_dir)
    
    # Write a template first
    template = TemplateDefinition(
        name="BaseMixin",
        namespace="myapp.models",
        columns=[
            ColumnDefinition(name="id", type="int", db_column="id", is_pk=True)
        ],
        package="myapp.models"
    )
    
    writer.write_template("myapp.models", template)
    
    # Write an entity to the same namespace
    entity = EntityDefinition(
        name="User",
        namespace="myapp.models",
        table_name="users",
        columns=[
            ColumnDefinition(name="username", type="string", db_column="username")
        ],
        extends=["myapp.models.BaseMixin"]
    )
    
    file_path = writer.write_entity("myapp.models", entity)
    
    # Verify both are in the same file
    with open(file_path, 'r') as f:
        data = toml.load(f)
    
    assert 'templates' in data
    assert 'BaseMixin' in data['templates']
    assert 'entities' in data
    assert 'User' in data['entities']


def test_column_optional_fields_omitted_when_default(temp_dir):
    """Test that optional fields with default values are omitted"""
    writer = TOMLWriter(base_dir=temp_dir)
    
    # Create entity with columns having default values
    entity = EntityDefinition(
        name="SimpleEntity",
        namespace="myapp.models",
        table_name="simple_entity",
        columns=[
            ColumnDefinition(
                name="id",
                type="int",
                db_column="id",  # Same as name, should be omitted
                is_pk=False,  # Default, should be omitted
                is_fk=False,  # Default, should be omitted
                nullable=True,  # Default, should be omitted
                unique=False,  # Default, should be omitted
                indexed=False,  # Default, should be omitted
            ),
        ]
    )
    
    file_path = writer.write_entity("myapp.models", entity)
    
    # Verify only required fields are present
    with open(file_path, 'r') as f:
        data = toml.load(f)
    
    col = data['entities']['SimpleEntity']['columns'][0]
    assert col['name'] == 'id'
    assert col['type'] == 'int'
    # These should not be present (default values)
    assert 'db_column' not in col
    assert 'primary_key' not in col
    assert 'foreign_key' not in col
    assert 'nullable' not in col
    assert 'unique' not in col
    assert 'indexed' not in col


def test_column_optional_fields_included_when_non_default(temp_dir):
    """Test that optional fields with non-default values are included"""
    writer = TOMLWriter(base_dir=temp_dir)
    
    # Create entity with columns having non-default values
    entity = EntityDefinition(
        name="ComplexEntity",
        namespace="myapp.models",
        table_name="complex_entity",
        columns=[
            ColumnDefinition(
                name="id",
                type="int",
                db_column="custom_id",  # Different from name
                is_pk=True,  # Non-default
                nullable=False,  # Non-default
                unique=True,  # Non-default
                indexed=True,  # Non-default
                max_length=100,  # Non-null
                comment="Custom ID field",  # Non-null
                default=0,  # Non-null
            ),
        ]
    )
    
    file_path = writer.write_entity("myapp.models", entity)
    
    # Verify all non-default fields are present
    with open(file_path, 'r') as f:
        data = toml.load(f)
    
    col = data['entities']['ComplexEntity']['columns'][0]
    assert col['name'] == 'id'
    assert col['type'] == 'int'
    assert col['db_column'] == 'custom_id'
    assert col['primary_key'] is True
    assert col['nullable'] is False
    assert col['unique'] is True
    assert col['max_length'] == 100
    assert col['comment'] == "Custom ID field"
    assert col['default'] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
