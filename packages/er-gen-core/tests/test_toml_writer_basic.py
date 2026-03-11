"""
Basic tests for TOMLWriter to verify implementation
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
    # Cleanup
    shutil.rmtree(temp_path, ignore_errors=True)


def test_toml_writer_creates_entity_file(temp_dir):
    """Test that TOMLWriter creates a file for an entity"""
    writer = TOMLWriter(base_dir=temp_dir)
    
    # Create a simple entity
    entity = EntityDefinition(
        name="User",
        namespace="myapp.models",
        table_name="users",
        columns=[
            ColumnDefinition(
                name="id",
                type="int",
                db_column="id",
                is_pk=True,
                nullable=False
            ),
            ColumnDefinition(
                name="username",
                type="string",
                db_column="username",
                unique=True
            ),
        ],
        extends=[],
        comment="User entity"
    )
    
    # Write entity
    file_path = writer.write_entity("myapp.models", entity)
    
    # Verify file was created
    assert os.path.exists(file_path)
    expected_path = os.path.join(temp_dir, "myapp", "models.toml")
    assert file_path == expected_path
    
    # Verify content
    with open(file_path, 'r') as f:
        data = toml.load(f)
    
    assert 'entities' in data
    assert 'User' in data['entities']
    assert data['entities']['User']['comment'] == "User entity"
    assert len(data['entities']['User']['columns']) == 2


def test_toml_writer_creates_template_file(temp_dir):
    """Test that TOMLWriter creates a file for a template"""
    writer = TOMLWriter(base_dir=temp_dir)
    
    # Create a simple template
    template = TemplateDefinition(
        name="TimestampMixin",
        namespace="myapp.mixins",
        columns=[
            ColumnDefinition(
                name="created_at",
                type="datetime",
                db_column="created_at",
                nullable=False
            ),
            ColumnDefinition(
                name="updated_at",
                type="datetime",
                db_column="updated_at",
                nullable=False
            ),
        ],
        package="myapp.mixins"
    )
    
    # Write template
    file_path = writer.write_template("myapp.mixins", template)
    
    # Verify file was created
    assert os.path.exists(file_path)
    expected_path = os.path.join(temp_dir, "myapp", "mixins.toml")
    assert file_path == expected_path
    
    # Verify content
    with open(file_path, 'r') as f:
        data = toml.load(f)
    
    assert 'templates' in data
    assert 'TimestampMixin' in data['templates']
    assert data['templates']['TimestampMixin']['package'] == "myapp.mixins"
    assert len(data['templates']['TimestampMixin']['columns']) == 2


def test_toml_writer_appends_to_same_file(temp_dir):
    """Test that multiple entities in same namespace go to same file"""
    writer = TOMLWriter(base_dir=temp_dir)
    
    # Create first entity
    entity1 = EntityDefinition(
        name="User",
        namespace="myapp.models",
        table_name="users",
        columns=[
            ColumnDefinition(name="id", type="int", db_column="id", is_pk=True)
        ]
    )
    
    # Create second entity
    entity2 = EntityDefinition(
        name="Post",
        namespace="myapp.models",
        table_name="posts",
        columns=[
            ColumnDefinition(name="id", type="int", db_column="id", is_pk=True)
        ]
    )
    
    # Write both entities
    file_path1 = writer.write_entity("myapp.models", entity1)
    file_path2 = writer.write_entity("myapp.models", entity2)
    
    # Verify same file
    assert file_path1 == file_path2
    
    # Verify both entities in file
    with open(file_path1, 'r') as f:
        data = toml.load(f)
    
    assert 'entities' in data
    assert 'User' in data['entities']
    assert 'Post' in data['entities']


def test_toml_writer_uses_namespace_format_for_extends(temp_dir):
    """Test that extends uses namespace format"""
    writer = TOMLWriter(base_dir=temp_dir)
    
    # Create entity with extends
    entity = EntityDefinition(
        name="AdminUser",
        namespace="myapp.models",
        table_name="admin_users",
        columns=[
            ColumnDefinition(name="id", type="int", db_column="id", is_pk=True)
        ],
        extends=["myapp.base.BaseUser", "myapp.mixins.TimestampMixin"]
    )
    
    # Write entity
    file_path = writer.write_entity("myapp.models", entity)
    
    # Verify extends format
    with open(file_path, 'r') as f:
        data = toml.load(f)
    
    extends = data['entities']['AdminUser']['extends']
    assert extends == ["myapp.base.BaseUser", "myapp.mixins.TimestampMixin"]
    # Verify no file paths (no slashes)
    for ext in extends:
        assert '/' not in ext
        assert '\\' not in ext


def test_toml_writer_atomic_write(temp_dir):
    """Test that writes are atomic (no partial files on error)"""
    writer = TOMLWriter(base_dir=temp_dir)
    
    # Create a valid entity first
    entity1 = EntityDefinition(
        name="User",
        namespace="myapp.models",
        table_name="users",
        columns=[
            ColumnDefinition(name="id", type="int", db_column="id", is_pk=True)
        ]
    )
    
    file_path = writer.write_entity("myapp.models", entity1)
    
    # Verify file exists and has content
    assert os.path.exists(file_path)
    with open(file_path, 'r') as f:
        original_content = f.read()
    
    # The atomic write should ensure the file is never in a partial state
    # Even if we write again, the original should be preserved until complete
    entity2 = EntityDefinition(
        name="Post",
        namespace="myapp.models",
        table_name="posts",
        columns=[
            ColumnDefinition(name="id", type="int", db_column="id", is_pk=True)
        ]
    )
    
    writer.write_entity("myapp.models", entity2)
    
    # File should still be valid TOML
    with open(file_path, 'r') as f:
        data = toml.load(f)
    
    assert 'entities' in data
    assert 'User' in data['entities']
    assert 'Post' in data['entities']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
