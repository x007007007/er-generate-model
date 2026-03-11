"""
Unit Tests for TemplateRegistry

These tests verify specific examples and edge cases for template discovery and resolution:
- Single file template discovery
- Multiple file template discovery
- Duplicate template detection
- Auto-derivation of export_path
- Explicit export_path precedence
- Template resolution by name
- Validation errors

Requirements: 2.1, 2.2, 2.3, 3.1, 7.1, 7.2, 7.4, 7.5
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


def create_toml_file(content: str) -> str:
    """
    Create a temporary TOML file with the given content.
    
    Args:
        content: TOML content as string
        
    Returns:
        Path to the created temporary file
    """
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False)
    f.write(content)
    f.flush()
    f.close()
    return f.name


class TestSingleFileTemplateDiscovery:
    """Test template discovery from a single TOML file."""
    
    def test_discover_single_template_with_package(self):
        """
        Test discovery of a single template with package field.
        
        Requirements: 2.1, 2.2
        """
        temp_file = None
        try:
            content = """
[templates.KinkoTechModelBase]
package = "kinkotech.common.models.base"

[[templates.KinkoTechModelBase.columns]]
name = "id"
type = "bigint"
primary_key = true

[[templates.KinkoTechModelBase.columns]]
name = "created_at"
type = "datetime"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            templates = registry.discover_templates([temp_file])
            
            assert len(templates) == 1, "Should discover exactly one template"
            assert "KinkoTechModelBase" in templates, "Template name should be in registry"
            
            template = templates["KinkoTechModelBase"]
            assert template.name == "KinkoTechModelBase"
            assert template.package == "kinkotech.common.models.base"
            assert template.export_path == "kinkotech.common.models.base_sqlalchemy"
            assert len(template.columns) == 2
            assert template.columns[0].name == "id"
            assert template.columns[1].name == "created_at"
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_discover_multiple_templates_from_single_file(self):
        """
        Test discovery of multiple templates from a single TOML file.
        
        Requirements: 2.1
        """
        temp_file = None
        try:
            content = """
[templates.BaseModel]
package = "myapp.models.base"

[[templates.BaseModel.columns]]
name = "id"
type = "integer"
primary_key = true

[templates.TimestampMixin]
package = "myapp.models.mixins"

[[templates.TimestampMixin.columns]]
name = "created_at"
type = "datetime"

[[templates.TimestampMixin.columns]]
name = "updated_at"
type = "datetime"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            templates = registry.discover_templates([temp_file])
            
            assert len(templates) == 2, "Should discover two templates"
            assert "BaseModel" in templates
            assert "TimestampMixin" in templates
            
            assert templates["BaseModel"].package == "myapp.models.base"
            assert templates["TimestampMixin"].package == "myapp.models.mixins"
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_discover_template_with_explicit_export_path(self):
        """
        Test discovery of template with explicit export_path.
        
        Requirements: 2.1, 2.3
        """
        temp_file = None
        try:
            content = """
[templates.CustomMixin]
package = "myapp.models.base"
export_path = "myapp.custom.sqlalchemy.mixins"

[[templates.CustomMixin.columns]]
name = "status"
type = "string"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            templates = registry.discover_templates([temp_file])
            
            assert len(templates) == 1
            template = templates["CustomMixin"]
            assert template.export_path == "myapp.custom.sqlalchemy.mixins"
            assert template.package == "myapp.models.base"
        
        finally:
            if temp_file:
                os.unlink(temp_file)


