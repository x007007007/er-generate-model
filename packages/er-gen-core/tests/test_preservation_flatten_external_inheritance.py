"""
Preservation Property Tests for SQLAlchemy Flatten Mode External Inheritance Fix

**Property 2: Preservation - Reference Mode and Non-Buggy Cases**

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

These tests MUST PASS on unfixed code - they verify baseline behavior to preserve.

GOAL: Observe and document behavior on UNFIXED code for non-buggy inputs (reference mode,
internal templates, no inheritance) to ensure the fix doesn't break existing functionality.

Property-based testing generates many test cases for stronger guarantees.
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
def toml_with_external_class_reference_mode(draw):
    """
    Generate TOML data with external class inheritance for reference mode.
    
    Returns a tuple of (toml_dict, entity_name, external_classes, entity_columns)
    """
    entity_name = draw(safe_identifier)
    num_entity_cols = draw(st.integers(min_value=1, max_value=3))
    
    entity_columns = []
    for i in range(num_entity_cols):
        col_name = draw(safe_column_name.filter(lambda x: x not in [c['name'] for c in entity_columns]))
        col_type = draw(safe_type)
        entity_columns.append({
            'name': col_name,
            'type': col_type,
            'primary_key': i == 0
        })
    
    num_external = draw(st.integers(min_value=1, max_value=2))
    external_classes = []
    for i in range(num_external):
        class_name = draw(safe_identifier.filter(lambda x: x not in external_classes and x != entity_name))
        external_class = f"kinkotech.common.infrastructure.models.base.{class_name}"
        external_classes.append(external_class)
    
    toml_dict = {
        'entities': {
            entity_name: {
                'extends': external_classes,
                'table_name': entity_name.lower(),
                'columns': entity_columns
            }
        }
    }
    
    return toml_dict, entity_name, external_classes, entity_columns


@st.composite
def toml_with_internal_template(draw):
    """
    Generate TOML data with internal template inheritance.
    
    Returns a tuple of (toml_dict, template_name, template_columns, entity_name, entity_columns, has_export_path)
    """
    template_name = draw(safe_identifier)
    num_template_cols = draw(st.integers(min_value=1, max_value=2))
    
    template_columns = []
    for i in range(num_template_cols):
        col_name = draw(safe_column_name.filter(lambda x: x not in [c['name'] for c in template_columns]))
        col_type = draw(safe_type)
        template_columns.append({
            'name': col_name,
            'type': col_type
        })
    
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
            'primary_key': i == 0
        })
    
    # Randomly decide if template has export_path
    has_export_path = draw(st.booleans())
    
    template_def = {'columns': template_columns}
    if has_export_path:
        template_def['export_path'] = f"myapp.mixins.{template_name.lower()}"
    
    toml_dict = {
        'templates': {
            template_name: template_def
        },
        'entities': {
            entity_name: {
                'extends': [template_name],
                'table_name': entity_name.lower(),
                'columns': entity_columns
            }
        }
    }
    
    return toml_dict, template_name, template_columns, entity_name, entity_columns, has_export_path


@st.composite
def toml_without_inheritance(draw):
    """
    Generate TOML data without any inheritance.
    
    Returns a tuple of (toml_dict, entity_name, entity_columns)
    """
    entity_name = draw(safe_identifier)
    num_entity_cols = draw(st.integers(min_value=1, max_value=3))
    
    entity_columns = []
    for i in range(num_entity_cols):
        col_name = draw(safe_column_name.filter(lambda x: x not in [c['name'] for c in entity_columns]))
        col_type = draw(safe_type)
        entity_columns.append({
            'name': col_name,
            'type': col_type,
            'primary_key': i == 0
        })
    
    toml_dict = {
        'entities': {
            entity_name: {
                'table_name': entity_name.lower(),
                'columns': entity_columns
            }
        }
    }
    
    return toml_dict, entity_name, entity_columns


class TestProperty2PreservationReferenceModeAndNonBuggyCases:
    """
    Property 2: Preservation - Reference Mode and Non-Buggy Cases
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
    
    These tests verify that the fix doesn't break existing functionality:
    - Reference mode with external classes should continue to import and inherit
    - Internal template handling should remain unchanged
    - No inheritance cases should continue to work
    
    **CRITICAL**: These tests MUST PASS on unfixed code - they document baseline behavior.
    """
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(toml_with_external_class_reference_mode())
    def test_reference_mode_external_classes_imported(self, test_data):
        """
        Test that external classes ARE imported in reference mode.
        
        This verifies Requirement 3.1:
        - When using reference mode with external classes
        - Then system SHALL continue to import external classes
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test PASSES
        - This is the baseline behavior to preserve
        
        **EXPECTED OUTCOME ON FIXED CODE**: This test PASSES
        - Reference mode behavior should remain unchanged
        """
        toml_dict, entity_name, external_classes, entity_columns = test_data
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code with reference mode
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        generated_code = renderer.render(er_model)
        
        # Property: Generated code SHOULD import external classes in reference mode
        for external_class in external_classes:
            parts = external_class.rsplit('.', 1)
            if len(parts) == 2:
                module_path = parts[0]
                class_name = parts[1]
                
                # Check that import statement IS present
                import_pattern = rf'from\s+{re.escape(module_path)}\s+import\s+.*{re.escape(class_name)}'
                
                assert re.search(import_pattern, generated_code), (
                    f"PRESERVATION VIOLATION: Reference mode should import external class '{class_name}'.\n"
                    f"This is existing behavior that must be preserved.\n"
                    f"Generated code:\n{generated_code}"
                )
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(toml_with_external_class_reference_mode())
    def test_reference_mode_external_classes_inherited(self, test_data):
        """
        Test that external classes ARE in the inheritance list in reference mode.
        
        This verifies Requirement 3.1:
        - When using reference mode with external classes
        - Then system SHALL continue to inherit from external classes
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test PASSES
        - This is the baseline behavior to preserve
        
        **EXPECTED OUTCOME ON FIXED CODE**: This test PASSES
        - Reference mode behavior should remain unchanged
        """
        toml_dict, entity_name, external_classes, entity_columns = test_data
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code with reference mode
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        generated_code = renderer.render(er_model)
        
        # Property: Generated class SHOULD inherit from external classes in reference mode
        for external_class in external_classes:
            parts = external_class.rsplit('.', 1)
            if len(parts) == 2:
                class_name = parts[1]
                
                # Check that class name IS in the class definition
                inheritance_pattern = rf'class\s+{re.escape(entity_name)}\s*\([^)]*{re.escape(class_name)}[^)]*\)'
                
                assert re.search(inheritance_pattern, generated_code), (
                    f"PRESERVATION VIOLATION: Reference mode should inherit from external class '{class_name}'.\n"
                    f"This is existing behavior that must be preserved.\n"
                    f"Generated code:\n{generated_code}"
                )
    
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(toml_with_internal_template())
    def test_internal_template_handling_flatten_mode(self, test_data):
        """
        Test that internal templates are handled correctly in flatten mode.
        
        This verifies Requirement 3.2:
        - When using flatten mode with internal templates WITHOUT export_path
        - Then system SHALL continue to expand fields from internal templates
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test PASSES
        - This is the baseline behavior to preserve
        
        **EXPECTED OUTCOME ON FIXED CODE**: This test PASSES
        - Internal template handling should remain unchanged
        """
        toml_dict, template_name, template_columns, entity_name, entity_columns, has_export_path = test_data
        
        # Skip if template has export_path (that's a known issue, not our concern)
        if has_export_path:
            return
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code with flatten mode
        renderer = SQLAlchemyRenderer(inheritance_mode='flatten')
        generated_code = renderer.render(er_model)
        
        # Property: In flatten mode, fields from internal templates (without export_path) should be expanded
        for template_col in template_columns:
            col_name = template_col['name']
            column_pattern = rf'{re.escape(col_name)}\s*=\s*Column\('
            
            assert re.search(column_pattern, generated_code), (
                f"PRESERVATION VIOLATION: Flatten mode should expand field '{col_name}' from internal template.\n"
                f"This is existing behavior that must be preserved.\n"
                f"Generated code:\n{generated_code}"
            )
        
        # Property: Entity's own fields should also be present
        for entity_col in entity_columns:
            col_name = entity_col['name']
            column_pattern = rf'{re.escape(col_name)}\s*=\s*Column\('
            
            assert re.search(column_pattern, generated_code), (
                f"PRESERVATION VIOLATION: Entity's own field '{col_name}' should be present.\n"
                f"Generated code:\n{generated_code}"
            )
    
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(toml_with_internal_template())
    def test_internal_template_handling_reference_mode(self, test_data):
        """
        Test that internal templates are handled correctly in reference mode.
        
        This verifies Requirement 3.1:
        - When using reference mode with internal templates WITHOUT export_path
        - Then system SHALL continue to expand fields from internal templates
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test PASSES
        - This is the baseline behavior to preserve
        
        **EXPECTED OUTCOME ON FIXED CODE**: This test PASSES
        - Internal template handling should remain unchanged
        """
        toml_dict, template_name, template_columns, entity_name, entity_columns, has_export_path = test_data
        
        # Skip if template has export_path (that's a known issue, not our concern)
        if has_export_path:
            return
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code with reference mode
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        generated_code = renderer.render(er_model)
        
        # Property: In reference mode without export_path, should expand fields
        for template_col in template_columns:
            col_name = template_col['name']
            column_pattern = rf'{re.escape(col_name)}\s*=\s*Column\('
            
            assert re.search(column_pattern, generated_code), (
                f"PRESERVATION VIOLATION: Reference mode should expand field '{col_name}' from template without export_path.\n"
                f"This is existing behavior that must be preserved.\n"
                f"Generated code:\n{generated_code}"
            )
    
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(toml_without_inheritance())
    def test_no_inheritance_only_base(self, test_data):
        """
        Test that entities without inheritance only inherit from Base.
        
        This verifies Requirement 3.3:
        - When entity has no classes in extends
        - Then system SHALL continue to generate models as before (only inherit from Base)
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test PASSES
        - This is the baseline behavior to preserve
        
        **EXPECTED OUTCOME ON FIXED CODE**: This test PASSES
        - No inheritance cases should remain unchanged
        """
        toml_dict, entity_name, entity_columns = test_data
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code (mode doesn't matter for no inheritance)
        renderer = SQLAlchemyRenderer(inheritance_mode='flatten')
        generated_code = renderer.render(er_model)
        
        # Property: Generated class should only inherit from Base
        class_pattern = rf'class\s+{re.escape(entity_name)}\s*\(\s*Base\s*\)\s*:'
        
        assert re.search(class_pattern, generated_code), (
            f"PRESERVATION VIOLATION: Entity without inheritance should only inherit from Base.\n"
            f"Expected: class {entity_name}(Base):\n"
            f"This is existing behavior that must be preserved.\n"
            f"Generated code:\n{generated_code}"
        )
        
        # Property: Entity's own fields should be present
        for entity_col in entity_columns:
            col_name = entity_col['name']
            column_pattern = rf'{re.escape(col_name)}\s*=\s*Column\('
            
            assert re.search(column_pattern, generated_code), (
                f"PRESERVATION VIOLATION: Entity's own field '{col_name}' should be present.\n"
                f"Generated code:\n{generated_code}"
            )
    
    def test_concrete_reference_mode_single_external_class(self):
        """
        Concrete test: Reference mode with single external class.
        
        This documents the baseline behavior for reference mode.
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test PASSES
        """
        toml_dict = {
            'entities': {
                'Order': {
                    'extends': ['kinkotech.common.infrastructure.models.base.KinkoTechModelBase'],
                    'table_name': 'order',
                    'columns': [
                        {'name': 'id', 'type': 'bigint', 'primary_key': True},
                        {'name': 'order_number', 'type': 'string'}
                    ]
                }
            }
        }
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code with reference mode
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        generated_code = renderer.render(er_model)
        
        # Verify import of external class
        assert 'from kinkotech.common.infrastructure.models.base import KinkoTechModelBase' in generated_code, (
            f"PRESERVATION: Reference mode should import external class.\n"
            f"Generated code:\n{generated_code}"
        )
        
        # Verify inheritance from external class
        assert re.search(r'class\s+Order\s*\([^)]*KinkoTechModelBase[^)]*\)', generated_code), (
            f"PRESERVATION: Reference mode should inherit from external class.\n"
            f"Generated code:\n{generated_code}"
        )
    
    def test_concrete_no_inheritance(self):
        """
        Concrete test: Entity without any inheritance.
        
        This documents the baseline behavior for entities without inheritance.
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test PASSES
        """
        toml_dict = {
            'entities': {
                'Product': {
                    'table_name': 'product',
                    'columns': [
                        {'name': 'id', 'type': 'bigint', 'primary_key': True},
                        {'name': 'name', 'type': 'string'}
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
        renderer = SQLAlchemyRenderer(inheritance_mode='flatten')
        generated_code = renderer.render(er_model)
        
        # Verify class only inherits from Base
        assert re.search(r'class\s+Product\s*\(\s*Base\s*\)\s*:', generated_code), (
            f"PRESERVATION: Entity without inheritance should only inherit from Base.\n"
            f"Generated code:\n{generated_code}"
        )
        
        # Verify entity's own fields are present
        assert re.search(r'id\s*=\s*Column\(', generated_code), (
            "Product model should have its own 'id' field"
        )
        assert re.search(r'name\s*=\s*Column\(', generated_code), (
            "Product model should have its own 'name' field"
        )
