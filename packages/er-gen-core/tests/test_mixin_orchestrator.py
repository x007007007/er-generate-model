"""
Unit tests for MixinOrchestrator.

Tests the orchestration of template discovery and mixin generation across
multiple TOML files with different inheritance modes.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from x007007007.er.mixin_orchestrator import MixinOrchestrator
from x007007007.er.template_registry import (
    ConflictError,
    TemplateNotFoundError,
    ValidationError
)


class TestMixinOrchestrator:
    """Test suite for MixinOrchestrator class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_toml_file(self, temp_dir):
        """Create a sample TOML file with templates."""
        toml_content = """
[templates.KinkoTechModelBase]
package = "kinkotech.common.models.base"

[[templates.KinkoTechModelBase.columns]]
name = "id"
type = "bigint"
primary_key = true

[[templates.KinkoTechModelBase.columns]]
name = "created_at"
type = "datetime"
nullable = false

[templates.TimestampMixin]
package = "kinkotech.common.models.timestamp"

[[templates.TimestampMixin.columns]]
name = "updated_at"
type = "datetime"
nullable = false
"""
        file_path = Path(temp_dir) / "models1.toml"
        file_path.write_text(toml_content)
        return str(file_path)
    
    @pytest.fixture
    def second_toml_file(self, temp_dir):
        """Create a second sample TOML file with templates."""
        toml_content = """
[templates.SoftDeleteMixin]
package = "kinkotech.common.models.soft_delete"

[[templates.SoftDeleteMixin.columns]]
name = "deleted_at"
type = "datetime"
nullable = true
"""
        file_path = Path(temp_dir) / "models2.toml"
        file_path.write_text(toml_content)
        return str(file_path)
    
    def test_process_templates_single_file_reference_mode(
        self, sample_toml_file, temp_dir
    ):
        """Test processing templates from a single file in reference mode."""
        orchestrator = MixinOrchestrator()
        output_dir = Path(temp_dir) / "output"
        
        templates = orchestrator.process_templates(
            toml_files=[sample_toml_file],
            output_dir=str(output_dir),
            inheritance_mode='reference'
        )
        
        # Verify templates discovered
        assert len(templates) == 2
        assert "KinkoTechModelBase" in templates
        assert "TimestampMixin" in templates
        
        # Verify template info
        base_template = templates["KinkoTechModelBase"]
        assert base_template.name == "KinkoTechModelBase"
        assert base_template.package == "kinkotech.common.models.base"
        assert base_template.export_path == "kinkotech.common.models.base_sqlalchemy"
        assert len(base_template.columns) == 2
        
        # Verify mixin files generated
        expected_file = (
            output_dir / "kinkotech" / "common" / "models" / "base_sqlalchemy" /
            "kinko_tech_model_base.py"
        )
        assert expected_file.exists()
        
        # Verify file content
        content = expected_file.read_text()
        assert "__abstract__ = True" in content
        assert "class KinkoTechModelBase" in content
        assert "id" in content
        assert "created_at" in content
    
    def test_process_templates_multiple_files_reference_mode(
        self, sample_toml_file, second_toml_file, temp_dir
    ):
        """Test processing templates from multiple files in reference mode."""
        orchestrator = MixinOrchestrator()
        output_dir = Path(temp_dir) / "output"
        
        templates = orchestrator.process_templates(
            toml_files=[sample_toml_file, second_toml_file],
            output_dir=str(output_dir),
            inheritance_mode='reference'
        )
        
        # Verify all templates discovered
        assert len(templates) == 3
        assert "KinkoTechModelBase" in templates
        assert "TimestampMixin" in templates
        assert "SoftDeleteMixin" in templates
        
        # Verify all mixin files generated
        base_file = (
            output_dir / "kinkotech" / "common" / "models" / "base_sqlalchemy" /
            "kinko_tech_model_base.py"
        )
        timestamp_file = (
            output_dir / "kinkotech" / "common" / "models" / "timestamp_sqlalchemy" /
            "timestamp_mixin.py"
        )
        soft_delete_file = (
            output_dir / "kinkotech" / "common" / "models" / "soft_delete_sqlalchemy" /
            "soft_delete_mixin.py"
        )
        
        assert base_file.exists()
        assert timestamp_file.exists()
        assert soft_delete_file.exists()
    
    def test_process_templates_flatten_mode_no_files_generated(
        self, sample_toml_file, temp_dir
    ):
        """Test processing templates in flatten mode doesn't generate files."""
        orchestrator = MixinOrchestrator()
        output_dir = Path(temp_dir) / "output"
        
        templates = orchestrator.process_templates(
            toml_files=[sample_toml_file],
            output_dir=str(output_dir),
            inheritance_mode='flatten'
        )
        
        # Verify templates discovered
        assert len(templates) == 2
        assert "KinkoTechModelBase" in templates
        
        # Verify no mixin files generated
        expected_file = (
            output_dir / "kinkotech" / "common" / "models" / "base_sqlalchemy" /
            "kinko_tech_model_base.py"
        )
        assert not expected_file.exists()
    
    def test_process_templates_invalid_inheritance_mode(
        self, sample_toml_file, temp_dir
    ):
        """Test processing templates with invalid inheritance mode raises error."""
        orchestrator = MixinOrchestrator()
        output_dir = Path(temp_dir) / "output"
        
        with pytest.raises(ValueError) as exc_info:
            orchestrator.process_templates(
                toml_files=[sample_toml_file],
                output_dir=str(output_dir),
                inheritance_mode='invalid'
            )
        
        assert "inheritance_mode must be 'reference' or 'flatten'" in str(exc_info.value)
    
    def test_process_templates_empty_toml_files_list(self, temp_dir):
        """Test processing with empty toml_files list raises error."""
        orchestrator = MixinOrchestrator()
        output_dir = Path(temp_dir) / "output"
        
        with pytest.raises(ValueError) as exc_info:
            orchestrator.process_templates(
                toml_files=[],
                output_dir=str(output_dir),
                inheritance_mode='reference'
            )
        
        assert "toml_files cannot be empty" in str(exc_info.value)
    
    def test_process_templates_invalid_toml_files_type(self, temp_dir):
        """Test processing with invalid toml_files type raises error."""
        orchestrator = MixinOrchestrator()
        output_dir = Path(temp_dir) / "output"
        
        with pytest.raises(ValueError) as exc_info:
            orchestrator.process_templates(
                toml_files="not_a_list",
                output_dir=str(output_dir),
                inheritance_mode='reference'
            )
        
        assert "toml_files must be a list" in str(exc_info.value)
    
    def test_process_templates_empty_output_dir(self, sample_toml_file):
        """Test processing with empty output_dir raises error."""
        orchestrator = MixinOrchestrator()
        
        with pytest.raises(ValueError) as exc_info:
            orchestrator.process_templates(
                toml_files=[sample_toml_file],
                output_dir="",
                inheritance_mode='reference'
            )
        
        assert "output_dir cannot be empty" in str(exc_info.value)
    
    def test_process_templates_nonexistent_toml_file(self, temp_dir):
        """Test processing with nonexistent TOML file raises error."""
        orchestrator = MixinOrchestrator()
        output_dir = Path(temp_dir) / "output"
        
        with pytest.raises(FileNotFoundError):
            orchestrator.process_templates(
                toml_files=["/nonexistent/file.toml"],
                output_dir=str(output_dir),
                inheritance_mode='reference'
            )
    
    def test_process_templates_duplicate_template_names(self, temp_dir):
        """Test processing with duplicate template names raises ConflictError."""
        # Create two files with same template name
        toml1_content = """
[templates.DuplicateTemplate]
package = "pkg1.models"

[[templates.DuplicateTemplate.columns]]
name = "id"
type = "bigint"
"""
        toml2_content = """
[templates.DuplicateTemplate]
package = "pkg2.models"

[[templates.DuplicateTemplate.columns]]
name = "id"
type = "bigint"
"""
        file1 = Path(temp_dir) / "file1.toml"
        file2 = Path(temp_dir) / "file2.toml"
        file1.write_text(toml1_content)
        file2.write_text(toml2_content)
        
        orchestrator = MixinOrchestrator()
        output_dir = Path(temp_dir) / "output"
        
        with pytest.raises(ConflictError) as exc_info:
            orchestrator.process_templates(
                toml_files=[str(file1), str(file2)],
                output_dir=str(output_dir),
                inheritance_mode='reference'
            )
        
        assert "Duplicate template name 'DuplicateTemplate'" in str(exc_info.value)
    
    def test_process_templates_creates_output_directory(
        self, sample_toml_file, temp_dir
    ):
        """Test processing creates output directory if it doesn't exist."""
        orchestrator = MixinOrchestrator()
        output_dir = Path(temp_dir) / "new_output_dir"
        
        # Verify directory doesn't exist
        assert not output_dir.exists()
        
        templates = orchestrator.process_templates(
            toml_files=[sample_toml_file],
            output_dir=str(output_dir),
            inheritance_mode='reference'
        )
        
        # Verify directory created
        assert output_dir.exists()
        assert output_dir.is_dir()
    
    def test_process_templates_output_dir_is_file(
        self, sample_toml_file, temp_dir
    ):
        """Test processing with output_dir as file raises error."""
        orchestrator = MixinOrchestrator()
        output_file = Path(temp_dir) / "output_file.txt"
        output_file.write_text("test")
        
        with pytest.raises(ValueError) as exc_info:
            orchestrator.process_templates(
                toml_files=[sample_toml_file],
                output_dir=str(output_file),
                inheritance_mode='reference'
            )
        
        assert "exists but is not a directory" in str(exc_info.value)
    
    def test_get_template_existing(self, sample_toml_file, temp_dir):
        """Test getting an existing template by name."""
        orchestrator = MixinOrchestrator()
        output_dir = Path(temp_dir) / "output"
        
        # Process templates first
        orchestrator.process_templates(
            toml_files=[sample_toml_file],
            output_dir=str(output_dir),
            inheritance_mode='reference'
        )
        
        # Get template
        template = orchestrator.get_template("KinkoTechModelBase")
        
        assert template.name == "KinkoTechModelBase"
        assert template.package == "kinkotech.common.models.base"
        assert len(template.columns) == 2
    
    def test_get_template_nonexistent(self, sample_toml_file, temp_dir):
        """Test getting a nonexistent template raises error."""
        orchestrator = MixinOrchestrator()
        output_dir = Path(temp_dir) / "output"
        
        # Process templates first
        orchestrator.process_templates(
            toml_files=[sample_toml_file],
            output_dir=str(output_dir),
            inheritance_mode='reference'
        )
        
        # Try to get nonexistent template
        with pytest.raises(TemplateNotFoundError) as exc_info:
            orchestrator.get_template("NonexistentTemplate")
        
        assert "Template 'NonexistentTemplate' not found" in str(exc_info.value)
    
    def test_process_templates_with_explicit_export_path(self, temp_dir):
        """Test processing templates with explicit export_path."""
        toml_content = """
[templates.CustomTemplate]
package = "pkg.models"
export_path = "custom.export.path"

[[templates.CustomTemplate.columns]]
name = "id"
type = "bigint"
"""
        file_path = Path(temp_dir) / "custom.toml"
        file_path.write_text(toml_content)
        
        orchestrator = MixinOrchestrator()
        output_dir = Path(temp_dir) / "output"
        
        templates = orchestrator.process_templates(
            toml_files=[str(file_path)],
            output_dir=str(output_dir),
            inheritance_mode='reference'
        )
        
        # Verify explicit export_path used
        template = templates["CustomTemplate"]
        assert template.export_path == "custom.export.path"
        
        # Verify file generated at correct path
        expected_file = (
            output_dir / "custom" / "export" / "path" / "custom_template.py"
        )
        assert expected_file.exists()
