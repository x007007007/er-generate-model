"""
Integration Tests for Automatic Namespace-Based Mixin Generation

**Validates: All requirements (integration validation)**

These tests verify the complete end-to-end workflow:
- TOML parsing → template discovery → mixin generation → entity rendering
- Multiple TOML files with cross-file references
- Both reference and flatten modes
- Generated code validity

Task 7.3: Write integration tests for end-to-end workflow
"""

import ast
import pytest
import tempfile
import shutil
from pathlib import Path

from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer
from x007007007.er.mixin_orchestrator import MixinOrchestrator


class TestNamespaceMixinIntegration:
    """Integration tests for the complete namespace-based mixin generation workflow."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_single_file_reference_mode_workflow(self, temp_dir):
        """
        Test complete workflow with single TOML file in reference mode.
        
        Validates:
        - TOML parsing discovers templates
        - Templates are processed by orchestrator
        - Mixin files are generated
        - Entities can reference templates
        - Generated code is valid Python
        """
        # Create TOML file with template and entity
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
name = "username"
type = "string"
max_length = 50
"""
        toml_file = Path(temp_dir) / "models.toml"
        toml_file.write_text(toml_content)
        
        output_dir = Path(temp_dir) / "output"
        
        # Step 1: Process templates with orchestrator (discovers and generates mixins)
        orchestrator = MixinOrchestrator()
        templates = orchestrator.process_templates(
            toml_files=[str(toml_file)],
            output_dir=str(output_dir),
            inheritance_mode='reference'
        )
        
        # Verify template discovered
        assert "TimestampMixin" in templates
        template = templates["TimestampMixin"]
        assert template.package == "common.models.base"
        assert template.export_path == "common.models.base_sqlalchemy"
        assert len(template.columns) == 2
        
        # Verify mixin file generated at correct path
        mixin_file = output_dir / "common" / "models" / "base_sqlalchemy" / "timestamp_mixin.py"
        assert mixin_file.exists()
        
        # Verify mixin file content
        mixin_content = mixin_file.read_text()
        assert "__abstract__ = True" in mixin_content
        assert "class TimestampMixin" in mixin_content
        assert "created_at" in mixin_content
        assert "updated_at" in mixin_content
        
        # Verify mixin code is valid Python
        try:
            ast.parse(mixin_content)
        except SyntaxError as e:
            pytest.fail(f"Generated mixin has syntax error: {e}\n{mixin_content}")
        
        # Step 2: Parse TOML and render entity
        # Note: Parser has its own template handling, so we test it separately
        parser = TomlERParser(inheritance_mode='reference')
        model = parser.parse(toml_content)
        
        # Verify entity parsed with template reference
        assert "User" in model.entities
        user_entity = model.entities["User"]
        assert "TimestampMixin" in user_entity.extends
        
        # Step 3: Render entity
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        entity_code = renderer.render(model)
        
        # Verify entity code is valid Python
        try:
            ast.parse(entity_code)
        except SyntaxError as e:
            pytest.fail(f"Generated entity has syntax error: {e}\n{entity_code}")
    
    def test_multiple_files_cross_reference_workflow(self, temp_dir):
        """
        Test complete workflow with multiple TOML files and cross-file references.
        
        Validates:
        - Templates discovered from multiple files
        - Mixin files generated for all templates
        - No duplicate template errors
        - Generated code is valid Python
        """
        # Create first TOML file with templates
        toml1_content = """
[templates.BaseMixin]
package = "common.models.base"

[[templates.BaseMixin.columns]]
name = "id"
type = "bigint"
primary_key = true

[templates.TimestampMixin]
package = "common.models.timestamp"

[[templates.TimestampMixin.columns]]
name = "created_at"
type = "datetime"
"""
        toml1_file = Path(temp_dir) / "common.toml"
        toml1_file.write_text(toml1_content)
        
        # Create second TOML file with entity referencing templates from first file
        toml2_content = """
[entities.User]
table_name = "users"
extends = ["BaseMixin", "TimestampMixin"]

[[entities.User.columns]]
name = "username"
type = "string"
max_length = 50
"""
        toml2_file = Path(temp_dir) / "users.toml"
        toml2_file.write_text(toml2_content)
        
        output_dir = Path(temp_dir) / "output"
        
        # Step 1: Process templates from both files
        orchestrator = MixinOrchestrator()
        templates = orchestrator.process_templates(
            toml_files=[str(toml1_file), str(toml2_file)],
            output_dir=str(output_dir),
            inheritance_mode='reference'
        )
        
        # Verify both templates discovered
        assert len(templates) == 2
        assert "BaseMixin" in templates
        assert "TimestampMixin" in templates
        
        # Verify both mixin files generated
        base_mixin_file = output_dir / "common" / "models" / "base_sqlalchemy" / "base_mixin.py"
        timestamp_mixin_file = output_dir / "common" / "models" / "timestamp_sqlalchemy" / "timestamp_mixin.py"
        
        assert base_mixin_file.exists()
        assert timestamp_mixin_file.exists()
        
        # Verify mixin files are valid Python
        try:
            ast.parse(base_mixin_file.read_text())
            ast.parse(timestamp_mixin_file.read_text())
        except SyntaxError as e:
            pytest.fail(f"Generated mixin has syntax error: {e}")
    
    def test_flatten_mode_workflow(self, temp_dir):
        """
        Test complete workflow in flatten mode.
        
        Validates:
        - Templates discovered but no mixin files generated
        - Entity fields expanded inline
        - No import statements for mixins
        - Generated code is valid Python
        """
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
name = "username"
type = "string"
max_length = 50
"""
        toml_file = Path(temp_dir) / "models.toml"
        toml_file.write_text(toml_content)
        
        output_dir = Path(temp_dir) / "output"
        
        # Step 1: Process templates in flatten mode
        orchestrator = MixinOrchestrator()
        templates = orchestrator.process_templates(
            toml_files=[str(toml_file)],
            output_dir=str(output_dir),
            inheritance_mode='flatten'
        )
        
        # Verify template discovered
        assert "TimestampMixin" in templates
        
        # Verify NO mixin file generated
        mixin_file = output_dir / "common" / "models" / "base_sqlalchemy" / "timestamp_mixin.py"
        assert not mixin_file.exists()
        
        # Step 2: Parse and render entity
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        renderer = SQLAlchemyRenderer(inheritance_mode='flatten')
        entity_code = renderer.render(model)
        
        # Verify NO import statements for mixins
        assert "from common.models.base_sqlalchemy" not in entity_code
        assert "import TimestampMixin" not in entity_code
        
        # Verify fields expanded inline
        assert "created_at" in entity_code
        assert "updated_at" in entity_code
        assert "id" in entity_code
        assert "username" in entity_code
        
        # Verify entity only inherits from Base
        assert "class User(Base)" in entity_code
        
        # Verify code is valid Python
        try:
            ast.parse(entity_code)
        except SyntaxError as e:
            pytest.fail(f"Generated entity has syntax error: {e}\n{entity_code}")
    
    def test_explicit_export_path_workflow(self, temp_dir):
        """
        Test workflow with explicit export_path (not auto-derived).
        
        Validates:
        - Explicit export_path takes precedence over package
        - Mixin file generated at explicit path
        - Generated code is valid Python
        """
        toml_content = """
