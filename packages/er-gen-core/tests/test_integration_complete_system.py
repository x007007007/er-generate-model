"""
Integration Tests for Complete System - Task 9.3

**Validates: All requirements**

These tests verify the complete end-to-end system with real TOML files.
"""

import ast
import sys
import pytest
import tempfile
import shutil
from pathlib import Path

from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer
from x007007007.er.mixin_orchestrator import MixinOrchestrator


class TestCompleteSystemIntegration:
    """Integration tests for complete system with real TOML files."""
    
    @pytest.fixture
    def temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_single_file_end_to_end(self, temp_dir):
        """Test complete end-to-end workflow with single TOML file."""
        toml_content = """
[templates.TimestampMixin]
package = "myapp.models.base"

[[templates.TimestampMixin.columns]]
name = "created_at"
type = "datetime"

[[templates.TimestampMixin.columns]]
name = "updated_at"
type = "datetime"

[entities.USER]
table_name = "users"
extends = ["TimestampMixin"]
columns = [
    {name = "id", type = "uuid", is_pk = true},
    {name = "username", type = "string", unique = true},
]
"""
        toml_file = Path(temp_dir) / "models.toml"
        toml_file.write_text(toml_content)
        output_dir = Path(temp_dir) / "output"
        
        # Process templates
        orchestrator = MixinOrchestrator()
        templates = orchestrator.process_templates(
            toml_files=[str(toml_file)],
            output_dir=str(output_dir),
            inheritance_mode='reference'
        )
        
        # Verify template discovered
        assert "TimestampMixin" in templates
        
        # Verify mixin file generated
        mixin_file = output_dir / "myapp" / "models" / "base_sqlalchemy" / "timestamp_mixin.py"
        assert mixin_file.exists(), f"Mixin file not found: {mixin_file}"
        
        # Verify mixin content
        mixin_content = mixin_file.read_text()
        assert "__abstract__ = True" in mixin_content
        assert "class TimestampMixin" in mixin_content
        assert "created_at" in mixin_content
        assert "updated_at" in mixin_content
        
        # Verify mixin is valid Python
        try:
            ast.parse(mixin_content)
        except SyntaxError as e:
            pytest.fail(f"Mixin syntax error: {e}")
        
        # Parse and render entity
        parser = TomlERParser(inheritance_mode='reference')
        model = parser.parse(toml_content)
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        entity_code = renderer.render(model)
        
        # Verify entity code is valid Python
        try:
            ast.parse(entity_code)
        except SyntaxError as e:
            pytest.fail(f"Entity syntax error: {e}")
    
    def test_multi_file_cross_reference(self, temp_dir):
        """Test multi-file scenario with cross-file template references."""
        base_content = """
[templates.AuditMixin]
package = "company.common.models.base"

[[templates.AuditMixin.columns]]
name = "created_at"
type = "datetime"

[[templates.AuditMixin.columns]]
name = "updated_at"
type = "datetime"
"""
        entities_content = """
[entities.PRODUCT]
table_name = "products"
extends = ["AuditMixin"]
columns = [
    {name = "id", type = "uuid", is_pk = true},
    {name = "name", type = "string"},
]
"""
        base_file = Path(temp_dir) / "base.toml"
        entities_file = Path(temp_dir) / "entities.toml"
        base_file.write_text(base_content)
        entities_file.write_text(entities_content)
        output_dir = Path(temp_dir) / "output"
        
        # Process templates from both files
        orchestrator = MixinOrchestrator()
        templates = orchestrator.process_templates(
            toml_files=[str(base_file), str(entities_file)],
            output_dir=str(output_dir),
            inheritance_mode='reference'
        )
        
        # Verify template discovered
        assert "AuditMixin" in templates
        
        # Verify mixin file generated
        mixin_file = output_dir / "company" / "common" / "models" / "base_sqlalchemy" / "audit_mixin.py"
        assert mixin_file.exists()
        
        # Verify mixin is valid Python
        try:
            ast.parse(mixin_file.read_text())
        except SyntaxError as e:
            pytest.fail(f"Mixin syntax error: {e}")
    
    def test_explicit_export_path(self, temp_dir):
        """Test templates with explicit export paths."""
        toml_content = """
[templates.CustomMixin]
package = "myapp.models.base"
export_path = "myapp.custom.mixins"

[[templates.CustomMixin.columns]]
name = "status"
type = "string"

[entities.TASK]
table_name = "tasks"
extends = ["CustomMixin"]
columns = [
    {name = "id", type = "bigint", is_pk = true},
]
"""
        toml_file = Path(temp_dir) / "models.toml"
        toml_file.write_text(toml_content)
        output_dir = Path(temp_dir) / "output"
        
        orchestrator = MixinOrchestrator()
        templates = orchestrator.process_templates(
            toml_files=[str(toml_file)],
            output_dir=str(output_dir),
            inheritance_mode='reference'
        )
        
        # Verify explicit export_path used
        assert templates["CustomMixin"].export_path == "myapp.custom.mixins"
        
        # Verify mixin file at explicit path
        mixin_file = output_dir / "myapp" / "custom" / "mixins" / "custom_mixin.py"
        assert mixin_file.exists()
        
        try:
            ast.parse(mixin_file.read_text())
        except SyntaxError as e:
            pytest.fail(f"Mixin syntax error: {e}")
    
    def test_flatten_mode(self, temp_dir):
        """Test flatten mode where no mixin files are generated."""
        toml_content = """
[templates.BaseMixin]
package = "app.models.base"

[[templates.BaseMixin.columns]]
name = "id"
type = "bigint"
is_pk = true

[entities.DOCUMENT]
table_name = "documents"
extends = ["BaseMixin"]
columns = [
    {name = "title", type = "string"},
]
"""
        toml_file = Path(temp_dir) / "models.toml"
        toml_file.write_text(toml_content)
        output_dir = Path(temp_dir) / "output"
        
        orchestrator = MixinOrchestrator()
        templates = orchestrator.process_templates(
            toml_files=[str(toml_file)],
            output_dir=str(output_dir),
            inheritance_mode='flatten'
        )
        
        # Verify template discovered
        assert "BaseMixin" in templates
        
        # Verify NO mixin file generated in flatten mode
        mixin_file = output_dir / "app" / "models" / "base_sqlalchemy" / "base_mixin.py"
        assert not mixin_file.exists()
        
        # Parse and render entity
        parser = TomlERParser()
        model = parser.parse(toml_content)
        renderer = SQLAlchemyRenderer(inheritance_mode='flatten')
        entity_code = renderer.render(model)
        
        # Verify no imports for mixins
        assert "from app.models.base_sqlalchemy" not in entity_code
        
        # Verify fields expanded inline
        assert "id" in entity_code
        assert "title" in entity_code
        
        try:
            ast.parse(entity_code)
        except SyntaxError as e:
            pytest.fail(f"Entity syntax error: {e}")
    
    def test_generated_code_importability(self, temp_dir):
        """Test that generated mixin code can be imported."""
        toml_content = """
[templates.ImportTestMixin]
package = "test.models.base"

[[templates.ImportTestMixin.columns]]
name = "test_id"
type = "bigint"
is_pk = true

[entities.TESTENTITY]
table_name = "test_entities"
extends = ["ImportTestMixin"]
columns = [
    {name = "name", type = "string"},
]
"""
        toml_file = Path(temp_dir) / "models.toml"
        toml_file.write_text(toml_content)
        output_dir = Path(temp_dir) / "output"
        
        orchestrator = MixinOrchestrator()
        orchestrator.process_templates(
            toml_files=[str(toml_file)],
            output_dir=str(output_dir),
            inheritance_mode='reference'
        )
        
        mixin_file = output_dir / "test" / "models" / "base_sqlalchemy" / "import_test_mixin.py"
        assert mixin_file.exists()
        
        # Create package structure
        (output_dir / "test").mkdir(parents=True, exist_ok=True)
        (output_dir / "test" / "__init__.py").touch()
        (output_dir / "test" / "models").mkdir(parents=True, exist_ok=True)
        (output_dir / "test" / "models" / "__init__.py").touch()
        (output_dir / "test" / "models" / "base_sqlalchemy").mkdir(parents=True, exist_ok=True)
        (output_dir / "test" / "models" / "base_sqlalchemy" / "__init__.py").touch()
        
        # Try to import the generated mixin
        sys.path.insert(0, str(output_dir))
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("import_test_mixin", mixin_file)
            mixin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mixin_module)
            
            # Verify the mixin class exists and has expected attributes
            assert hasattr(mixin_module, 'ImportTestMixin')
            assert hasattr(mixin_module.ImportTestMixin, '__abstract__')
            assert mixin_module.ImportTestMixin.__abstract__ is True
        except Exception as e:
            pytest.fail(f"Import failed: {e}")
        finally:
            sys.path.remove(str(output_dir))
    
    def test_complex_scenario_with_relationships(self, temp_dir):
        """Test complex scenario with templates and relationships."""
        base_content = """
[templates.AuditMixin]
package = "company.models.base"

[[templates.AuditMixin.columns]]
name = "created_at"
type = "datetime"
"""
        entities_content = """
[entities.USER]
table_name = "users"
extends = ["AuditMixin"]
columns = [
    {name = "id", type = "bigint", is_pk = true},
    {name = "username", type = "string"},
]

[entities.POST]
table_name = "posts"
extends = ["AuditMixin"]
columns = [
    {name = "id", type = "bigint", is_pk = true},
    {name = "author", type = "bigint", is_fk = true, db_column = "author_id"},
    {name = "title", type = "string"},
]

[[relationships]]
left = "USER"
right = "POST"
type = "one-to-many"
right_column = "author_id"
"""
        base_file = Path(temp_dir) / "base.toml"
        entities_file = Path(temp_dir) / "entities.toml"
        base_file.write_text(base_content)
        entities_file.write_text(entities_content)
        output_dir = Path(temp_dir) / "output"
        
        orchestrator = MixinOrchestrator()
        templates = orchestrator.process_templates(
            toml_files=[str(base_file), str(entities_file)],
            output_dir=str(output_dir),
            inheritance_mode='reference'
        )
        
        # Verify template and mixin file
        assert "AuditMixin" in templates
        mixin_file = output_dir / "company" / "models" / "base_sqlalchemy" / "audit_mixin.py"
        assert mixin_file.exists()
        
        try:
            ast.parse(mixin_file.read_text())
        except SyntaxError as e:
            pytest.fail(f"Mixin syntax error: {e}")
        
        # Parse and render entities
        parser = TomlERParser(inheritance_mode='reference')
        model = parser.parse(entities_content)
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        entity_code = renderer.render(model)
        
        # Verify relationship preserved
        assert "author_id" in entity_code
        
        try:
            ast.parse(entity_code)
        except SyntaxError as e:
            pytest.fail(f"Entity syntax error: {e}")
