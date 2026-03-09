"""
Property-based tests for Django-style foreign key naming.

These tests use hypothesis to verify universal properties across many generated inputs.
Each test runs a minimum of 100 iterations.
"""
import re
import pytest
from hypothesis import given, settings, strategies as st, HealthCheck
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.models import ERModel, Entity, Column, Relationship
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer


# Custom strategies for generating valid identifiers
safe_identifier = st.from_regex(r'[A-Z][a-zA-Z0-9]*', fullmatch=True).filter(lambda s: len(s) < 50)
safe_column_name = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(lambda s: len(s) < 30 and not s.endswith('_id'))


@st.composite
def django_style_fk_model(draw):
    """
    Generate an ERModel with Django-style foreign key naming.
    
    This strategy creates:
    - Two entities (left and right)
    - A relationship between them
    - A column in the right entity with name (logical) and db_column (with _id suffix)
    
    Returns a tuple of (model, right_entity_name, fk_logical_name, fk_db_column)
    """
    # Generate entity names
    left_entity_name = draw(safe_identifier)
    right_entity_name = draw(safe_identifier.filter(lambda x: x != left_entity_name))
    
    # Generate column names
    pk_column_name = 'id'
    fk_logical_name = draw(safe_column_name)
    fk_db_column = f"{fk_logical_name}_id"
    
    # Generate table names
    left_table_name = left_entity_name.lower()
    right_table_name = right_entity_name.lower()
    
    # Create entities
    left_entity = Entity(
        name=left_entity_name,
        table_name=left_table_name,
        columns=[
            Column(name=pk_column_name, type='bigint', db_column=pk_column_name, is_pk=True, nullable=False)
        ]
    )
    
    right_entity = Entity(
        name=right_entity_name,
        table_name=right_table_name,
        columns=[
            Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False),
            Column(name=fk_logical_name, type='bigint', db_column=fk_db_column, nullable=True)
        ]
    )
    
    # Create relationship
    relationship = Relationship(
        left_entity=left_entity_name,
        right_entity=right_entity_name,
        relation_type='one-to-many',
        left_column=pk_column_name,
        right_column=fk_db_column
    )
    
    # Create ERModel
    model = ERModel(
        entities={
            left_entity_name: left_entity,
            right_entity_name: right_entity
        },
        relationships=[relationship]
    )
    
    # Mark foreign keys (simulating what the parser does)
    parser = TomlERParser()
    parser._mark_foreign_keys(model.entities, model.relationships)
    
    return model, right_entity_name, fk_logical_name, fk_db_column


