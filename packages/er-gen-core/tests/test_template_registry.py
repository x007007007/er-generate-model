"""
Unit tests for TemplateRegistry class.

Tests template discovery, resolution, auto-derivation of export_path,
duplicate detection, and validation.
"""
import pytest
import tempfile
import os
from pathlib import Path

from x007007007.er.template_registry import (
    TemplateRegistry,
    ConflictError,
    TemplateNotFoundError,
    ValidationError
)


def test_discover_single_file_with_package():
    """Test discovering templates from a single TOML file with package field."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write("""
[templates.TestMixin]
package = "myapp.models.base"

[[templates.TestMixin.columns]]
name = "id"
type = "bigint"
primary_key = true

[[templates.TestMixin.columns]]
name = "created_at"
type = "datetime"
nullable = false
""")
        f.flush()
        temp_file = f.name
    
    try:
        registry = TemplateRegistry()
        templates = registry.discover_templates([temp_file])
        
        assert len(templates) == 1
        assert "TestMixin" in templates
        
        template = templates["TestMixin"]
        assert template.name == "TestMixin"
        assert template.package == "myapp.models.base"
        # Auto-derived export_path should have _sqlalchemy suffix
        assert template.export_path == "myapp.models.base_sqlalchemy"
        assert len(template.columns) == 2
        assert template.columns[0].name == "id"
        assert template.columns[1].name == "created_at"
    finally:
        os.unlink(temp_file)


def test_discover_with_explicit_export_path():
    """Test that explicit export_path takes precedence over package."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write("""
[templates.TestMixin]
package = "myapp.models.base"
export_path = "custom.export.path"

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
        assert template.export_path == "custom.export.path"
        assert template.package == "myapp.models.base"
    finally:
        os.unlink(temp_file)


def test_discover_multiple_files():
    """Test discovering templates from multiple TOML files."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f1:
        f1.write("""
[templates.Mixin1]
package = "app1.models"

[[templates.Mixin1.columns]]
name = "field1"
type = "string"
""")
        f1.flush()
        temp_file1 = f1.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f2:
        f2.write("""
[templates.Mixin2]
package = "app2.models"

[[templates.Mixin2.columns]]
name = "field2"
type = "integer"
""")
        f2.flush()
        temp_file2 = f2.name
    
    try:
        registry = TemplateRegistry()
        templates = registry.discover_templates([temp_file1, temp_file2])
        
        assert len(templates) == 2
        assert "Mixin1" in templates
        assert "Mixin2" in templates
        assert templates["Mixin1"].columns[0].name == "field1"
        assert templates["Mixin2"].columns[0].name == "field2"
    finally:
        os.unlink(temp_file1)
        os.unlink(temp_file2)


def test_duplicate_template_detection():
    """Test that duplicate template names raise ConflictError."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f1:
        f1.write("""
[templates.DuplicateMixin]
package = "app1.models"

[[templates.DuplicateMixin.columns]]
name = "field1"
type = "string"
""")
        f1.flush()
        temp_file1 = f1.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f2:
        f2.write("""
[templates.DuplicateMixin]
package = "app2.models"

[[templates.DuplicateMixin.columns]]
name = "field2"
type = "integer"
""")
        f2.flush()
        temp_file2 = f2.name
    
    try:
        registry = TemplateRegistry()
        with pytest.raises(ConflictError) as exc_info:
            registry.discover_templates([temp_file1, temp_file2])
        
        assert "DuplicateMixin" in str(exc_info.value)
        assert temp_file1 in str(exc_info.value)
        assert temp_file2 in str(exc_info.value)
    finally:
        os.unlink(temp_file1)
        os.unlink(temp_file2)


def test_resolve_template():
    """Test resolving templates by name."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write("""
[templates.ResolveMixin]
package = "myapp.models"

[[templates.ResolveMixin.columns]]
name = "id"
type = "bigint"
""")
        f.flush()
        temp_file = f.name
    
    try:
        registry = TemplateRegistry()
        registry.discover_templates([temp_file])
        
        # Resolve existing template
        template = registry.resolve_template("ResolveMixin")
        assert template is not None
        assert template.name == "ResolveMixin"
        
        # Resolve non-existing template
        template = registry.resolve_template("NonExistent")
        assert template is None
    finally:
        os.unlink(temp_file)


def test_validation_no_package_or_export_path():
    """Test that templates without package or export_path raise ValidationError."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write("""
[templates.InvalidMixin]

[[templates.InvalidMixin.columns]]
name = "id"
type = "bigint"
""")
        f.flush()
        temp_file = f.name
    
    try:
        registry = TemplateRegistry()
        with pytest.raises(ValidationError) as exc_info:
            registry.discover_templates([temp_file])
        
        assert "InvalidMixin" in str(exc_info.value)
        assert "package" in str(exc_info.value) or "export_path" in str(exc_info.value)
    finally:
        os.unlink(temp_file)


def test_validation_empty_columns():
    """Test that templates with empty columns list raise ValidationError."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write("""
[templates.EmptyMixin]
package = "myapp.models"
columns = []
""")
        f.flush()
        temp_file = f.name
    
    try:
        registry = TemplateRegistry()
        with pytest.raises(ValidationError) as exc_info:
            registry.discover_templates([temp_file])
        
        assert "EmptyMixin" in str(exc_info.value)
        assert "empty columns" in str(exc_info.value).lower()
    finally:
        os.unlink(temp_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