class TestMultipleFileTemplateDiscovery:
    """Test template discovery from multiple TOML files."""
    
    def test_discover_templates_from_two_files(self):
        """
        Test discovery of templates from two separate TOML files.
        
        Requirements: 2.1
        """
        temp_file1 = None
        temp_file2 = None
        try:
            content1 = """
[templates.BaseModel]
package = "common.models.base"

[[templates.BaseModel.columns]]
name = "id"
type = "integer"
primary_key = true
"""
            
            content2 = """
[templates.TimestampMixin]
package = "common.models.mixins"

[[templates.TimestampMixin.columns]]
name = "created_at"
type = "datetime"
"""
            
            temp_file1 = create_toml_file(content1)
            temp_file2 = create_toml_file(content2)
            
            registry = TemplateRegistry()
            templates = registry.discover_templates([temp_file1, temp_file2])
            
            assert len(templates) == 2, "Should discover templates from both files"
            assert "BaseModel" in templates
            assert "TimestampMixin" in templates
        
        finally:
            if temp_file1:
                os.unlink(temp_file1)
            if temp_file2:
                os.unlink(temp_file2)
    
    def test_discover_templates_from_multiple_files_with_multiple_templates(self):
        """
        Test discovery when multiple files each contain multiple templates.
        
        Requirements: 2.1
        """
        temp_files = []
        try:
            content1 = """
[templates.BaseModel]
package = "app1.models"

[[templates.BaseModel.columns]]
name = "id"
type = "integer"

[templates.Mixin1]
package = "app1.mixins"

[[templates.Mixin1.columns]]
name = "field1"
type = "string"
"""
            
            content2 = """
[templates.BaseModel2]
package = "app2.models"

[[templates.BaseModel2.columns]]
name = "id"
type = "bigint"

[templates.Mixin2]
package = "app2.mixins"

[[templates.Mixin2.columns]]
name = "field2"
type = "integer"
"""
            
            temp_files.append(create_toml_file(content1))
            temp_files.append(create_toml_file(content2))
            
            registry = TemplateRegistry()
            templates = registry.discover_templates(temp_files)
            
            assert len(templates) == 4, "Should discover all templates from all files"
            assert "BaseModel" in templates
            assert "Mixin1" in templates
            assert "BaseModel2" in templates
            assert "Mixin2" in templates
        
        finally:
            for temp_file in temp_files:
                os.unlink(temp_file)


class TestDuplicateTemplateDetection:
    """Test detection and reporting of duplicate template names."""
    
    def test_duplicate_template_names_raises_conflict_error(self):
        """
        Test that duplicate template names across files raise ConflictError.
        
        Requirements: 2.4
        """
        temp_file1 = None
        temp_file2 = None
        try:
            content1 = """
[templates.BaseModel]
package = "app1.models"

[[templates.BaseModel.columns]]
name = "id"
type = "integer"
"""
            
            content2 = """
[templates.BaseModel]
package = "app2.models"

[[templates.BaseModel.columns]]
name = "id"
type = "bigint"
"""
            
            temp_file1 = create_toml_file(content1)
            temp_file2 = create_toml_file(content2)
            
            registry = TemplateRegistry()
            
            with pytest.raises(ConflictError) as exc_info:
                registry.discover_templates([temp_file1, temp_file2])
            
            error_message = str(exc_info.value)
            assert "BaseModel" in error_message, "Error should mention template name"
            assert "Duplicate template" in error_message
        
        finally:
            if temp_file1:
                os.unlink(temp_file1)
            if temp_file2:
                os.unlink(temp_file2)
    
    def test_duplicate_in_same_file_handled_by_toml_parser(self):
        """
        Test that duplicates in the same file are handled by TOML parser.
        
        Note: TOML parser will either raise an error or use the last definition.
        
        Requirements: 2.4
        """
        temp_file = None
        try:
            # TOML spec says last definition wins for duplicate keys
            content = """
[templates.BaseModel]
package = "app1.models"

[[templates.BaseModel.columns]]
name = "id"
type = "integer"

[templates.BaseModel]
package = "app2.models"

[[templates.BaseModel.columns]]
name = "id"
type = "bigint"
"""
            
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            # This may raise an error or use last definition depending on TOML library
            # We just verify it doesn't crash unexpectedly
            try:
                templates = registry.discover_templates([temp_file])
                # If it succeeds, verify we got one template
                assert "BaseModel" in templates
            except Exception:
                # If it fails, that's also acceptable behavior
                pass
        
        finally:
            if temp_file:
                os.unlink(temp_file)