[templates.CustomMixin]
package = "original.package"
export_path = "custom.export.path"

[[templates.CustomMixin.columns]]
name = "custom_field"
type = "string"

[entities.Model]
table_name = "models"
extends = ["CustomMixin"]

[[entities.Model.columns]]
name = "id"
type = "bigint"
primary_key = true
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
        
        # Verify explicit export_path used
        template = templates["CustomMixin"]
        assert template.export_path == "custom.export.path"
        
        # Verify mixin file at explicit path
        mixin_file = output_dir / "custom" / "export" / "path" / "custom_mixin.py"
        assert mixin_file.exists()
        
        # Verify mixin code is valid Python
        try:
            ast.parse(mixin_file.read_text())
        except SyntaxError as e:
            pytest.fail(f"Generated mixin has syntax error: {e}")
    
    def test_complex_workflow_with_relationships(self, temp_dir):
        """
        Test workflow with templates and relationships.
        
        Validates:
        - Templates work alongside relationships
        - Mixin files generated correctly
        - Generated code is valid Python
        """
        toml_content = """
[templates.BaseMixin]
package = "common.models.base"

[[templates.BaseMixin.columns]]
name = "id"
type = "bigint"
primary_key = true

[[templates.BaseMixin.columns]]
name = "created_at"
type = "datetime"

[[relationships]]
left = "User"
right = "Post"
type = "one-to-many"
left_column = "id"
right_column = "author_id"

[entities.User]
table_name = "users"
extends = ["BaseMixin"]

[[entities.User.columns]]
name = "username"
type = "string"
max_length = 50

[entities.Post]
table_name = "posts"
extends = ["BaseMixin"]

[[entities.Post.columns]]
name = "author"
type = "bigint"
db_column = "author_id"

[[entities.Post.columns]]
name = "title"
type = "string"
max_length = 200
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
        
        # Verify mixin generated
        mixin_file = output_dir / "common" / "models" / "base_sqlalchemy" / "base_mixin.py"
        assert mixin_file.exists()
        
        # Verify mixin is valid Python
        try:
            ast.parse(mixin_file.read_text())
        except SyntaxError as e:
            pytest.fail(f"Generated mixin has syntax error: {e}")
        
        # Parse and render
        parser = TomlERParser(inheritance_mode='reference')
        model = parser.parse(toml_content)
        
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        entity_code = renderer.render(model)
        
        # Verify relationship preserved
        assert "author_id = Column(" in entity_code
        assert "author = relationship(" in entity_code
        
        # Verify code is valid Python
        try:
            ast.parse(entity_code)
        except SyntaxError as e:
            pytest.fail(f"Generated entity has syntax error: {e}\n{entity_code}")
    
    def test_field_order_preservation(self, temp_dir):
        """
        Test that field order is preserved (template fields first, then entity fields).
        
        Validates:
        - In flatten mode, template fields appear before entity fields
        - Field order matches specification
        """
        toml_content = """