class TestProperty1DjangoStyleNaming:
    """
    Property 1: Django-Style Naming Convention
    
    **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
    
    For any TOML definition with a foreign key column where name is specified
    and db_column ends with _id, the generated SQLAlchemy model SHALL create:
    - A Column definition using the db_column name (with _id suffix)
    - A relationship object using the name (without _id suffix)
    - The relationship SHALL include foreign_keys=[{db_column}] parameter
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(django_style_fk_model())
    def test_column_uses_db_column_name_with_id_suffix(self, test_data):
        """
        Test that the generated Column definition uses db_column (with _id suffix).
        
        This verifies Requirement 1.2: WHEN a TOML definition specifies a column
        with name = "code" and db_column = "code_id", THE Generator SHALL create
        a Foreign_Key_Column named code_id.
        """
        model, right_entity_name, fk_logical_name, fk_db_column = test_data
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Property: The generated code should have a Column definition using db_column
        # Pattern: {db_column} = Column(
        column_pattern = rf'{re.escape(fk_db_column)}\s*=\s*Column\('
        
        assert re.search(column_pattern, generated_code), (
            f"Generated code should contain Column definition using db_column '{fk_db_column}', "
            f"but pattern '{column_pattern}' not found in:\n{generated_code}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(django_style_fk_model())
    def test_relationship_uses_logical_name_without_id_suffix(self, test_data):
        """
        Test that the generated relationship object uses the logical name (without _id suffix).
        
        This verifies Requirement 1.1: WHEN a TOML definition specifies a column
        with name = "code" and db_column = "code_id", THE Generator SHALL create
        a Relationship_Object named code.
        """
        model, right_entity_name, fk_logical_name, fk_db_column = test_data
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Property: The generated code should have a relationship using the logical name
        # Pattern: {logical_name} = relationship(
        # Note: We need to be careful not to match the column definition
        relationship_pattern = rf'{re.escape(fk_logical_name)}\s*=\s*relationship\('
        
        assert re.search(relationship_pattern, generated_code), (
            f"Generated code should contain relationship definition using logical name '{fk_logical_name}', "
            f"but pattern '{relationship_pattern}' not found in:\n{generated_code}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(django_style_fk_model())
    def test_relationship_includes_foreign_keys_parameter(self, test_data):
        """
        Test that the relationship includes foreign_keys=[{db_column}] parameter.
        
        This verifies Requirement 1.3: THE Relationship_Object SHALL reference
        the Foreign_Key_Column in its foreign_keys parameter.
        """
        model, right_entity_name, fk_logical_name, fk_db_column = test_data
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Property: The relationship should include foreign_keys=[{db_column}]
        # Pattern: foreign_keys=[{db_column}]
        foreign_keys_pattern = rf'foreign_keys\s*=\s*\[\s*{re.escape(fk_db_column)}\s*\]'
        
        assert re.search(foreign_keys_pattern, generated_code), (
            f"Generated code should contain 'foreign_keys=[{fk_db_column}]' in relationship, "
            f"but pattern '{foreign_keys_pattern}' not found in:\n{generated_code}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(django_style_fk_model())
    def test_column_and_relationship_both_present(self, test_data):
        """
        Test that both Column and relationship are present in the generated code.
        
        This verifies Requirement 1.4: FOR ALL foreign key columns, THE Generator
        SHALL produce both a Foreign_Key_Column with _id suffix and a Relationship_Object
        using the original name.
        """
        model, right_entity_name, fk_logical_name, fk_db_column = test_data
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Property: Both column and relationship should be present
        column_pattern = rf'{re.escape(fk_db_column)}\s*=\s*Column\('
        relationship_pattern = rf'{re.escape(fk_logical_name)}\s*=\s*relationship\('
        
        has_column = re.search(column_pattern, generated_code)
        has_relationship = re.search(relationship_pattern, generated_code)
        
        assert has_column and has_relationship, (
            f"Generated code should contain both Column '{fk_db_column}' and "
            f"relationship '{fk_logical_name}', but found: "
            f"column={bool(has_column)}, relationship={bool(has_relationship)}\n"
            f"Generated code:\n{generated_code}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(django_style_fk_model())
    def test_column_has_foreign_key_constraint(self, test_data):
        """
        Test that the Column definition includes a ForeignKey constraint.
        
        This verifies that the foreign key column properly references the target table.
        """
        model, right_entity_name, fk_logical_name, fk_db_column = test_data
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Get the left entity name (the target of the foreign key)
        left_entity_name = list(model.entities.keys())[0]
        left_table_name = model.entities[left_entity_name].table_name
        
        # Property: The column should have ForeignKey constraint
        # Pattern: {db_column} = Column(..., ForeignKey('{table}.id'), ...)
        # We look for the ForeignKey reference in the same line or nearby
        
        # Find the column definition
        column_start = generated_code.find(f'{fk_db_column} = Column(')
        assert column_start != -1, f"Column definition for '{fk_db_column}' not found"
        
        # Find the closing parenthesis for this Column definition
        # We need to handle nested parentheses
        paren_count = 0
        i = column_start + len(f'{fk_db_column} = Column(')
        column_end = i
        for j in range(i, len(generated_code)):
            if generated_code[j] == '(':
                paren_count += 1
            elif generated_code[j] == ')':
                if paren_count == 0:
                    column_end = j
                    break
                paren_count -= 1
        
        column_definition = generated_code[column_start:column_end+1]
        
        # Check for ForeignKey in the column definition
        assert 'ForeignKey' in column_definition, (
            f"Column definition for '{fk_db_column}' should contain ForeignKey constraint, "
            f"but it doesn't:\n{column_definition}"
        )
        
        # Check that it references the correct table
        fk_reference_pattern = rf"ForeignKey\(['\"]({re.escape(left_table_name)}\.id)['\"]"
        assert re.search(fk_reference_pattern, column_definition), (
            f"ForeignKey should reference '{left_table_name}.id', "
            f"but pattern not found in:\n{column_definition}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        left_entity_name=safe_identifier,
        right_entity_name=safe_identifier,
        num_fk_columns=st.integers(min_value=2, max_value=4)
    )
    def test_multiple_foreign_keys_all_follow_django_naming(self, left_entity_name, right_entity_name, num_fk_columns):
        """
        Test that multiple foreign keys in the same entity all follow Django-style naming.
        
        This verifies that the naming convention is applied consistently across
        all foreign keys in an entity.
        """
        # Ensure entity names are different
        if left_entity_name == right_entity_name:
            right_entity_name = f"{right_entity_name}Other"
        
        # Create left entity
        left_entity = Entity(
            name=left_entity_name,
            table_name=left_entity_name.lower(),
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False)
            ]
        )
        
        # Create right entity with multiple FK columns
        fk_columns = []
        relationships = []
        fk_names = []
        
        for i in range(num_fk_columns):
            fk_logical_name = f'fk_{i}'
            fk_db_column = f'fk_{i}_id'
            fk_names.append((fk_logical_name, fk_db_column))
            
            fk_columns.append(
                Column(name=fk_logical_name, type='bigint', db_column=fk_db_column, nullable=True)
            )
            relationships.append(
                Relationship(
                    left_entity=left_entity_name,
                    right_entity=right_entity_name,
                    relation_type='one-to-many',
                    left_column='id',
                    right_column=fk_db_column
                )
            )
        
        right_entity = Entity(
            name=right_entity_name,
            table_name=right_entity_name.lower(),
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False)
            ] + fk_columns
        )
        
        # Create ERModel
        model = ERModel(
            entities={
                left_entity_name: left_entity,
                right_entity_name: right_entity
            },
            relationships=relationships
        )
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Property: All foreign keys should follow Django-style naming
        for fk_logical_name, fk_db_column in fk_names:
            # Check column uses db_column
            column_pattern = rf'{re.escape(fk_db_column)}\s*=\s*Column\('
            assert re.search(column_pattern, generated_code), (
                f"Column definition for '{fk_db_column}' not found in generated code"
            )
            
            # Check relationship uses logical name
            relationship_pattern = rf'{re.escape(fk_logical_name)}\s*=\s*relationship\('
            assert re.search(relationship_pattern, generated_code), (
                f"Relationship definition for '{fk_logical_name}' not found in generated code"
            )
            
            # Check foreign_keys parameter
            foreign_keys_pattern = rf'foreign_keys\s*=\s*\[\s*{re.escape(fk_db_column)}\s*\]'
            assert re.search(foreign_keys_pattern, generated_code), (
                f"foreign_keys=[{fk_db_column}] not found in generated code"
            )
