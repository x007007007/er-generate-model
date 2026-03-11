"""
Edge case tests for TemplateRegistry class.

Tests invalid inputs, malformed TOML, invalid package paths, etc.
"""
import pytest
import tempfile
import os

from x007007007.er.template_registry import (
    TemplateRegistry,
    ValidationError
)
import toml


def test_invalid_toml_file():
    """Test that malformed TOML files raise appropriate error."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write("""
[templates.BadMixin
# Missing closing bracket
package = "myapp.models"
""")
        f.flush()
        temp_file = f.name
    
    try:
        registry = TemplateRegistry()
        with pytest.raises(toml.TomlDecodeError):
            registry.discover_templates([temp_file])
    finally:
        os.unlink(temp_file)


def test_nonexistent_file():
    """Test that non-existent files raise FileNotFoundError."""
    registry = TemplateRegistry()
    with pytest.raises(FileNotFoundError):
        registry.discover_templates(['/nonexistent/path/to/file.toml'])


def test_invalid_package_path():
    """Test that invalid package paths raise ValidationError."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write("""
[templates.BadMixin]
package = "my-invalid-package.models"

[[templates.BadMixin.columns]]
name = "id"
type = "bigint"
""")
        f.flush()
        temp_file = f.name
    
    try:
        registry = TemplateRegistry()
        with pytest.raises(ValidationError) as exc_info:
            registry.discover_templates([temp_file])
        
        assert "my-invalid-package" in str(exc_info.value)
    finally:
        os.unlink(temp_file)


def test_invalid_template_name():
    """Test that invalid template names raise ValidationError."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write("""
[templates."Invalid-Name"]
package = "myapp.models"

[[templates."Invalid-Name".columns]]
name = "id"
type = "bigint"
""")
        f.flush()
        temp_file = f.name
    
    try:
        registry = TemplateRegistry()
        with pytest.raises(ValidationError) as exc_info:
            registry.discover_templates([temp_file])
        
        assert "Invalid-Name" in str(exc_info.value)
        assert "identifier" in str(exc_info.value).lower()
    finally:
        os.unlink(temp_file)


def test_invalid_export_path():
    """Test that invalid export_path raises ValidationError."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write("""
[templates.BadMixin]
export_path = "my-invalid.export.path"

[[templates.BadMixin.columns]]
name = "id"
type = "bigint"
""")
        f.flush()
        temp_file = f.name
    
    try:
        registry = TemplateRegistry()
        with pytest.raises(ValidationError) as exc_info:
            registry.discover_templates([temp_file])
        
        assert "export_path" in str(exc_info.value).lower()
    finally:
        os.unlink(temp_file)


def test_resolve_with_invalid_input():
    """Test that resolve_template validates input."""
    registry = TemplateRegistry()
    
    with pytest.raises(ValueError):
        registry.resolve_template("")
    
    with pytest.raises(ValueError):
        registry.resolve_template(123)  # type: ignore


def test_idempotent_transformation():
    """Test that already-transformed packages are handled correctly."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write("""
[templates.TestMixin]
package = "myapp.models.base_sqlalchemy"

[[templates.TestMixin.columns]]
name = "id"
type = "bigint"
""")
        f.flush()
        temp_file = f.name
    
    try:
        registry = TemplateRegistry()
        templates = registry.discover_templates([temp_file])
        
        template = templates["TestMixin"]
        # Should remain unchanged (idempotent)
        assert template.export_path == "myapp.models.base_sqlalchemy"
    finally:
        os.unlink(temp_file)


def test_column_without_required_fields():
    """Test that columns without required fields raise ValidationError."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write("""
[templates.BadMixin]
package = "myapp.models"

[[templates.BadMixin.columns]]
name = "id"
# Missing 'type' field
""")
        f.flush()
        temp_file = f.name
    
    try:
        registry = TemplateRegistry()
        with pytest.raises(ValidationError) as exc_info:
            registry.discover_templates([temp_file])
        
        assert "type" in str(exc_info.value).lower()
    finally:
        os.unlink(temp_file)


def test_empty_toml_file():
    """Test that empty TOML files are handled gracefully."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write("")
        f.flush()
        temp_file = f.name
    
    try:
        registry = TemplateRegistry()
        templates = registry.discover_templates([temp_file])
        
        # Should return empty dict
        assert len(templates) == 0
    finally:
        os.unlink(temp_file)


def test_toml_without_templates_section():
    """Test that TOML files without templates section are handled gracefully."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write("""
[entities.MyEntity]
table_name = "my_entity"

[[entities.MyEntity.columns]]
name = "id"
type = "bigint"
""")
        f.flush()
        temp_file = f.name
    
    try:
        registry = TemplateRegistry()
        templates = registry.discover_templates([temp_file])
        
        # Should return empty dict
        assert len(templates) == 0
    finally:
        os.unlink(temp_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