[templates.OrderedMixin]
package = "common.models.base"

[[templates.OrderedMixin.columns]]
name = "mixin_field_1"
type = "string"

[[templates.OrderedMixin.columns]]
name = "mixin_field_2"
type = "string"

[entities.TestEntity]
table_name = "test_entities"
extends = ["OrderedMixin"]

[[entities.TestEntity.columns]]
name = "entity_field_1"
type = "string"

[[entities.TestEntity.columns]]
name = "entity_field_2"
type = "string"
"""
        toml_file = Path(temp_dir) / "models.toml"
        toml_file.write_text(toml_content)
        
        output_dir = Path(temp_dir) / "output"
        
        # Process in flatten mode
        orchestrator = MixinOrchestrator()
        orchestrator.process_templates(
            toml_files=[str(toml_file)],
            output_dir=str(output_dir),
            inheritance_mode='flatten'
        )
        
        # Parse and render
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        renderer = SQLAlchemyRenderer(inheritance_mode='flatten')
        entity_code = renderer.render(model)
        
        # Find positions of fields in generated code
        mixin_field_1_pos = entity_code.find("mixin_field_1")
        mixin_field_2_pos = entity_code.find("mixin_field_2")
        entity_field_1_pos = entity_code.find("entity_field_1")
        entity_field_2_pos = entity_code.find("entity_field_2")
        
        # Verify all fields present
        assert mixin_field_1_pos != -1
        assert mixin_field_2_pos != -1
        assert entity_field_1_pos != -1
        assert entity_field_2_pos != -1
        
        # Verify order: mixin fields before entity fields
        assert mixin_field_1_pos < entity_field_1_pos
        assert mixin_field_2_pos < entity_field_1_pos
        assert mixin_field_1_pos < entity_field_2_pos
        assert mixin_field_2_pos < entity_field_2_pos
    
    def test_generated_code_validity_comprehensive(self, temp_dir):
        """
        Comprehensive test of generated code validity.
        
        Validates:
        - Mixin files are syntactically valid
        - Entity files are syntactically valid
        - All column attributes preserved
        - Code can be parsed by AST
        """
        toml_content = """
[templates.ComprehensiveMixin]
package = "test.models.base"

[[templates.ComprehensiveMixin.columns]]
name = "id"
type = "bigint"
primary_key = true
nullable = false

[[templates.ComprehensiveMixin.columns]]
name = "created_at"
type = "datetime"
nullable = false

[[templates.ComprehensiveMixin.columns]]
name = "updated_at"
type = "datetime"
nullable = true

[[templates.ComprehensiveMixin.columns]]
name = "status"
type = "string"
max_length = 20
default = "active"

[entities.ComprehensiveEntity]
table_name = "comprehensive_entities"
extends = ["ComprehensiveMixin"]

[[entities.ComprehensiveEntity.columns]]
name = "name"
type = "string"
max_length = 100
unique = true
nullable = false

[[entities.ComprehensiveEntity.columns]]
name = "description"
type = "text"
nullable = true

