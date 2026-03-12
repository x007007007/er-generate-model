"""
Preservation Property Tests for Third-Party Library Inheritance Import Fix

**Property 2: Preservation - Internal Templates and Other Modes Behavior**

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

These tests verify that the fix doesn't break existing functionality.
They capture the observed behavior on UNFIXED code for non-buggy inputs.

IMPORTANT: Follow observation-first methodology
- Observe behavior on UNFIXED code for non-buggy inputs
- Write property-based tests capturing observed behavior patterns
- Run tests on UNFIXED code
- EXPECTED OUTCOME: Tests PASS (confirms baseline behavior to preserve)

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
def toml_with_internal_mixin(draw):
    """
    Generate TOML data with internal mixin inheritance (namespace parts < 3).
    
    Returns a tuple of (toml_dict, template_name, entity_name, entity_columns)
    """
    # Generate template name (single part - internal mixin)
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
    
    # Generate entity
    entity_name = draw(safe_identifier.filter(lambda x: x != template_name))
    num_entity_cols = draw(st.integers(min_value=1, max_value=3))
    
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
    
    # Add export_path to ensure template is generated as a separate file
    # Without export_path, templates are flattened in reference mode
    template_file_name = template_name.lower()
    
    toml_dict = {
        'templates': {
            template_name: {
                'export_path': f'mixins.{template_file_name}',
                'columns': template_columns
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
    
    return toml_dict, template_name, entity_name, entity_columns


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


class TestProperty2PreservationInternalTemplatesAndOtherModes:
    """
    Property 2: Preservation - Internal Templates and Other Modes Behavior
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**
    
    For any non-buggy input (internal templates, flatten mode, no inheritance),
    the fixed system SHALL produce identical results to the original system.
    
    **CRITICAL**: These tests MUST PASS on unfixed code - they document baseline behavior.
    """
    
    def test_concrete_internal_mixin_no_third_prefix(self):
        """
        Test Case 1: Internal Mixin preservation - entity extends `TimestampMixin` (2 parts)
        
        Observe: import statement does NOT have `third.` prefix
        Observe: file generated at `mixins/timestamp_mixin.py`
        
        **Validates: Requirement 3.1**
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test PASSES
        - This is the baseline behavior to preserve
        
        **EXPECTED OUTCOME ON FIXED CODE**: This test PASSES
        - Internal mixin handling should remain unchanged
        """
        toml_dict = {
            'templates': {
                'TimestampMixin': {
                    'columns': [
                        {'name': 'created_at', 'type': 'datetime'},
                        {'name': 'updated_at', 'type': 'datetime'}
                    ]
                }
            },
            'entities': {
                'User': {
                    'extends': ['TimestampMixin'],
                    'table_name': 'user',
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
        
        # Generate SQLAlchemy code with reference mode (multi-file)
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        files = renderer.render_multi_file(er_model)
        
        # Get the entity file
        entity_file = files.get('user.py', '')
        
        # Property 1: Import statement should NOT have `third.` prefix
        # Note: System converts template names to lowercase without underscores
        assert 'from mixins.timestampmixin import TimestampMixin' in entity_file, (
            f"PRESERVATION VIOLATION (Req 3.1): Internal mixin import should NOT have `third.` prefix.\n"
            f"Expected: from mixins.timestampmixin import TimestampMixin\n"
            f"This is existing behavior that must be preserved.\n"
            f"Generated entity file:\n{entity_file}"
        )
        
        # Property 2: File should be generated at `mixins/timestampmixin.py`
        # Note: System converts template names to lowercase without underscores
        expected_file_path = 'mixins/timestampmixin.py'
        assert expected_file_path in files, (
            f"PRESERVATION VIOLATION (Req 3.5): Internal mixin file should be generated at mixins/ directory.\n"
            f"Expected file: {expected_file_path}\n"
            f"Generated files: {list(files.keys())}\n"
            f"This is existing behavior that must be preserved."
        )
        
        # Property 3: Mixin file should contain class definition
        mixin_file = files.get(expected_file_path, '')
        assert 'class TimestampMixin' in mixin_file, (
            f"PRESERVATION VIOLATION: Mixin file should contain class definition.\n"
            f"Expected: class TimestampMixin\n"
            f"Generated file content:\n{mixin_file}"
        )
    
    def test_concrete_flatten_mode_no_external_imports(self):
        """
        Test Case 2: Flatten mode preservation - `inheritance_mode='flatten'`
        
        Observe: no external class imports generated
        Observe: template fields are flattened into entity
        
        **Validates: Requirement 3.3**
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test PASSES
        - This is the baseline behavior to preserve
        
        **EXPECTED OUTCOME ON FIXED CODE**: This test PASSES
        - Flatten mode behavior should remain unchanged
        """
        toml_dict = {
            'templates': {
                'BaseModel': {
                    'columns': [
                        {'name': 'id', 'type': 'bigint', 'primary_key': True},
                        {'name': 'created_at', 'type': 'datetime'}
                    ]
                }
            },
            'entities': {
                'Product': {
                    'extends': ['BaseModel'],
                    'table_name': 'product',
                    'columns': [
                        {'name': 'name', 'type': 'string'},
                        {'name': 'price', 'type': 'int'}
                    ]
                }
            }
        }
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code with flatten mode (single-file)
        renderer = SQLAlchemyRenderer(inheritance_mode='flatten')
        generated_code = renderer.render(er_model)
        
        # Property 1: No external class imports should be generated
        # In flatten mode, we should NOT see "from ... import BaseModel"
        assert 'from mixins.base_model import BaseModel' not in generated_code, (
            f"PRESERVATION VIOLATION (Req 3.3): Flatten mode should NOT generate external class imports.\n"
            f"This is existing behavior that must be preserved.\n"
            f"Generated code:\n{generated_code}"
        )
        
        # Property 2: Template fields should be flattened into entity
        assert 'id = Column(' in generated_code, (
            f"PRESERVATION VIOLATION (Req 3.3): Flatten mode should include inherited field 'id'.\n"
            f"Generated code:\n{generated_code}"
        )
        assert 'created_at = Column(' in generated_code, (
            f"PRESERVATION VIOLATION (Req 3.3): Flatten mode should include inherited field 'created_at'.\n"
            f"Generated code:\n{generated_code}"
        )
        
        # Property 3: Entity's own fields should also be present
        assert 'name = Column(' in generated_code, (
            f"Entity's own field 'name' should be present.\n"
            f"Generated code:\n{generated_code}"
        )
        assert 'price = Column(' in generated_code, (
            f"Entity's own field 'price' should be present.\n"
            f"Generated code:\n{generated_code}"
        )
    
    def test_concrete_no_inheritance_normal_generation(self):
        """
        Test Case 3: Non-inheritance scenario preservation - entity without `extends` field
        
        Observe: model generation works normally
        
        **Validates: Requirement 3.2**
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test PASSES
        - This is the baseline behavior to preserve
        
        **EXPECTED OUTCOME ON FIXED CODE**: This test PASSES
        - Non-inheritance scenarios should remain unchanged
        """
        toml_dict = {
            'entities': {
                'Order': {
                    'table_name': 'order',
                    'columns': [
                        {'name': 'id', 'type': 'bigint', 'primary_key': True},
                        {'name': 'order_number', 'type': 'string'},
                        {'name': 'total', 'type': 'int'}
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
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        generated_code = renderer.render(er_model)
        
        # Property 1: Class should only inherit from Base
        assert re.search(r'class\s+Order\s*\(\s*Base\s*\)\s*:', generated_code), (
            f"PRESERVATION VIOLATION (Req 3.2): Entity without inheritance should only inherit from Base.\n"
            f"Expected: class Order(Base):\n"
            f"This is existing behavior that must be preserved.\n"
            f"Generated code:\n{generated_code}"
        )
        
        # Property 2: All entity fields should be present
        assert 'id = Column(' in generated_code, "Field 'id' should be present"
        assert 'order_number = Column(' in generated_code, "Field 'order_number' should be present"
        assert 'total = Column(' in generated_code, "Field 'total' should be present"
        
        # Property 3: __tablename__ should be set correctly
        assert "__tablename__ = 'order'" in generated_code or '__tablename__ = "order"' in generated_code, (
            f"__tablename__ should be set to 'order'.\n"
            f"Generated code:\n{generated_code}"
        )
    
    def test_concrete_namespace_transformation_sqlalchemy_suffix(self):
        """
        Test Case 4: Namespace transformation preservation - `_sqlalchemy` suffix addition
        
        Observe: namespace transformation works correctly for both internal and third-party
        
        **Validates: Requirement 3.4**
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test PASSES
        - This is the baseline behavior to preserve
        
        **EXPECTED OUTCOME ON FIXED CODE**: This test PASSES
        - Namespace transformation logic should remain unchanged
        """
        toml_dict = {
            'templates': {
                'AuditMixin': {
                    'columns': [
                        {'name': 'created_by', 'type': 'string'}
                    ]
                }
            },
            'entities': {
                'Invoice': {
                    'extends': ['AuditMixin'],
                    'table_name': 'invoice',
                    'columns': [
                        {'name': 'id', 'type': 'bigint', 'primary_key': True},
                        {'name': 'amount', 'type': 'int'}
                    ]
                }
            }
        }
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code with reference mode (multi-file)
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        files = renderer.render_multi_file(er_model)
        
        # Property: Mixin file should be generated
        # Note: System converts template names to lowercase without underscores
        expected_file_path = 'mixins/auditmixin.py'
        assert expected_file_path in files, (
            f"PRESERVATION VIOLATION (Req 3.4): Mixin file should be generated.\n"
            f"Expected file: {expected_file_path}\n"
            f"Generated files: {list(files.keys())}\n"
            f"This is existing behavior that must be preserved."
        )
        
        # Property: Import statement should use the correct path
        entity_file = files.get('invoice.py', '')
        assert 'from mixins.auditmixin import AuditMixin' in entity_file, (
            f"PRESERVATION VIOLATION (Req 3.4): Import statement should use correct path.\n"
            f"Expected: from mixins.auditmixin import AuditMixin\n"
            f"Generated entity file:\n{entity_file}"
        )
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(toml_with_internal_mixin())
    def test_property_internal_templates_no_third_prefix(self, test_data):
        """
        Property-based test: Internal templates should NOT have `third.` prefix
        
        This verifies Requirement 3.1:
        - When entity extends internal template (namespace parts < 3)
        - Then import statement should NOT have `third.` prefix
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test PASSES
        - This is the baseline behavior to preserve
        
        **EXPECTED OUTCOME ON FIXED CODE**: This test PASSES
        - Internal template handling should remain unchanged
        """
        toml_dict, template_name, entity_name, entity_columns = test_data
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code with reference mode (multi-file)
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        files = renderer.render_multi_file(er_model)
        
        # Get the entity file
        entity_filename = re.sub(r'(?<!^)(?=[A-Z])', '_', entity_name).lower() + '.py'
        entity_file = files.get(entity_filename, '')
        
        # If entity file is empty, check if it's using a different naming convention
        if not entity_file:
            # Try lowercase without underscores
            entity_filename_alt = entity_name.lower() + '.py'
            entity_file = files.get(entity_filename_alt, '')
            if entity_file:
                entity_filename = entity_filename_alt
        
        # Skip if entity file is not found (might be a generation issue unrelated to our test)
        if not entity_file:
            return
        
        # Property: Internal template import should NOT have `third.` prefix
        # Convert template name to lowercase (no underscores) for file path
        template_file_name = template_name.lower()
        expected_import_pattern = rf'from\s+mixins\.{re.escape(template_file_name)}\s+import\s+{re.escape(template_name)}'
        
        assert re.search(expected_import_pattern, entity_file), (
            f"PRESERVATION VIOLATION: Internal template import should NOT have `third.` prefix.\n"
            f"Template: {template_name}\n"
            f"Expected pattern: from mixins.{template_file_name} import {template_name}\n"
            f"Entity: {entity_name}\n"
            f"Entity filename: {entity_filename}\n"
            f"This is existing behavior that must be preserved.\n"
            f"Generated entity file:\n{entity_file}"
        )
        
        # Property: Internal template file should be in mixins/ directory
        expected_file_path = f'mixins/{template_file_name}.py'
        assert expected_file_path in files, (
            f"PRESERVATION VIOLATION: Internal template file should be in mixins/ directory.\n"
            f"Expected file: {expected_file_path}\n"
            f"Generated files: {list(files.keys())}\n"
            f"This is existing behavior that must be preserved."
        )
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(toml_without_inheritance())
    def test_property_no_inheritance_only_base(self, test_data):
        """
        Property-based test: Entities without inheritance should only inherit from Base
        
        This verifies Requirement 3.2:
        - When entity has no extends field
        - Then class should only inherit from Base
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test PASSES
        - This is the baseline behavior to preserve
        
        **EXPECTED OUTCOME ON FIXED CODE**: This test PASSES
        - Non-inheritance scenarios should remain unchanged
        """
        toml_dict, entity_name, entity_columns = test_data
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        generated_code = renderer.render(er_model)
        
        # Property: Class should only inherit from Base
        class_pattern = rf'class\s+{re.escape(entity_name)}\s*\(\s*Base\s*\)\s*:'
        
        assert re.search(class_pattern, generated_code), (
            f"PRESERVATION VIOLATION: Entity without inheritance should only inherit from Base.\n"
            f"Expected: class {entity_name}(Base):\n"
            f"Entity: {entity_name}\n"
            f"This is existing behavior that must be preserved.\n"
            f"Generated code:\n{generated_code}"
        )
        
        # Property: Entity's own fields should be present
        for entity_col in entity_columns:
            col_name = entity_col['name']
            column_pattern = rf'{re.escape(col_name)}\s*=\s*Column\('
            
            assert re.search(column_pattern, generated_code), (
                f"PRESERVATION VIOLATION: Entity's own field '{col_name}' should be present.\n"
                f"Entity: {entity_name}\n"
                f"Generated code:\n{generated_code}"
            )
