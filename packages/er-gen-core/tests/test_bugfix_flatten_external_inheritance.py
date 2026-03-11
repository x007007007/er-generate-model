"""
Bug Condition Exploration Test for SQLAlchemy Flatten Mode External Inheritance Fix

**Property 1: Fault Condition - No External Inheritance in Flatten Mode**

**Validates: Requirements 2.1, 2.2, 2.3**

This test MUST FAIL on unfixed code - failure confirms the bug exists.
DO NOT attempt to fix the test or the code when it fails.

The test encodes the expected behavior - it will validate the fix when it passes after implementation.

GOAL: Surface counterexamples that demonstrate external Django classes are incorrectly imported
and inherited in SQLAlchemy models when using flatten mode.

Scoped PBT Approach: Test concrete failing cases with entities that extend external Django classes
(classes not defined in model.templates) using flatten mode.
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
def toml_with_external_class_inheritance(draw):
    """
    Generate TOML data with external class inheritance (classes not in templates).
    
    This strategy creates:
    - An entity that extends external Django classes (not defined in templates)
    - The entity has its own columns
    
    Returns a tuple of (toml_dict, entity_name, external_classes, entity_columns)
    """
    # Generate entity name and columns
    entity_name = draw(safe_identifier)
    num_entity_cols = draw(st.integers(min_value=1, max_value=3))
    
    entity_columns = []
    for i in range(num_entity_cols):
        col_name = draw(safe_column_name.filter(lambda x: x not in [c['name'] for c in entity_columns]))
        col_type = draw(safe_type)
        entity_columns.append({
            'name': col_name,
            'type': col_type,
            'primary_key': i == 0  # First column is PK
        })
    
    # Generate external class references (Django model classes)
    num_external = draw(st.integers(min_value=1, max_value=3))
    external_classes = []
    for i in range(num_external):
        class_name = draw(safe_identifier.filter(lambda x: x not in external_classes and x != entity_name))
        # Create fully qualified external class name (Django-style)
        external_class = f"kinkotech.common.infrastructure.models.base.{class_name}"
        external_classes.append(external_class)
    
    # Build TOML structure
    toml_dict = {
        # NO templates section - external classes are not defined here
        'entities': {
            entity_name: {
                'extends': external_classes,
                'table_name': entity_name.lower(),
                'columns': entity_columns
            }
        }
    }
    
    return toml_dict, entity_name, external_classes, entity_columns


class TestProperty1NoExternalInheritanceInFlattenMode:
    """
    Property 1: Fault Condition - No External Inheritance in Flatten Mode
    
    **Validates: Requirements 2.1, 2.2, 2.3**
    
    For any entity with external classes in extends list when using flatten mode,
    the generated SQLAlchemy model SHALL NOT import external classes, SHALL NOT inherit
    from external classes, and SHALL only inherit from Base.
    
    **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists.
    """
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(toml_with_external_class_inheritance())
    def test_flatten_mode_no_external_imports(self, test_data):
        """
        Test that external classes are NOT imported in flatten mode.
        
        This verifies Requirement 2.1:
        - When generating SQLAlchemy output with flatten mode
        - And entity has external Django classes in extends
        - Then system SHALL NOT import the external Django classes
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test FAILS
        - Generated code will contain import statements for external classes
        - Counterexamples will show which external classes are imported
        
        **EXPECTED OUTCOME ON FIXED CODE**: This test PASSES
        - Generated code will NOT contain import statements for external classes
        """
        toml_dict, entity_name, external_classes, entity_columns = test_data
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code with flatten mode
        renderer = SQLAlchemyRenderer(inheritance_mode='flatten')
        generated_code = renderer.render(er_model)
        
        # Property: Generated code should NOT import external classes
        for external_class in external_classes:
            # Extract module path and class name
            parts = external_class.rsplit('.', 1)
            if len(parts) == 2:
                module_path = parts[0]
                class_name = parts[1]
                
                # Check that import statement is NOT present
                import_pattern = rf'from\s+{re.escape(module_path)}\s+import\s+.*{re.escape(class_name)}'
                
                assert not re.search(import_pattern, generated_code), (
                    f"COUNTEREXAMPLE FOUND: Generated SQLAlchemy model for '{entity_name}' "
                    f"INCORRECTLY imports external class '{class_name}' from '{module_path}' in flatten mode.\n"
                    f"External classes: {external_classes}\n"
                    f"This confirms the bug: external classes are imported when they should not be.\n"
                    f"Generated code:\n{generated_code}"
                )
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(toml_with_external_class_inheritance())
    def test_flatten_mode_no_external_inheritance(self, test_data):
        """
        Test that external classes are NOT in the inheritance list in flatten mode.
        
        This verifies Requirement 2.2:
        - When generating SQLAlchemy output with flatten mode
        - And entity has external Django classes in extends
        - Then system SHALL only inherit from Base (not from external classes)
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test FAILS
        - Generated class will inherit from external classes
        - Counterexamples will show which external classes are in inheritance list
        
        **EXPECTED OUTCOME ON FIXED CODE**: This test PASSES
        - Generated class will only inherit from Base
        """
        toml_dict, entity_name, external_classes, entity_columns = test_data
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code with flatten mode
        renderer = SQLAlchemyRenderer(inheritance_mode='flatten')
        generated_code = renderer.render(er_model)
        
        # Property: Generated class should only inherit from Base
        # Pattern: class EntityName(Base):
        class_pattern = rf'class\s+{re.escape(entity_name)}\s*\(\s*Base\s*\)\s*:'
        
        assert re.search(class_pattern, generated_code), (
            f"COUNTEREXAMPLE FOUND: Generated SQLAlchemy model for '{entity_name}' "
            f"does NOT inherit only from Base in flatten mode.\n"
            f"Expected: class {entity_name}(Base):\n"
            f"External classes that should NOT be inherited: {external_classes}\n"
            f"This confirms the bug: external classes are in the inheritance list.\n"
            f"Generated code:\n{generated_code}"
        )
        
        # Also verify that external class names are NOT in the class definition
        for external_class in external_classes:
            parts = external_class.rsplit('.', 1)
            if len(parts) == 2:
                class_name = parts[1]
                
                # Check that class name is NOT in the class definition line
                # Pattern: class EntityName(...ClassName...) - use word boundaries to avoid false matches
                inheritance_pattern = rf'class\s+{re.escape(entity_name)}\s*\([^)]*\b{re.escape(class_name)}\b[^)]*\)'
                
                assert not re.search(inheritance_pattern, generated_code), (
                    f"COUNTEREXAMPLE FOUND: Generated SQLAlchemy model for '{entity_name}' "
                    f"INCORRECTLY inherits from external class '{class_name}' in flatten mode.\n"
                    f"Expected: class {entity_name}(Base):\n"
                    f"Actual: class definition includes '{class_name}'\n"
                    f"This confirms the bug: external classes are in the inheritance list.\n"
                    f"Generated code:\n{generated_code}"
                )
    
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(toml_with_external_class_inheritance())
    def test_flatten_mode_entity_fields_present(self, test_data):
        """
        Test that entity's own fields are present in flatten mode.
        
        This ensures that the fix doesn't break the existing functionality of
        rendering entity's own columns.
        """
        toml_dict, entity_name, external_classes, entity_columns = test_data
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code with flatten mode
        renderer = SQLAlchemyRenderer(inheritance_mode='flatten')
        generated_code = renderer.render(er_model)
        
        # Property: Generated model should contain entity's own fields
        for entity_col in entity_columns:
            col_name = entity_col['name']
            column_pattern = rf'{re.escape(col_name)}\s*=\s*Column\('
            
            assert re.search(column_pattern, generated_code), (
                f"Entity's own field '{col_name}' should be present in generated code"
            )
    
    def test_concrete_single_external_class_flatten_mode(self):
        """
        Concrete test case: Entity extends single external Django class with flatten mode.
        
        This is a concrete example of the bug:
        - Entity extends 'kinkotech.common.infrastructure.models.base.KinkoTechModelBase'
        - Using flatten mode
        - Expected: No import, only inherit from Base
        - Actual (UNFIXED): Imports KinkoTechModelBase and inherits from it
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test FAILS
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
        
        # Generate SQLAlchemy code with flatten mode
        renderer = SQLAlchemyRenderer(inheritance_mode='flatten')
        generated_code = renderer.render(er_model)
        
        # Verify NO import of external class
        assert 'from kinkotech.common.infrastructure.models.base import' not in generated_code, (
            f"COUNTEREXAMPLE: Generated code INCORRECTLY imports external class in flatten mode.\n"
            f"Generated code:\n{generated_code}"
        )
        
        # Verify class only inherits from Base
        assert re.search(r'class\s+Order\s*\(\s*Base\s*\)\s*:', generated_code), (
            f"COUNTEREXAMPLE: Generated class does NOT inherit only from Base in flatten mode.\n"
            f"Expected: class Order(Base):\n"
            f"Generated code:\n{generated_code}"
        )
        
        # Verify entity's own fields are present
        assert re.search(r'id\s*=\s*Column\(', generated_code), (
            "Order model should have its own 'id' field"
        )
        assert re.search(r'order_number\s*=\s*Column\(', generated_code), (
            "Order model should have its own 'order_number' field"
        )
    
    def test_concrete_multiple_external_classes_flatten_mode(self):
        """
        Concrete test case: Entity extends multiple external Django classes with flatten mode.
        
        This tests the bug with multiple external classes:
        - Entity extends multiple Django model classes
        - Using flatten mode
        - Expected: No imports, only inherit from Base
        - Actual (UNFIXED): Imports all external classes and inherits from them
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test FAILS
        """
        toml_dict = {
            'entities': {
                'PromotionCode': {
                    'extends': [
                        'kinkotech.common.infrastructure.models.base.KinkoTechModelBase',
                        'kinkotech.common.infrastructure.models.base.CreateModifyMixinModel',
                        'kinkotech.common.infrastructure.models.base.LocationMixin'
                    ],
                    'table_name': 'promotion_code',
                    'columns': [
                        {'name': 'id', 'type': 'bigint', 'primary_key': True},
                        {'name': 'code', 'type': 'string'},
                        {'name': 'discount', 'type': 'int'}
                    ]
                }
            }
        }
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code with flatten mode
        renderer = SQLAlchemyRenderer(inheritance_mode='flatten')
        generated_code = renderer.render(er_model)
        
        # Verify NO imports of external classes
        assert 'from kinkotech.common.infrastructure.models.base import' not in generated_code, (
            f"COUNTEREXAMPLE: Generated code INCORRECTLY imports external classes in flatten mode.\n"
            f"Generated code:\n{generated_code}"
        )
        
        # Verify class only inherits from Base
        assert re.search(r'class\s+PromotionCode\s*\(\s*Base\s*\)\s*:', generated_code), (
            f"COUNTEREXAMPLE: Generated class does NOT inherit only from Base in flatten mode.\n"
            f"Expected: class PromotionCode(Base):\n"
            f"Generated code:\n{generated_code}"
        )
        
        # Verify none of the external class names appear in the class definition
        assert 'KinkoTechModelBase' not in re.search(r'class\s+PromotionCode\s*\([^)]*\)', generated_code).group(), (
            "COUNTEREXAMPLE: KinkoTechModelBase should NOT be in inheritance list"
        )
        assert 'CreateModifyMixinModel' not in re.search(r'class\s+PromotionCode\s*\([^)]*\)', generated_code).group(), (
            "COUNTEREXAMPLE: CreateModifyMixinModel should NOT be in inheritance list"
        )
        assert 'LocationMixin' not in re.search(r'class\s+PromotionCode\s*\([^)]*\)', generated_code).group(), (
            "COUNTEREXAMPLE: LocationMixin should NOT be in inheritance list"
        )
        
        # Verify entity's own fields are present
        assert re.search(r'id\s*=\s*Column\(', generated_code), (
            "PromotionCode model should have its own 'id' field"
        )
        assert re.search(r'code\s*=\s*Column\(', generated_code), (
            "PromotionCode model should have its own 'code' field"
        )
        assert re.search(r'discount\s*=\s*Column\(', generated_code), (
            "PromotionCode model should have its own 'discount' field"
        )
    
    def test_concrete_mixed_internal_external_flatten_mode(self):
        """
        Concrete test case: Entity extends both internal templates and external classes with flatten mode.
        
        This tests the bug with mixed inheritance:
        - Entity extends both internal templates (defined in TOML) and external Django classes
        - Using flatten mode
        - Expected: No external imports, only inherit from Base, expand all fields
        - Actual (UNFIXED): Imports external classes and inherits from them
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test FAILS
        """
        toml_dict = {
            'templates': {
                'TimestampMixin': {
                    'columns': [
                        {'name': 'created_at', 'type': 'datetime'}
                    ]
                }
            },
            'entities': {
                'Product': {
                    'extends': [
                        'TimestampMixin',
                        'kinkotech.common.infrastructure.models.base.KinkoTechModelBase'
                    ],
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
        
        # Generate SQLAlchemy code with flatten mode
        renderer = SQLAlchemyRenderer(inheritance_mode='flatten')
        generated_code = renderer.render(er_model)
        
        # Verify NO import of external class
        assert 'from kinkotech.common.infrastructure.models.base import' not in generated_code, (
            f"COUNTEREXAMPLE: Generated code INCORRECTLY imports external class in flatten mode.\n"
            f"Generated code:\n{generated_code}"
        )
        
        # Verify class only inherits from Base
        assert re.search(r'class\s+Product\s*\(\s*Base\s*\)\s*:', generated_code), (
            f"COUNTEREXAMPLE: Generated class does NOT inherit only from Base in flatten mode.\n"
            f"Expected: class Product(Base):\n"
            f"Generated code:\n{generated_code}"
        )
        
        # Verify fields from internal template are expanded
        assert re.search(r'created_at\s*=\s*Column\(', generated_code), (
            "Product model should have 'created_at' field from TimestampMixin"
        )
        
        # Verify entity's own fields are present
        assert re.search(r'id\s*=\s*Column\(', generated_code), (
            "Product model should have its own 'id' field"
        )
        assert re.search(r'name\s*=\s*Column\(', generated_code), (
            "Product model should have its own 'name' field"
        )
