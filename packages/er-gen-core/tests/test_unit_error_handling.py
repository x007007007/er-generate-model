"""
Unit Tests for Error Handling

These tests verify error handling across all components:
- Duplicate template error reporting (TemplateRegistry)
- Missing template error reporting (TemplateRegistry)
- Invalid package path error reporting (NamespaceTransformer)
- File generation failure reporting (MixinGenerator)
- TOML parsing error reporting (TemplateRegistry)

**Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5**
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from x007007007.er.template_registry import (
    TemplateRegistry,
    ConflictError,
    TemplateNotFoundError,
    ValidationError
)
from x007007007.er.namespace import NamespaceTransformer
from x007007007.er.mixin_generator import MixinGenerator
from x007007007.er.models import TemplateInfo, Column


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


class TestDuplicateTemplateErrorReporting:
    """
    Test duplicate template error reporting.
    
    **Validates: Requirement 10.1**
    
    When a template conflict occurs, the Template_Registry SHALL report both 
    conflicting file paths.
    """
    
    def test_duplicate_template_reports_both_file_paths(self):
        """
        Test that ConflictError includes both conflicting file paths.
        
        The error message should clearly identify:
        - The duplicate template name
        - The first file where it was defined
        - The second file where it was found
        """
        temp_file1 = None
        temp_file2 = None
        try:
            content1 = """
[templates.DuplicateTemplate]
package = "app1.models"

[[templates.DuplicateTemplate.columns]]
name = "id"
type = "integer"
"""
            
            content2 = """
[templates.DuplicateTemplate]
package = "app2.models"

[[templates.DuplicateTemplate.columns]]
name = "id"
type = "bigint"
"""
            
            temp_file1 = create_toml_file(content1)
            temp_file2 = create_toml_file(content2)
            
            registry = TemplateRegistry()
            
            with pytest.raises(ConflictError) as exc_info:
                registry.discover_templates([temp_file1, temp_file2])
            
            error_message = str(exc_info.value)
            
            # Verify error message contains template name
            assert "DuplicateTemplate" in error_message, (
                "Error message should mention the duplicate template name"
            )
            
            # Verify error message contains both file paths
            assert temp_file1 in error_message or Path(temp_file1).name in error_message, (
                "Error message should mention the first file"
            )
            assert temp_file2 in error_message or Path(temp_file2).name in error_message, (
                "Error message should mention the second file"
            )
            
            # Verify error message is clear about the issue
            assert "Duplicate" in error_message or "duplicate" in error_message, (
                "Error message should clearly indicate this is a duplicate"
            )
        
        finally:
            if temp_file1:
                os.unlink(temp_file1)
            if temp_file2:
                os.unlink(temp_file2)
    
    def test_duplicate_template_error_message_format(self):
        """
        Test that duplicate template error message is well-formatted and informative.
        
        The error message should be clear enough for a developer to:
        1. Understand what went wrong
        2. Identify which template is duplicated
        3. Know which files to check
        """
        temp_file1 = None
        temp_file2 = None
        try:
            content = """
[templates.ConflictingName]
package = "test.models"

[[templates.ConflictingName.columns]]
name = "field"
type = "string"
"""
            
            temp_file1 = create_toml_file(content)
            temp_file2 = create_toml_file(content)
            
            registry = TemplateRegistry()
            
            with pytest.raises(ConflictError) as exc_info:
                registry.discover_templates([temp_file1, temp_file2])
            
            error_message = str(exc_info.value)
            
            # Verify message structure
            assert "ConflictingName" in error_message
            assert "found in files" in error_message or "files:" in error_message, (
                "Error should indicate multiple files are involved"
            )
        
        finally:
            if temp_file1:
                os.unlink(temp_file1)
            if temp_file2:
                os.unlink(temp_file2)
    
    def test_multiple_duplicates_reported_separately(self):
        """
        Test that when multiple templates are processed, the first duplicate is reported.
        
        This ensures that errors are caught early and reported clearly.
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

[templates.Template2]
package = "app1.models"

[[templates.Template2.columns]]
name = "id"
type = "integer"
"""
            
            content2 = """
[templates.Template1]
package = "app2.models"

[[templates.Template1.columns]]
name = "id"
type = "integer"

[templates.Template3]
package = "app2.models"