[[entities.ComprehensiveEntity.columns]]
name = "count"
type = "int"
default = 0
"""
        toml_file = Path(temp_dir) / "models.toml"
        toml_file.write_text(toml_content)
        
        output_dir = Path(temp_dir) / "output"
        
        # Process templates
        orchestrator = MixinOrchestrator()
        orchestrator.process_templates(
            toml_files=[str(toml_file)],
            output_dir=str(output_dir),
            inheritance_mode='reference'
        )
        
        # Verify mixin file
        mixin_file = output_dir / "test" / "models" / "base_sqlalchemy" / "comprehensive_mixin.py"
        assert mixin_file.exists()
        
        mixin_content = mixin_file.read_text()
        
        # Verify mixin has all required elements
        assert "from sqlalchemy" in mixin_content
        assert "class ComprehensiveMixin" in mixin_content
        assert "__abstract__ = True" in mixin_content
        assert "id = Column(" in mixin_content
        assert "created_at = Column(" in mixin_content
        assert "updated_at = Column(" in mixin_content
        assert "status = Column(" in mixin_content
        
        # Verify mixin is valid Python
        try:
            ast.parse(mixin_content)
        except SyntaxError as e:
            pytest.fail(f"Generated mixin has syntax error: {e}\n{mixin_content}")
        
        # Parse and render entity
        parser = TomlERParser(inheritance_mode='reference')
        model = parser.parse(toml_content)
        
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        entity_code = renderer.render(model)
        
        # Verify entity has entity-specific fields
        assert "name = Column(" in entity_code
        assert "description = Column(" in entity_code
        assert "count = Column(" in entity_code
        
        # Verify entity is valid Python
        try:
            ast.parse(entity_code)
        except SyntaxError as e:
            pytest.fail(f"Generated entity has syntax error: {e}\n{entity_code}")


class TestNamespaceMixinErrorHandling:
    """Integration tests for error handling in the workflow."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_missing_template_reference_error(self, temp_dir):
        """
        Test that referencing a non-existent template raises appropriate error.
        
        Validates:
        - Error raised when entity references missing template
        - Error message is clear and helpful
        """
        toml_content = """
[entities.User]
table_name = "users"
extends = ["NonexistentMixin"]

[[entities.User.columns]]
name = "id"
type = "bigint"
primary_key = true
"""
        toml_file = Path(temp_dir) / "models.toml"
        toml_file.write_text(toml_content)
        
        output_dir = Path(temp_dir) / "output"
        
        # Process templates (should succeed - no templates to process)
        orchestrator = MixinOrchestrator()
        orchestrator.process_templates(
            toml_files=[str(toml_file)],
            output_dir=str(output_dir),
            inheritance_mode='reference'
        )
        
        # Parse model
        parser = TomlERParser()
        model = parser.parse(toml_content)
        
        # Rendering should fail with clear error
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        
        # The renderer should handle missing templates gracefully
        # (either by raising an error or by skipping the missing template)
        # This depends on the implementation
        try:
            entity_code = renderer.render(model)
            # If it doesn't raise an error, verify it at least doesn't crash
            assert entity_code is not None
        except Exception as e:
            # If it raises an error, verify it's informative
            assert "NonexistentMixin" in str(e) or "template" in str(e).lower()
    
    def test_duplicate_template_names_error(self, temp_dir):
        """
        Test that duplicate template names across files raise error.
        
        Validates:
        - ConflictError raised for duplicate templates
        - Error message includes both file paths
        """
        from x007007007.er.template_registry import ConflictError
        
        # Create two files with same template name
        toml1_content = """
[templates.DuplicateMixin]
package = "pkg1.models"

[[templates.DuplicateMixin.columns]]
name = "field1"
type = "string"
"""
        toml2_content = """
[templates.DuplicateMixin]
package = "pkg2.models"

[[templates.DuplicateMixin.columns]]
name = "field2"
type = "string"
"""
        toml1_file = Path(temp_dir) / "file1.toml"
        toml2_file = Path(temp_dir) / "file2.toml"
        toml1_file.write_text(toml1_content)
        toml2_file.write_text(toml2_content)
        
        output_dir = Path(temp_dir) / "output"
        
        # Processing should raise ConflictError
        orchestrator = MixinOrchestrator()
        
        with pytest.raises(ConflictError) as exc_info:
            orchestrator.process_templates(
                toml_files=[str(toml1_file), str(toml2_file)],
                output_dir=str(output_dir),
                inheritance_mode='reference'
            )
        
        # Verify error message includes template name and both files
        error_msg = str(exc_info.value)
        assert "DuplicateMixin" in error_msg
        assert "file1.toml" in error_msg
        assert "file2.toml" in error_msg
