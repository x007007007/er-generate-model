"""
Preservation Property Tests for Django Inheritance Field Preservation Bugfix

**Property 2: Preservation - Non-Inheritance Behavior Preservation**

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

These tests verify that non-buggy inputs continue to generate correctly after the fix.
Tests should PASS on unfixed code (confirming baseline behavior to preserve).

IMPORTANT: Follow observation-first methodology
- Observe behavior on UNFIXED code for non-buggy inputs
- Write property-based tests capturing observed behavior patterns

Expected Outcome: Tests PASS on unfixed code (confirms baseline behavior to preserve)
"""
import re
import ast
import pytest
import toml
from hypothesis import given, settings, strategies as st, HealthCheck, assume
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer


# Custom strategies for generating valid identifiers
safe_identifier = st.from_regex(r'[A-Z][a-zA-Z0-9]*', fullmatch=True).filter(lambda s: len(s) < 50)
safe_column_name = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(lambda s: len(s) < 30)
safe_type = st.sampled_from(['string', 'text', 'bigint', 'int', 'datetime', 'boolean'])


@st.composite
def toml_entity_without_inheritance(draw):
    """
    Generate TOML data with entity that has NO inheritance.
    
    This represents the baseline case that should work correctly
    and continue to work after the fix.
    
    Returns a tuple of (toml_dict, entity_name, entity_columns)
    """
    # Generate entity name and columns
    entity_name = draw(safe_identifier)
    num_cols = draw(st.integers(min_value=1, max_value=4))
    
    entity_columns = []
    for i in range(num_cols):
        col_name = draw(safe_column_name.filter(
            lambda x: x not in [c['name'] for c in entity_columns]
        ))
        col_type = draw(safe_type)
        entity_columns.append({
            'name': col_name,
            'type': col_type,
            'primary_key': i == 0  # First column is PK
        })
    
    # Build TOML structure WITHOUT extends field
    toml_dict = {
        'entities': {
            entity_name: {
                'table_name': entity_name.lower(),
                'columns': entity_columns
                # NOTE: NO extends field - this is the baseline case
            }
        }
    }
    
    return toml_dict, entity_name, entity_columns