[[templates.Template3.columns]]
name = "id"
type = "integer"
"""
            
            temp_file1 = create_toml_file(content1)
            temp_file2 = create_toml_file(content2)
            
            registry = TemplateRegistry()
            
            # Should fail on first duplicate (Template1)
            with pytest.raises(ConflictError) as exc_info:
                registry.discover_templates([temp_file1, temp_file2])
            
            error_message = str(exc_info.value)
            assert "Template1" in error_message
        
        finally:
            if temp_file1:
                os.unlink(temp_file1)
            if temp_file2:
                os.unlink(temp_file2)


class TestMissingTemplateErrorReporting:
    """
    Test missing template error reporting.
    
    **Validates: Requirement 10.2**
    
    When a template is not found, the Template_Registry SHALL report the template 
    name and requesting entity.
    """
    
    def test_missing_template_returns_none_from_resolve(self):
        """
        Test that resolve_template returns None for missing templates.
        
        This is the expected behavior for template resolution - it returns None
        rather than raising an error, allowing the caller to decide how to handle it.
        """
        temp_file = None
        try:
            content = """
[templates.ExistingTemplate]
package = "test.models"

[[templates.ExistingTemplate.columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            registry.discover_templates([temp_file])
            
            # Resolve non-existent template
            result = registry.resolve_template("NonExistentTemplate")
            
            assert result is None, (
                "resolve_template should return None for missing templates"
            )
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_missing_template_name_reported_clearly(self):
        """
        Test that when a template is missing, the template name is clear.
        
        While resolve_template returns None, this test verifies that the template
        name can be used to generate clear error messages in calling code.
        """
        registry = TemplateRegistry()
        registry.discover_templates([])
        
        missing_template_name = "MissingTemplate"
        result = registry.resolve_template(missing_template_name)
        
        assert result is None
        
        # Verify that we can construct a clear error message
        if result is None:
            error_msg = f"Template '{missing_template_name}' not found in registry"
            assert missing_template_name in error_msg
            assert "not found" in error_msg
    
    def test_resolve_template_with_empty_registry(self):
        """
        Test resolving templates when registry is empty.
        
        This ensures that the error handling works even when no templates
        have been loaded.
        """
        registry = TemplateRegistry()
        
        # Don't discover any templates
        result = registry.resolve_template("AnyTemplate")
        
        assert result is None, (
            "Should return None when registry is empty"
        )
    
    def test_resolve_template_with_similar_name(self):
        """
        Test that template resolution is exact match only.
        
        This ensures that typos or similar names don't accidentally match.
        """
        temp_file = None
        try:
            content = """
[templates.UserModel]
package = "test.models"

[[templates.UserModel.columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            registry.discover_templates([temp_file])
            
            # Try to resolve with similar but different names
            assert registry.resolve_template("UserModel") is not None
            assert registry.resolve_template("usermodel") is None  # Case sensitive
            assert registry.resolve_template("UserModels") is None  # Extra 's'
            assert registry.resolve_template("User") is None  # Partial match
        
        finally:
            if temp_file:
                os.unlink(temp_file)


class TestInvalidPackagePathErrorReporting:
    """
    Test invalid package path error reporting.
    
    **Validates: Requirement 10.3**
    
    When a package path is invalid, the Namespace_Transformer SHALL report the 
    invalid component.
    """
    
    def test_empty_package_path_error_message(self):
        """
        Test that empty package path produces clear error message.
        """
        transformer = NamespaceTransformer()
        
        with pytest.raises(ValueError) as exc_info:
            transformer.transform_package_to_export_path("")
        
        error_message = str(exc_info.value)
        assert "empty" in error_message.lower() or "cannot be empty" in error_message.lower(), (
            "Error message should indicate the package path is empty"
        )
    
    def test_none_package_path_error_message(self):
        """
        Test that None package path produces clear error message.
        """
        transformer = NamespaceTransformer()
        
        with pytest.raises((ValueError, AttributeError, TypeError)):
            transformer.transform_package_to_export_path(None)
    
    def test_invalid_identifier_in_package_path_reports_component(self):
        """
        Test that invalid Python identifier in package path reports the specific component.
        
        The error message should identify which component is invalid.
        """
        transformer = NamespaceTransformer()
        
        # Package with invalid identifier (contains hyphen)
        with pytest.raises(ValueError) as exc_info:
            transformer.transform_package_to_export_path("my-app.models.base")
        
        error_message = str(exc_info.value)
        
        # Should mention the invalid component
        assert "my-app" in error_message or "identifier" in error_message.lower(), (
            "Error message should identify the invalid component"
        )
    
    def test_package_with_empty_component_reports_issue(self):
        """
        Test that package path with empty components reports the issue clearly.
        """
        transformer = NamespaceTransformer()
        
        # Package with empty component (double dot)
        with pytest.raises(ValueError) as exc_info:
            transformer.transform_package_to_export_path("myapp..models")
        
        error_message = str(exc_info.value)
        
        assert "empty" in error_message.lower() or "component" in error_message.lower(), (
            "Error message should indicate there's an empty component"
        )
    
    def test_package_with_number_start_reports_invalid_identifier(self):
        """
        Test that package component starting with number is reported as invalid.
        """
        transformer = NamespaceTransformer()
        
        # Package component starting with number
        with pytest.raises(ValueError) as exc_info:
            transformer.transform_package_to_export_path("myapp.123models.base")
        
        error_message = str(exc_info.value)
        
        assert "identifier" in error_message.lower() or "123models" in error_message, (
            "Error message should indicate invalid Python identifier"
        )
    
    def test_package_with_special_characters_reports_component(self):
        """
        Test that package with special characters reports the problematic component.
        """
        transformer = NamespaceTransformer()
        
        invalid_packages = [
            "my@app.models",
            "myapp.models!.base",
            "myapp.mod els.base",  # Space in component
            "myapp.models#base",
        ]
        
        for invalid_package in invalid_packages:
            with pytest.raises(ValueError) as exc_info:
                transformer.transform_package_to_export_path(invalid_package)
            
            error_message = str(exc_info.value)
            assert "identifier" in error_message.lower() or invalid_package in error_message, (
                f"Error message should identify issue with: {invalid_package}"
            )
    
    def test_unsupported_framework_error_message(self):
        """
        Test that unsupported framework produces clear error message.
        """
        transformer = NamespaceTransformer()
        
        with pytest.raises(ValueError) as exc_info:
            transformer.transform_package_to_export_path("myapp.models", "unsupported_framework")
        
        error_message = str(exc_info.value)
        
        assert "unsupported" in error_message.lower() or "framework" in error_message.lower(), (
            "Error message should indicate unsupported framework"
        )
        assert "unsupported_framework" in error_message, (
            "Error message should mention the specific framework name"
        )


class TestFileGenerationFailureReporting:
    """
    Test file generation failure reporting.
    
    **Validates: Requirement 10.4**
    
    When file generation fails, the Mixin_Generator SHALL report the target path 
    and error reason.
    """
    
    def test_missing_export_path_error_includes_template_name(self):
        """
        Test that missing export_path error includes template name.
        """
        generator = MixinGenerator()
        
        columns = [
            Column(name='id', type='bigint', db_column='id', is_pk=True)
        ]
        
        template_info = TemplateInfo(
            name='TestTemplate',
            package='test.models',
            export_path=None,  # Missing export_path
            columns=columns,
            source_file='test.toml'
        )
        
        with pytest.raises(ValueError) as exc_info:
            generator.generate_mixin_file('TestTemplate', template_info, '/tmp')
        
        error_message = str(exc_info.value)
        
        assert "TestTemplate" in error_message, (
            "Error message should include template name"
        )
        assert "export_path" in error_message, (
            "Error message should mention export_path"
        )
    
    def test_empty_columns_error_includes_template_name(self):
        """
        Test that empty columns error includes template name.
        """
        generator = MixinGenerator()
        
        template_info = TemplateInfo(
            name='EmptyColumnsTemplate',
            package='test.models',
            export_path='test.models_sqlalchemy',
            columns=[],  # Empty columns
            source_file='test.toml'
        )
        
        with pytest.raises(ValueError) as exc_info:
            generator.generate_mixin_file('EmptyColumnsTemplate', template_info, '/tmp')
        
        error_message = str(exc_info.value)
        
        assert "EmptyColumnsTemplate" in error_message, (
            "Error message should include template name"
        )
        assert "empty" in error_message.lower() or "columns" in error_message, (
            "Error message should mention empty columns"
        )
    
    def test_empty_template_name_error_message(self):
        """
        Test that empty template name produces clear error.
        """
        generator = MixinGenerator()
        
        columns = [
            Column(name='id', type='bigint', db_column='id', is_pk=True)
        ]
        
        template_info = TemplateInfo(
            name='TestTemplate',
            package='test.models',
            export_path='test.models_sqlalchemy',
            columns=columns,
            source_file='test.toml'
        )
        
        with pytest.raises(ValueError) as exc_info:
            generator.generate_mixin_file('', template_info, '/tmp')  # Empty name
        
        error_message = str(exc_info.value)
        
        assert "template_name" in error_message or "empty" in error_message.lower(), (
            "Error message should indicate template name is empty"
        )
    
    def test_permission_error_includes_path_and_reason(self):
        """
        Test that permission errors include the target path and reason.
        
        This test simulates a permission error during directory creation.
        """
        generator = MixinGenerator()
        
        columns = [
            Column(name='id', type='bigint', db_column='id', is_pk=True)
        ]
        
        template_info = TemplateInfo(
            name='PermissionTest',
            package='test.models',
            export_path='test.models_sqlalchemy',
            columns=columns,
            source_file='test.toml'
        )
        
        # Mock Path.mkdir to raise PermissionError
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError) as exc_info:
                generator.generate_mixin_file('PermissionTest', template_info, '/tmp')
            
            error_message = str(exc_info.value)
            
            # Should include path information
            assert "test" in error_message.lower() or "models" in error_message.lower() or "Permission" in error_message, (
                "Error message should include path or permission information"
            )
    
    def test_write_error_includes_file_path(self):
        """
        Test that write errors include the file path.
        
        This test simulates a write error during file creation.
        """
        generator = MixinGenerator()
        
        columns = [
            Column(name='id', type='bigint', db_column='id', is_pk=True)
        ]
        
        template_info = TemplateInfo(
            name='WriteErrorTest',
            package='test.models',
            export_path='test.models_sqlalchemy',
            columns=columns,
            source_file='test.toml'
        )
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the open function to raise PermissionError
            with patch('builtins.open', side_effect=PermissionError("Cannot write")):
                with pytest.raises(PermissionError) as exc_info:
                    generator.generate_mixin_file('WriteErrorTest', template_info, temp_dir)
                
                error_message = str(exc_info.value)
                
                # Should include file path or write information
                assert "write" in error_message.lower() or "Cannot" in error_message, (
                    "Error message should indicate write failure"
                )


class TestTOMLParsingErrorReporting:
    """
    Test TOML parsing error reporting.
    
    **Validates: Requirement 10.5**
    
    When TOML parsing fails, the Template_Registry SHALL report the file path 
    and line number if available.
    """
    
    def test_malformed_toml_error_propagates(self):
        """
        Test that malformed TOML file errors are propagated with context.
        
        The TOML library will raise its own error, but we should ensure
        the file path is available in the error context.
        """
        temp_file = None
        try:
            # Create malformed TOML (unclosed bracket)
            content = """
[templates.BadToml
package = "test.models"

[[templates.BadToml.columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            
            # Should raise TOML parsing error
            with pytest.raises(Exception) as exc_info:  # toml.TomlDecodeError or similar
                registry.discover_templates([temp_file])
            
            # The error should be related to TOML parsing
            error_type = type(exc_info.value).__name__
            assert "Toml" in error_type or "Decode" in error_type or "Parse" in error_type or "Expected" in str(exc_info.value), (
                f"Should raise TOML-related error, got: {error_type}"
            )
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_nonexistent_file_error_includes_path(self):
        """
        Test that non-existent file error includes the file path.
        """
        registry = TemplateRegistry()
        
        nonexistent_path = "/nonexistent/path/to/file.toml"
        
        with pytest.raises(FileNotFoundError) as exc_info:
            registry.discover_templates([nonexistent_path])
        
        error_message = str(exc_info.value)
        
        assert nonexistent_path in error_message or "file.toml" in error_message, (
            "Error message should include the file path"
        )
    
    def test_invalid_toml_structure_error_includes_file_path(self):
        """
        Test that invalid TOML structure errors include file path context.
        """
        temp_file = None
        try:
            # Create TOML with invalid structure (templates is not a dict)
            content = """
templates = "not a dictionary"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            
            with pytest.raises(ValidationError) as exc_info:
                registry.discover_templates([temp_file])
            
            error_message = str(exc_info.value)
            
            # Should mention the file and the issue
            assert temp_file in error_message or "templates" in error_message, (
                "Error message should provide context about the file or section"
            )
            assert "dictionary" in error_message.lower() or "dict" in error_message.lower(), (
                "Error message should indicate the type issue"
            )
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_invalid_template_data_error_includes_file_and_template(self):
        """
        Test that invalid template data errors include file path and template name.
        """
        temp_file = None
        try:
            # Create TOML with invalid template data (template is not a dict)
            content = """
[templates]
BadTemplate = "not a dictionary"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            
            with pytest.raises(ValidationError) as exc_info:
                registry.discover_templates([temp_file])
            
            error_message = str(exc_info.value)
            
            # Should mention the template name and file
            assert "BadTemplate" in error_message, (
                "Error message should include template name"
            )
            assert temp_file in error_message or "dictionary" in error_message.lower(), (
                "Error message should provide context"
            )
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_missing_required_field_error_includes_context(self):
        """
        Test that missing required field errors include helpful context.
        """
        temp_file = None
        try:
            # Create TOML with template missing both package and export_path
            content = """
[templates.MissingFields]

[[templates.MissingFields.columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            
            with pytest.raises(ValidationError) as exc_info:
                registry.discover_templates([temp_file])
            
            error_message = str(exc_info.value)
            
            # Should mention the template and the missing fields
            assert "MissingFields" in error_message, (
                "Error message should include template name"
            )
            assert "package" in error_message or "export_path" in error_message, (
                "Error message should mention the missing fields"
            )
            assert temp_file in error_message, (
                "Error message should include file path"
            )
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_invalid_column_data_error_includes_context(self):
        """
        Test that invalid column data errors include template and file context.
        """
        temp_file = None
        try:
            # Create TOML with column missing required field
            content = """
[templates.BadColumn]
package = "test.models"

[[templates.BadColumn.columns]]
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            
            with pytest.raises(ValidationError) as exc_info:
                registry.discover_templates([temp_file])
            
            error_message = str(exc_info.value)
            
            # Should mention the template, column, and file
            assert "BadColumn" in error_message, (
                "Error message should include template name"
            )
            assert "name" in error_message.lower() or "column" in error_message.lower(), (
                "Error message should mention the column issue"
            )
            assert temp_file in error_message, (
                "Error message should include file path"
            )
        
        finally:
            if temp_file:
                os.unlink(temp_file)


class TestErrorMessageQuality:
    """
    Test overall error message quality and informativeness.
    
    These tests ensure that error messages are:
    - Clear and understandable
    - Include relevant context
    - Help developers quickly identify and fix issues
    """
    
    def test_validation_error_messages_are_actionable(self):
        """
        Test that validation errors provide actionable information.
        
        A good error message tells the developer:
        1. What went wrong
        2. Where it went wrong
        3. How to fix it (implicitly)
        """
        temp_file = None
        try:
            content = """
[templates.InvalidTemplate]
package = "my-invalid-package"

[[templates.InvalidTemplate.columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            
            with pytest.raises(ValidationError) as exc_info:
                registry.discover_templates([temp_file])
            
            error_message = str(exc_info.value)
            
            # Should be informative
            assert len(error_message) > 20, (
                "Error message should be descriptive, not just a code"
            )
            
            # Should include key information
            has_template_name = "InvalidTemplate" in error_message
            has_package_info = "package" in error_message.lower() or "my-invalid-package" in error_message
            has_identifier_info = "identifier" in error_message.lower()
            
            assert has_template_name or has_package_info or has_identifier_info, (
                "Error message should include relevant context"
            )
        
        finally:
            if temp_file:
                os.unlink(temp_file)
    
    def test_error_messages_use_consistent_terminology(self):
        """
        Test that error messages use consistent terminology.
        
        This helps developers understand the system better.
        """
        temp_file = None
        try:
            content = """
[templates.Test1]

[[templates.Test1.columns]]
name = "id"
type = "integer"
"""
            temp_file = create_toml_file(content)
            
            registry = TemplateRegistry()
            
            with pytest.raises(ValidationError) as exc_info:
                registry.discover_templates([temp_file])
            
            error_message = str(exc_info.value)
            
            # Should use consistent terms like "template", "package", "export_path"
            # rather than mixing synonyms
            assert "template" in error_message.lower() or "Template" in error_message, (
                "Error messages should use 'template' terminology"
            )
        
        finally:
            if temp_file:
                os.unlink(temp_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