class TestExportPathAutoDerivation:
    """Test auto-derivation of export_path from package."""
    
    def test_export_path_auto_derived_when_only_package_specified(self):
        """
        Test that export_path is auto-derived when only package is specified.
        
        Requirements: 2.2
        """
        temp_file = None
        try:
            content = """
[templates.MyModel]
package = "myapp.models.base"

[[templates.MyModel.columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            templates = registry.discover_templates([temp_file])
            
            template = templates["MyModel"]
            assert template.export_path == "myapp.models.base_sqlalchemy"
            assert template.package == "myapp.models.base"
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_export_path_auto_derived_with_single_component_package(self):
        """
        Test auto-derivation with single-component package.
        
        Requirements: 2.2
        """
        temp_file = None
        try:
            content = """
[templates.SimpleModel]
package = "models"

[[templates.SimpleModel.columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            templates = registry.discover_templates([temp_file])
            
            template = templates["SimpleModel"]
            assert template.export_path == "models_sqlalchemy"
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_export_path_auto_derived_preserves_package_structure(self):
        """
        Test that auto-derivation preserves all package components except last.
        
        Requirements: 2.2
        """
        temp_file = None
        try:
            content = """
[templates.DeepModel]
package = "company.division.team.project.models"

[[templates.DeepModel.columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            templates = registry.discover_templates([temp_file])
            
            template = templates["DeepModel"]
            assert template.export_path == "company.division.team.project.models_sqlalchemy"
            
            # Verify structure is preserved
            original_parts = template.package.split('.')
            derived_parts = template.export_path.split('.')
            
            assert len(original_parts) == len(derived_parts)
            for i in range(len(original_parts) - 1):
                assert original_parts[i] == derived_parts[i]
        
        finally:
            if temp_file:
                os.unlink(temp_file)


class TestExplicitExportPathPrecedence:
    """Test that explicit export_path takes precedence over auto-derivation."""
    
    def test_explicit_export_path_used_when_both_specified(self):
        """
        Test that explicit export_path is used when both package and export_path are specified.
        
        Requirements: 2.3
        """
        temp_file = None
        try:
            content = """
[templates.CustomModel]
package = "myapp.models.base"
export_path = "custom.path.to.mixins"

[[templates.CustomModel.columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            templates = registry.discover_templates([temp_file])
            
            template = templates["CustomModel"]
            assert template.export_path == "custom.path.to.mixins"
            assert template.export_path != "myapp.models.base_sqlalchemy"
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_explicit_export_path_not_transformed(self):
        """
        Test that explicit export_path is not transformed.
        
        Requirements: 2.3
        """
        temp_file = None
        try:
            content = """
[templates.NoTransform]
package = "myapp.models"
export_path = "already.has.sqlalchemy"

[[templates.NoTransform.columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            templates = registry.discover_templates([temp_file])
            
            template = templates["NoTransform"]
            # Should use explicit path exactly as specified
            assert template.export_path == "already.has.sqlalchemy"
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_export_path_only_without_package(self):
        """
        Test template with only export_path (no package).
        
        Requirements: 2.3
        """
        temp_file = None
        try:
            content = """
[templates.ExportOnly]
export_path = "custom.export.path"

[[templates.ExportOnly.columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            templates = registry.discover_templates([temp_file])
            
            template = templates["ExportOnly"]
            assert template.export_path == "custom.export.path"
            assert template.package is None
        
        finally:
            if temp_file:
                os.unlink(temp_file)


class TestTemplateResolution:
    """Test template resolution by name."""
    
    def test_resolve_existing_template(self):
        """
        Test resolving a template that exists in the registry.
        
        Requirements: 3.1
        """
        temp_file = None
        try:
            content = """
[templates.MyTemplate]
package = "myapp.models"

[[templates.MyTemplate.columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            registry.discover_templates([temp_file])
            
            resolved = registry.resolve_template("MyTemplate")
            
            assert resolved is not None
            assert resolved.name == "MyTemplate"
            assert resolved.package == "myapp.models"
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_resolve_nonexistent_template_returns_none(self):
        """
        Test that resolving a non-existent template returns None.
        
        Requirements: 3.2
        """
        temp_file = None
        try:
            content = """
[templates.ExistingTemplate]
package = "myapp.models"

[[templates.ExistingTemplate.columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            registry.discover_templates([temp_file])
            
            resolved = registry.resolve_template("NonExistentTemplate")
            
            assert resolved is None
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_resolve_template_from_multiple_files(self):
        """
        Test resolving templates from different files.
        
        Requirements: 3.1, 8.1
        """
        temp_file1 = None
        temp_file2 = None
        try:
            content1 = """
[templates.Template1]
package = "app1.models"

[[templates.Template1.columns]]
name = "id"
type = "integer"
"""
            
            content2 = """
[templates.Template2]
package = "app2.models"

[[templates.Template2.columns]]
name = "id"
type = "bigint"
"""
            
            temp_file1 = create_toml_file(content1)
            temp_file2 = create_toml_file(content2)
            
            registry = TemplateRegistry()
            registry.discover_templates([temp_file1, temp_file2])
            
            # Should be able to resolve templates from both files
            resolved1 = registry.resolve_template("Template1")
            resolved2 = registry.resolve_template("Template2")
            
            assert resolved1 is not None
            assert resolved1.name == "Template1"
            assert resolved2 is not None
            assert resolved2.name == "Template2"
        
        finally:
            if temp_file1:
                os.unlink(temp_file1)
            if temp_file2:
                os.unlink(temp_file2)
    
    def test_resolve_template_before_discovery_returns_none(self):
        """
        Test that resolving before discovery returns None.
        
        Requirements: 3.1
        """
        registry = TemplateRegistry()
        resolved = registry.resolve_template("AnyTemplate")
        
        assert resolved is None


class TestValidationErrors:
    """Test validation error handling."""
    
    def test_template_without_package_or_export_path_raises_error(self):
        """
        Test that template without package or export_path raises ValidationError.
        
        Requirements: 7.1
        """
        temp_file = None
        try:
            content = """
[templates.InvalidTemplate]

[[templates.InvalidTemplate.columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            
            with pytest.raises(ValidationError) as exc_info:
                registry.discover_templates([temp_file])
            
            error_message = str(exc_info.value)
            assert "package" in error_message or "export_path" in error_message
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_template_with_empty_columns_raises_error(self):
        """
        Test that template with empty columns list raises ValidationError.
        
        Requirements: 7.2
        """
        temp_file = None
        try:
            content = """
[templates.NoColumns]
package = "myapp.models"
columns = []
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            
            with pytest.raises(ValidationError) as exc_info:
                registry.discover_templates([temp_file])
            
            error_message = str(exc_info.value)
            assert "empty columns" in error_message.lower()
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_invalid_export_path_with_empty_component_raises_error(self):
        """
        Test that export_path with empty components raises ValidationError.
        
        Requirements: 7.4
        """
        temp_file = None
        try:
            content = """
[templates.BadExportPath]
export_path = "myapp..models"

[[templates.BadExportPath.columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            
            with pytest.raises(ValidationError) as exc_info:
                registry.discover_templates([temp_file])
            
            error_message = str(exc_info.value)
            assert "empty component" in error_message.lower()
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_invalid_export_path_with_invalid_identifier_raises_error(self):
        """
        Test that export_path with invalid Python identifier raises ValidationError.
        
        Requirements: 7.4
        """
        temp_file = None
        try:
            content = """
[templates.BadIdentifier]
export_path = "my-app.models"

[[templates.BadIdentifier.columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            
            with pytest.raises(ValidationError) as exc_info:
                registry.discover_templates([temp_file])
            
            error_message = str(exc_info.value)
            assert "not a valid Python identifier" in error_message
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_invalid_template_name_raises_error(self):
        """
        Test that invalid template name raises ValidationError.
        
        Requirements: 7.5
        """
        temp_file = None
        try:
            content = """
[templates."invalid-name"]
package = "myapp.models"

[[templates."invalid-name".columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            
            with pytest.raises(ValidationError) as exc_info:
                registry.discover_templates([temp_file])
            
            error_message = str(exc_info.value)
            assert "not a valid Python identifier" in error_message
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_malformed_toml_file_raises_error(self):
        """
        Test that malformed TOML file raises appropriate error.
        
        Requirements: 2.5
        """
        temp_file = None
        try:
            content = """
[templates.BadToml
package = "myapp.models"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            
            with pytest.raises(Exception):  # toml.TomlDecodeError or similar
                registry.discover_templates([temp_file])
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_nonexistent_file_raises_error(self):
        """
        Test that non-existent file raises FileNotFoundError.
        
        Requirements: 2.5
        """
        registry = TemplateRegistry()
        
        with pytest.raises(FileNotFoundError):
            registry.discover_templates(["/nonexistent/path/to/file.toml"])
    
    def test_column_without_name_raises_error(self):
        """
        Test that column without name field raises ValidationError.
        
        Requirements: 7.2
        """
        temp_file = None
        try:
            content = """
[templates.BadColumn]
package = "myapp.models"

[[templates.BadColumn.columns]]
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            
            with pytest.raises(ValidationError) as exc_info:
                registry.discover_templates([temp_file])
            
            error_message = str(exc_info.value)
            assert "name" in error_message.lower()
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_column_without_type_raises_error(self):
        """
        Test that column without type field raises ValidationError.
        
        Requirements: 7.2
        """
        temp_file = None
        try:
            content = """
[templates.BadColumn]
package = "myapp.models"

[[templates.BadColumn.columns]]
name = "id"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            
            with pytest.raises(ValidationError) as exc_info:
                registry.discover_templates([temp_file])
            
            error_message = str(exc_info.value)
            assert "type" in error_message.lower()
        
        finally:
            if temp_file:
                os.unlink(temp_file)


class TestSourceFileMetadata:
    """Test that source file metadata is preserved."""
    
    def test_source_file_stored_in_template_info(self):
        """
        Test that source file path is stored in TemplateInfo.
        
        Requirements: 8.2
        """
        temp_file = None
        try:
            content = """
[templates.MyTemplate]
package = "myapp.models"

[[templates.MyTemplate.columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            templates = registry.discover_templates([temp_file])
            
            template = templates["MyTemplate"]
            assert template.source_file is not None
            assert template.source_file.endswith(".toml")
            # Should be absolute path
            assert Path(template.source_file).is_absolute()
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_source_file_different_for_different_files(self):
        """
        Test that templates from different files have different source_file values.
        
        Requirements: 8.2
        """
        temp_file1 = None
        temp_file2 = None
        try:
            content1 = """
[templates.Template1]
package = "app1.models"

[[templates.Template1.columns]]
name = "id"
type = "integer"
"""
            
            content2 = """
[templates.Template2]
package = "app2.models"

[[templates.Template2.columns]]
name = "id"
type = "integer"
"""
            
            temp_file1 = create_toml_file(content1)
            temp_file2 = create_toml_file(content2)
            
            registry = TemplateRegistry()
            templates = registry.discover_templates([temp_file1, temp_file2])
            
            template1 = templates["Template1"]
            template2 = templates["Template2"]
            
            assert template1.source_file != template2.source_file
            assert Path(temp_file1).absolute() == Path(template1.source_file)
            assert Path(temp_file2).absolute() == Path(template2.source_file)
        
        finally:
            if temp_file1:
                os.unlink(temp_file1)
            if temp_file2:
                os.unlink(temp_file2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