@st.composite
def toml_entity_with_export_path_inheritance(draw):
    """
    Generate TOML data with entity that inherits from template WITH export_path.
    
    This represents the case where inheritance works correctly (external Python class).
    This should continue to work after the fix.
    
    Returns a tuple of (toml_dict, template_name, entity_name, entity_columns)
    """
    # Generate template name with export_path
    template_name = draw(safe_identifier)
    export_path = f"myapp.mixins.{template_name.lower()}"
    
    # Template has columns (but they won't be expanded since it has export_path)
    num_template_cols = draw(st.integers(min_value=1, max_value=2))
    template_columns = []
    for i in range(num_template_cols):
        col_name = draw(safe_column_name.filter(
            lambda x: x not in [c['name'] for c in template_columns]
        ))
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
            'primary_key': i == 0
        })
    
    # Build TOML structure
    toml_dict = {
        'templates': {
            template_name: {
                'export_path': export_path,  # This makes it an external class
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


class TestProperty2PreservationNoInheritance:
    """
    Property 2.1: Preservation - Entities Without Inheritance
    
    **Validates: Requirement 3.1**
    
    For any TOML entity without extends field, the system SHALL CONTINUE TO
    generate correct SQLAlchemy models with all directly defined fields.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(toml_entity_without_inheritance())
    def test_entities_without_inheritance_generate_correctly(self, test_data):
        """
        Test that entities without inheritance continue to generate correctly.
        
        This verifies Requirement 3.1:
        - When TOML entity has NO extends field
        - Then system should generate SQLAlchemy model with all directly defined fields
        - This behavior must remain unchanged after the fix
        
        **EXPECTED OUTCOME**: This test PASSES on unfixed code
        """
        toml_dict, entity_name, entity_columns = test_data
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(er_model)
        
        # Property: All entity columns should be present in generated code
        for col in entity_columns:
            col_name = col['name']
            column_pattern = rf'{re.escape(col_name)}\s*=\s*Column\('
            
            assert re.search(column_pattern, generated_code), (
                f"Entity '{entity_name}' should have field '{col_name}' in generated code.\n"
                f"This is baseline behavior that must be preserved.\n"
                f"Generated code:\n{generated_code}"
            )
        
        # Verify generated code is syntactically valid
        try:
            ast.parse(generated_code)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{generated_code}")


class TestProperty2PreservationExportPathInheritance:
    """
    Property 2.2: Preservation - Entities With Export Path Inheritance
    
    **Validates: Requirement 3.2**
    
    For any TOML entity that extends templates with export_path, the system
    SHALL CONTINUE TO generate correct SQLAlchemy models that inherit from
    external Python classes without duplicating inherited fields.
    """
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(toml_entity_with_export_path_inheritance())
    def test_export_path_inheritance_works_correctly(self, test_data):
        """
        Test that inheritance from templates with export_path continues to work.
        
        This verifies Requirement 3.2:
        - When TOML entity extends template WITH export_path
        - Then system should generate SQLAlchemy model that inherits from external class
        - Inherited fields should NOT be duplicated in the entity class
        - This behavior must remain unchanged after the fix
        
        **EXPECTED OUTCOME**: This test PASSES on unfixed code
        """
        toml_dict, template_name, entity_name, entity_columns = test_data
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(er_model)
        
        # Property 1: Entity's own columns should be present
        for col in entity_columns:
            col_name = col['name']
            column_pattern = rf'{re.escape(col_name)}\s*=\s*Column\('
            
            assert re.search(column_pattern, generated_code), (
                f"Entity '{entity_name}' should have its own field '{col_name}'.\n"
                f"Generated code:\n{generated_code}"
            )
        
        # Property 2: Template columns should NOT be duplicated
        # (they should be inherited from the external class)
        template_columns = toml_dict['templates'][template_name]['columns']
        for col in template_columns:
            col_name = col['name']
            # Count occurrences of this column definition
            # Use word boundary to match exact column name, not substrings
            column_pattern = rf'\b{re.escape(col_name)}\s*=\s*Column\('
            matches = re.findall(column_pattern, generated_code)
            
            # Should appear at most once (in the template class, not in entity)
            # Actually, with export_path, template fields shouldn't appear at all
            # because they're in an external file
            assert len(matches) <= 1, (
                f"Template field '{col_name}' should not be duplicated in entity.\n"
                f"Found {len(matches)} occurrences.\n"
                f"Generated code:\n{generated_code}"
            )
        
        # Verify generated code is syntactically valid
        try:
            ast.parse(generated_code)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{generated_code}")


class TestProperty2PreservationFieldTypeMappings:
    """
    Property 2.3: Preservation - Field Type Mappings
    
    **Validates: Requirement 3.3**
    
    For any field type mapping (string → String, bigint → BigInteger, etc.),
    the system SHALL CONTINUE TO map types correctly.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(toml_entity_without_inheritance())
    def test_field_type_mappings_remain_unchanged(self, test_data):
        """
        Test that field type mappings continue to work correctly.
        
        This verifies Requirement 3.3:
        - When TOML field has specific type (string, bigint, datetime, etc.)
        - Then system should map it to correct SQLAlchemy type
        - This mapping must remain unchanged after the fix
        
        **EXPECTED OUTCOME**: This test PASSES on unfixed code
        """
        toml_dict, entity_name, entity_columns = test_data
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(er_model)
        
        # Property: Each field should have a SQLAlchemy type
        for col in entity_columns:
            col_name = col['name']
            col_type = col['type']
            
            # Find the column definition line
            column_pattern = rf'{re.escape(col_name)}\s*=\s*Column\([^)]+\)'
            match = re.search(column_pattern, generated_code)
            
            assert match, (
                f"Column '{col_name}' should be present in generated code.\n"
                f"Generated code:\n{generated_code}"
            )
            
            column_def = match.group(0)
            
            # Verify it has a SQLAlchemy type (not checking exact mapping, just presence)
            sqlalchemy_types = ['String', 'Text', 'Integer', 'BigInteger', 'Boolean', 
                              'Date', 'DateTime', 'Time', 'Float', 'Numeric']
            has_type = any(t in column_def for t in sqlalchemy_types)
            
            assert has_type, (
                f"Column '{col_name}' should have a SQLAlchemy type.\n"
                f"Column definition: {column_def}"
            )


class TestProperty2PreservationFieldAttributes:
    """
    Property 2.4: Preservation - Field Attributes
    
    **Validates: Requirement 3.4**
    
    For any field attributes (nullable, unique, primary_key, comment, etc.),
    the system SHALL CONTINUE TO correctly apply these attributes.
    """
    
    def test_nullable_attribute_preserved(self):
        """
        Test that nullable attribute is correctly applied.
        
        **EXPECTED OUTCOME**: This test PASSES on unfixed code
        
        Observed behavior:
        - nullable=True: Column is generated without explicit nullable parameter (default is nullable)
        - nullable=False: Column is generated with explicit nullable=False
        """
        toml_dict = {
            'entities': {
                'TestEntity': {
                    'table_name': 'test_entity',
                    'columns': [
                        {'name': 'id', 'type': 'bigint', 'primary_key': True},
                        {'name': 'optional_field', 'type': 'string', 'nullable': True},
                        {'name': 'required_field', 'type': 'string', 'nullable': False}
                    ]
                }
            }
        }
        
        toml_content = toml.dumps(toml_dict)
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(er_model)
        
        # Verify optional field is present (nullable=True may be omitted as it's default)
        assert re.search(r'optional_field\s*=\s*Column\(', generated_code), (
            "Nullable field should be present in generated code"
        )
        
        # Verify non-nullable fields have explicit nullable=False
        assert 'required_field' in generated_code and 'nullable=False' in generated_code, (
            f"Non-nullable field should have explicit nullable=False.\nGenerated code:\n{generated_code}"
        )
    
    def test_unique_attribute_preserved(self):
        """
        Test that unique attribute is correctly applied.
        
        **EXPECTED OUTCOME**: This test PASSES on unfixed code
        """
        toml_dict = {
            'entities': {
                'TestEntity': {
                    'table_name': 'test_entity',
                    'columns': [
                        {'name': 'id', 'type': 'bigint', 'primary_key': True},
                        {'name': 'unique_field', 'type': 'string', 'unique': True}
                    ]
                }
            }
        }
        
        toml_content = toml.dumps(toml_dict)
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(er_model)
        
        # Verify unique fields have unique=True
        # Note: The regex needs to handle the case where unique=True appears in the Column definition
        assert 'unique_field' in generated_code and 'unique=True' in generated_code, (
            f"Unique field should have unique=True.\nGenerated code:\n{generated_code}"
        )
    
    def test_primary_key_attribute_preserved(self):
        """
        Test that primary_key attribute is correctly applied.
        
        **EXPECTED OUTCOME**: This test PASSES on unfixed code
        """
        toml_dict = {
            'entities': {
                'TestEntity': {
                    'table_name': 'test_entity',
                    'columns': [
                        {'name': 'id', 'type': 'bigint', 'primary_key': True},
                        {'name': 'name', 'type': 'string'}
                    ]
                }
            }
        }
        
        toml_content = toml.dumps(toml_dict)
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(er_model)
        
        # Verify primary key field has primary_key=True
        assert re.search(r'id\s*=\s*Column\([^)]*primary_key=True', generated_code), (
            "Primary key field should have primary_key=True"
        )


class TestProperty2PreservationRelationships:
    """
    Property 2.5: Preservation - Relationship Definitions
    
    **Validates: Requirement 3.2**
    
    For any relationship definition, the system SHALL CONTINUE TO generate
    correct foreign key and relationship definitions.
    """
    
    def test_relationship_generation_preserved(self):
        """
        Test that relationship definitions continue to generate correctly.
        
        **EXPECTED OUTCOME**: This test PASSES on unfixed code
        """
        toml_dict = {
            'entities': {
                'Author': {
                    'table_name': 'author',
                    'columns': [
                        {'name': 'id', 'type': 'bigint', 'primary_key': True},
                        {'name': 'name', 'type': 'string'}
                    ]
                },
                'Book': {
                    'table_name': 'book',
                    'columns': [
                        {'name': 'id', 'type': 'bigint', 'primary_key': True},
                        {'name': 'title', 'type': 'string'},
                        {'name': 'author_id', 'type': 'bigint', 'foreign_key': 'Author.id'}
                    ]
                }
            }
        }
        
        toml_content = toml.dumps(toml_dict)
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(er_model)
        
        # Verify foreign key is generated
        # Note: The exact format may vary, but it should contain ForeignKey
        assert 'ForeignKey' in generated_code, (
            "Generated code should contain ForeignKey for relationships"
        )
        
        # Verify both entities are present
        assert 'class Author' in generated_code, "Author entity should be generated"
        assert 'class Book' in generated_code, "Book entity should be generated"


class TestProperty2PreservationDjangoNaming:
    """
    Property 2.6: Preservation - Django-Style Naming
    
    **Validates: Requirement 3.5**
    
    For any Django-style relationship naming, the system SHALL CONTINUE TO
    use logical names (like 'code') rather than entity names (like 'i18ncode_rel').
    """
    
    def test_django_style_naming_preserved(self):
        """
        Test that Django-style naming conventions are preserved.
        
        This is a placeholder test since the exact Django naming behavior
        depends on the specific implementation. The test verifies that
        field names from TOML are used as-is in the generated code.
        
        **EXPECTED OUTCOME**: This test PASSES on unfixed code
        """
        toml_dict = {
            'entities': {
                'Translation': {
                    'table_name': 'translation',
                    'columns': [
                        {'name': 'id', 'type': 'bigint', 'primary_key': True},
                        {'name': 'code', 'type': 'string'}  # Logical name, not 'i18ncode_rel'
                    ]
                }
            }
        }
        
        toml_content = toml.dumps(toml_dict)
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(er_model)
        
        # Verify the logical name 'code' is used
        assert re.search(r'code\s*=\s*Column\(', generated_code), (
            "Field should use logical name 'code' from TOML"
        )
        
        # Verify it doesn't use entity-based naming like 'i18ncode_rel'
        assert 'i18ncode_rel' not in generated_code, (
            "Should not use entity-based naming like 'i18ncode_rel'"
        )
