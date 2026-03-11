"""
Integration tests for CLI with MixinOrchestrator.

Tests that the convert command properly integrates with MixinOrchestrator
to process templates and generate mixin files.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from click.testing import CliRunner

from x007007007.er_tool.convert import convert_cmd


class TestCLIMixinIntegration:
    """Test suite for CLI integration with MixinOrchestrator."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_toml_with_templates(self, temp_dir):
        """Create a sample TOML file with templates."""
        toml_content = """
[templates.TimestampMixin]
package = "common.models.base"

[[templates.TimestampMixin.columns]]
name = "created_at"
type = "datetime"
nullable = false

[[templates.TimestampMixin.columns]]
name = "updated_at"
type = "datetime"
nullable = false

[entities.User]
table_name = "users"
extends = ["TimestampMixin"]

[[entities.User.columns]]
name = "id"
type = "bigint"
primary_key = true

[[entities.User.columns]]
name = "email"
type = "string"
max_length = 255
"""
        file_path = Path(temp_dir) / "models.toml"
        file_path.write_text(toml_content)
        return str(file_path)
    
    def test_convert_toml_with_templates_reference_mode(
        self, sample_toml_with_templates, temp_dir
    ):
        """Test convert command with TOML templates in reference mode."""
        runner = CliRunner()
        output_dir = Path(temp_dir) / "output"
        
        result = runner.invoke(convert_cmd, [
            sample_toml_with_templates,
            '--input-type', 'toml',
            '--format', 'sqlalchemy',
            '--output-dir', str(output_dir),
            '--inheritance-mode', 'reference'
        ])
        
        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        
        # Verify output directory was created
        assert output_dir.exists(), "Output directory should be created"
        
        # Verify mixin file was generated
        mixin_file = output_dir / "common" / "models" / "base_sqlalchemy" / "timestamp_mixin.py"
        assert mixin_file.exists(), f"Mixin file should be generated at {mixin_file}"
        
        # Verify mixin file contains expected content
        mixin_content = mixin_file.read_text()
        assert "class TimestampMixin" in mixin_content
        assert "__abstract__ = True" in mixin_content
        assert "created_at" in mixin_content
        assert "updated_at" in mixin_content
        
        # Verify entity file was generated
        entity_file = output_dir / "user.py"
        assert entity_file.exists(), "Entity file should be generated"
        
        # Verify entity imports the mixin
        entity_content = entity_file.read_text()
        assert "from common.models.base_sqlalchemy.timestamp_mixin import TimestampMixin" in entity_content
        assert "class User" in entity_content
    
    def test_convert_toml_with_templates_flatten_mode(
        self, sample_toml_with_templates, temp_dir
    ):
        """Test convert command with TOML templates in flatten mode."""
        runner = CliRunner()
        output_dir = Path(temp_dir) / "output"
        
        result = runner.invoke(convert_cmd, [
            sample_toml_with_templates,
            '--input-type', 'toml',
            '--format', 'sqlalchemy',
            '--output-dir', str(output_dir),
            '--inheritance-mode', 'flatten'
        ])
        
        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        
        # Verify output directory was created
        assert output_dir.exists(), "Output directory should be created"
        
        # In flatten mode, no mixin files should be generated
        mixin_dir = output_dir / "common"
        assert not mixin_dir.exists(), "No mixin directory should be created in flatten mode"
        
        # Verify entity file was generated
        entity_file = output_dir / "user.py"
        assert entity_file.exists(), "Entity file should be generated"
        
        # Verify entity has expanded fields (not imports)
        entity_content = entity_file.read_text()
        assert "created_at" in entity_content
        assert "updated_at" in entity_content
        # Should not import mixin in flatten mode
        assert "import TimestampMixin" not in entity_content
    
    def test_convert_toml_without_output_dir_skips_mixin_generation(
        self, sample_toml_with_templates, temp_dir
    ):
        """Test that mixin generation is skipped when no output directory is specified."""
        runner = CliRunner()
        output_file = Path(temp_dir) / "output.py"
        
        result = runner.invoke(convert_cmd, [
            sample_toml_with_templates,
            '--input-type', 'toml',
            '--format', 'sqlalchemy',
            '--output', str(output_file),
            '--inheritance-mode', 'reference'
        ])
        
        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        
        # Verify output file was created
        assert output_file.exists(), "Output file should be created"
        
        # Verify no mixin directory was created (single file output)
        mixin_dir = Path(temp_dir) / "common"
        assert not mixin_dir.exists(), "No mixin directory should be created for single file output"
    
    def test_convert_toml_multiple_files_with_cross_references(self, temp_dir):
        """Test convert command with multiple TOML files and cross-file template references."""
        # Create first TOML file with template
        toml1_content = """
[templates.BaseMixin]
package = "common.models.base"

[[templates.BaseMixin.columns]]
name = "id"
type = "bigint"
primary_key = true
"""
        toml1_path = Path(temp_dir) / "base.toml"
        toml1_path.write_text(toml1_content)
        
        # Create second TOML file that references the template
        toml2_content = """
[entities.User]
table_name = "users"
extends = ["BaseMixin"]

[[entities.User.columns]]
name = "email"
type = "string"
max_length = 255
"""
        toml2_path = Path(temp_dir) / "models.toml"
        toml2_path.write_text(toml2_content)
        
        runner = CliRunner()
        output_dir = Path(temp_dir) / "output"
        
        result = runner.invoke(convert_cmd, [
            str(toml2_path),
            '--input-type', 'toml',
            '--format', 'sqlalchemy',
            '--output-dir', str(output_dir),
            '--inheritance-mode', 'reference',
            '--toml-files', str(toml1_path)
        ])
        
        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        
        # Verify mixin file was generated from first TOML
        mixin_file = output_dir / "common" / "models" / "base_sqlalchemy" / "base_mixin.py"
        assert mixin_file.exists(), "Mixin file should be generated from cross-referenced template"
        
        # Verify entity file references the mixin
        entity_file = output_dir / "user.py"
        assert entity_file.exists(), "Entity file should be generated"
        entity_content = entity_file.read_text()
        assert "from common.models.base_sqlalchemy.base_mixin import BaseMixin" in entity_content
