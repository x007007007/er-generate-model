"""
Bug Condition Exploration Test for Django Inheritance Field Preservation

**Property 1: Fault Condition - Inheritance Field Loss Detection**

**Validates: Requirements 1.1, 1.2, 1.3**

This test MUST FAIL on unfixed code - failure confirms the bug exists.
DO NOT attempt to fix the test or the code when it fails.

The test encodes the expected behavior - it will validate the fix when it passes after implementation.

GOAL: Surface counterexamples that demonstrate inherited fields are missing from generated SQLAlchemy models.

Scoped PBT Approach: Test concrete failing cases with TOML entities that extend templates without export_path.
"""
import re
import pytest
import toml
from hypothesis import given, settings, strategies as st, HealthCheck
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer


# Custom strategies for generating valid identifiers
safe_identifier = st.from_regex(r'[A-Z][a-zA-Z0-9]*', fullmatch=True).filter(lambda s: len(s) < 50)
safe_column_name = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(lambda s: len(s) < 30)
safe_type = st.sampled_from(['string', 'text', 'bigint', 'int', 'datetime', 'boolean'])


@st.composite
def toml_with_template_inheritance(draw):
    """
    Generate TOML data with template inheritance (without export_path).
    
    This strategy creates:
    - A template (mixin) with columns but NO export_path
    - An entity that extends this template
    - The entity has its own columns
    
    Returns a tuple of (toml_dict, template_name, template_columns, entity_name, entity_columns)
    """
    # Generate template name and columns
    template_name = draw(safe_identifier)
    num_template_cols = draw(st.integers(min_value=1, max_value=3))
    
    template_columns = []
    for i in range(num_template_cols):
        col_name = draw(safe_column_name.filter(lambda x: x not in [c['name'] for c in template_columns]))
        col_type = draw(safe_type)
        template_columns.append({
            'name': col_name,
            'type': col_type
        })
    
    # Generate entity name and columns
    entity_name = draw(safe_identifier.filter(lambda x: x != template_name))
    num_entity_cols = draw(st.integers(min_value=1, max_value=2))
    
    entity_columns = []
    for i in range(num_entity_cols):
        col_name = draw(safe_column_name.filter(
            lambda x: x not in [c['name'] for c in entity_columns] and 
                     x not in [c['name'] for c in template_columns]
        ))
        col_type = draw(safe_type)
        entity_columns.append({
            'name': col_name,
            'type': col_type,
            'primary_key': i == 0  # First column is PK
        })
    
    # Build TOML structure
    toml_dict = {
        'templates': {
            template_name: {
                'columns': template_columns
                # NOTE: NO export_path - this triggers the bug
            }
        },
        'entities': {
            entity_name: {
                'extends': [template_name],
                'table_name': entity_name.lower(),
                'columns': entity_columns
            }
        }
    }
    
    return toml_dict, template_name, template_columns, entity_name, entity_columns


class TestProperty1InheritanceFieldLossDetection:
    """
    Property 1: Fault Condition - Inheritance Field Loss Detection
    
    **Validates: Requirements 1.1, 1.2, 1.3**
    
    For any TOML entity with extends field referencing templates without export_path,
    the generated SQLAlchemy model SHALL contain all inherited fields from those templates.
    
    **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(toml_with_template_inheritance())
    def test_inherited_fields_present_in_generated_model(self, test_data):
        """
        Test that inherited fields from templates (without export_path) are present in generated SQLAlchemy models.
        
        This verifies Requirements 1.1, 1.2, 1.3:
        - When TOML entity has extends field referencing templates without export_path
        - Then generated SQLAlchemy model should contain all inherited fields
        - Not just the directly defined fields
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test FAILS
        - Generated models will be missing inherited fields
        - Counterexamples will show which fields are missing
        
        **EXPECTED OUTCOME ON FIXED CODE**: This test PASSES
        - Generated models will contain all inherited fields
        """
        toml_dict, template_name, template_columns, entity_name, entity_columns = test_data
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(er_model)
        
        # Property: Generated model should contain ALL inherited fields from template
        # Check each template column is present in the generated code
        for template_col in template_columns:
            col_name = template_col['name']
            
            # Pattern: {col_name} = Column(
            column_pattern = rf'{re.escape(col_name)}\s*=\s*Column\('
            
            assert re.search(column_pattern, generated_code), (
                f"COUNTEREXAMPLE FOUND: Generated SQLAlchemy model for '{entity_name}' "
                f"is MISSING inherited field '{col_name}' from template '{template_name}'.\n"
                f"Template columns: {[c['name'] for c in template_columns]}\n"
                f"Entity columns: {[c['name'] for c in entity_columns]}\n"
                f"This confirms the bug: inherited fields are lost when templates lack export_path.\n"
                f"Generated code:\n{generated_code}"
            )
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(toml_with_template_inheritance())
    def test_entity_own_fields_also_present(self, test_data):
        """
        Test that entity's own fields are present alongside inherited fields.
        
        This ensures that the fix doesn't break the existing functionality of
        rendering entity's own columns.
        """
        toml_dict, template_name, template_columns, entity_name, entity_columns = test_data
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(er_model)
        
        # Property: Generated model should contain entity's own fields
        for entity_col in entity_columns:
            col_name = entity_col['name']
            column_pattern = rf'{re.escape(col_name)}\s*=\s*Column\('
            
            assert re.search(column_pattern, generated_code), (
                f"Entity's own field '{col_name}' should be present in generated code"
            )
    
    def test_concrete_example_undefined_template_reference(self):
        """
        Concrete test case: Entity extends undefined template (actual bug scenario).
        
        This is the ACTUAL bug from the example file:
        - Entity extends 'CreateModifyMixinModel' 
        - But CreateModifyMixinModel is NOT defined in the [templates] section
        - The parser treats it as an external class and doesn't expand fields
        
        **ROOT CAUSE**: Django parser doesn't export mixin class field definitions to TOML [templates] section
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test documents current behavior
        - Parser correctly treats undefined templates as external classes
        - No fields are expanded (this is correct behavior for undefined templates)
        
        **THE REAL BUG**: Django-to-TOML conversion should detect mixin classes and include
        their field definitions in the [templates] section of the TOML output.
        
        **UPDATE**: Actually, the bug is in the GENERATOR, not Django parser!
        - Parser correctly treats undefined templates as external classes
        - **BUG**: Generator ignores extends field for external classes - no Python inheritance!
        - Expected: class Translation(CreateModifyMixinModel, Base):
        - Actual: class Translation(Base):
        """
        toml_dict = {
            # NO templates section - this matches the actual bug example!
            'entities': {
                'Translation': {
                    'extends': ['kinkotech.common.infrastructure.models.base.CreateModifyMixinModel'],
                    'table_name': 'translation',
                    'columns': [
                        {'name': 'id', 'type': 'bigint', 'primary_key': True},
                        {'name': 'text', 'type': 'string'}
                    ]
                }
            }
        }
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(er_model)
        
        # Verify the entity's own fields are present
        assert re.search(r'id\s*=\s*Column\(', generated_code), (
            "Translation model should have its own 'id' field"
        )
        assert re.search(r'text\s*=\s*Column\(', generated_code), (
            "Translation model should have its own 'text' field"
        )
        
        # **BUG**: These assertions FAIL - generator ignores extends for undefined templates
        # Expected: class Translation(CreateModifyMixinModel, Base):
        # Actual: class Translation(Base):
        assert 'CreateModifyMixinModel' in generated_code, (
            f"COUNTEREXAMPLE FOUND: Generated code is MISSING Python inheritance statement.\n"
            f"Entity extends 'CreateModifyMixinModel' but generated class only inherits from Base.\n"
            f"Expected: class Translation(CreateModifyMixinModel, Base):\n"
            f"Actual: class Translation(Base):\n"
            f"This is the bug: generator ignores extends field for undefined templates.\n"
            f"Generated code:\n{generated_code}"
        )
    
    def test_concrete_example_multiple_mixins(self):
        """
        Concrete test case: Multiple mixin inheritance.
        
        Entity extends multiple templates, all without export_path.
        Expected: All fields from all templates should be present.
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test FAILS
        """
        toml_dict = {
            'templates': {
                'TimestampMixin': {
                    'columns': [
                        {'name': 'created_at', 'type': 'datetime'}
                    ]
                },
                'SoftDeleteMixin': {
                    'columns': [
                        {'name': 'deleted_at', 'type': 'datetime', 'nullable': True}
                    ]
                }
            },
            'entities': {
                'User': {
                    'extends': ['TimestampMixin', 'SoftDeleteMixin'],
                    'table_name': 'user',
                    'columns': [
                        {'name': 'id', 'type': 'bigint', 'primary_key': True},
                        {'name': 'username', 'type': 'string'}
                    ]
                }
            }
        }
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(er_model)
        
        # Check for fields from TimestampMixin
        assert re.search(r'created_at\s*=\s*Column\(', generated_code), (
            "COUNTEREXAMPLE: User model is MISSING 'created_at' field from TimestampMixin.\n"
            f"Generated code:\n{generated_code}"
        )
        
        # Check for fields from SoftDeleteMixin
        assert re.search(r'deleted_at\s*=\s*Column\(', generated_code), (
            "COUNTEREXAMPLE: User model is MISSING 'deleted_at' field from SoftDeleteMixin.\n"
            f"Generated code:\n{generated_code}"
        )
        
        # Check for entity's own fields
        assert re.search(r'id\s*=\s*Column\(', generated_code), (
            "User model should have its own 'id' field"
        )
        assert re.search(r'username\s*=\s*Column\(', generated_code), (
            "User model should have its own 'username' field"
        )
