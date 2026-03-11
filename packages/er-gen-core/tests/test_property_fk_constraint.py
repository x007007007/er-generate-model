"""
Property-based tests for Foreign Key constraint correctness.

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
safe_table_prefix = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(lambda s: len(s) < 20)


@st.composite
def fk_model_with_optional_prefix(draw):
    """
    Generate an ERModel with a foreign key relationship and optional table prefix.
    
    This strategy creates:
    - Two entities (left and right) with a relationship
    - Optional table prefix
    - A foreign key column in the right entity
    
    Returns a tuple of (model, left_table_name, left_pk_column, table_prefix)
    """
    # Generate entity names
    left_entity_name = draw(safe_identifier)
    right_entity_name = draw(safe_identifier.filter(lambda x: x != left_entity_name))
    
    # Generate column names
    left_pk_column = draw(st.sampled_from(['id', 'pk', 'uuid']))
    fk_logical_name = draw(safe_column_name)
    fk_db_column = f"{fk_logical_name}_id"
    
    # Generate table names
    left_table_name = left_entity_name.lower()
    right_table_name = right_entity_name.lower()
    
    # Optionally generate table prefix
    has_prefix = draw(st.booleans())
    table_prefix = draw(safe_table_prefix) if has_prefix else None
    
    # Determine column types
    pk_type = draw(st.sampled_from(['bigint', 'int', 'uuid']))
    
    # Create entities
    left_entity = Entity(
        name=left_entity_name,
        table_name=left_table_name,
        columns=[
            Column(name=left_pk_column, type=pk_type, db_column=left_pk_column, is_pk=True, nullable=False)
        ]
    )
    
    right_entity = Entity(
        name=right_entity_name,
        table_name=right_table_name,
        columns=[
            Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False),
            Column(name=fk_logical_name, type=pk_type, db_column=fk_db_column, nullable=True)
        ]
    )
    
    # Create relationship
    relationship = Relationship(
        left_entity=left_entity_name,
        right_entity=right_entity_name,
        relation_type='one-to-many',
        left_column=left_pk_column,
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
    
    return model, left_table_name, left_pk_column, table_prefix


class TestProperty3ForeignKeyConstraintCorrectness:
    """
    Property 3: Foreign Key Constraint Correctness
    
    **Validates: Requirements 2.2, 3.3, 5.4, 7.1, 7.2, 7.3**
    
    For any relationship definition, the generated ForeignKey constraint SHALL
    reference the correct target table and column in the format:
    - {table_prefix}_{table_name}.{column_name} when table_prefix is configured
    - {table_name}.{column_name} when table_prefix is not configured
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(fk_model_with_optional_prefix())
    def test_foreign_key_references_correct_table_and_column(self, test_data):
        """
        Test that ForeignKey constraint references the correct target table and column.
        
        This verifies that the generated ForeignKey constraint uses the correct format
        based on whether a table prefix is configured.
        """
        model, left_table_name, left_pk_column, table_prefix = test_data
        
        # Generate SQLAlchemy code with table_prefix
        renderer = SQLAlchemyRenderer(table_prefix=table_prefix or '')
        generated_code = renderer.render(model)
        
        # Determine expected ForeignKey reference format
        if table_prefix:
            expected_fk_ref = f"{table_prefix}_{left_table_name}.{left_pk_column}"
        else:
            expected_fk_ref = f"{left_table_name}.{left_pk_column}"
        
        # Property: The generated code should contain ForeignKey with correct reference
        # Pattern: ForeignKey('{expected_fk_ref}')
        fk_pattern = rf"ForeignKey\(['\"]({re.escape(expected_fk_ref)})['\"]"
        
        assert re.search(fk_pattern, generated_code), (
            f"Generated code should contain ForeignKey('{expected_fk_ref}'), "
            f"but pattern '{fk_pattern}' not found in:\n{generated_code}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(fk_model_with_optional_prefix())
    def test_foreign_key_format_with_table_prefix(self, test_data):
        """
        Test that ForeignKey uses {prefix}_{table}.{column} format when prefix is configured.
        
        This specifically validates Requirement 7.2: THE Generator SHALL construct
        ForeignKey references as {prefix}_{table_name}.{column_name} when prefix is present.
        """
        model, left_table_name, left_pk_column, table_prefix = test_data
        
        # Only test when table_prefix is configured
        if not table_prefix:
            return
        
        # Generate SQLAlchemy code with table_prefix
        renderer = SQLAlchemyRenderer(table_prefix=table_prefix)
        generated_code = renderer.render(model)
        
        # Expected format with prefix
        expected_fk_ref = f"{table_prefix}_{left_table_name}.{left_pk_column}"
        
        # Property: ForeignKey should use prefix format
        fk_pattern = rf"ForeignKey\(['\"]({re.escape(expected_fk_ref)})['\"]"
        
        assert re.search(fk_pattern, generated_code), (
            f"When table_prefix='{table_prefix}' is configured, "
            f"ForeignKey should use format '{expected_fk_ref}', "
            f"but not found in:\n{generated_code}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(fk_model_with_optional_prefix())
    def test_foreign_key_format_without_table_prefix(self, test_data):
        """
        Test that ForeignKey uses {table}.{column} format when prefix is not configured.
        
        This specifically validates Requirement 7.3: THE Generator SHALL construct
        ForeignKey references as {table_name}.{column_name} when prefix is absent.
        """
        model, left_table_name, left_pk_column, table_prefix = test_data
        
        # Only test when table_prefix is NOT configured
        if table_prefix:
            return
        
        # Generate SQLAlchemy code without table_prefix
        renderer = SQLAlchemyRenderer(table_prefix='')
        generated_code = renderer.render(model)
        
        # Expected format without prefix
        expected_fk_ref = f"{left_table_name}.{left_pk_column}"
        
        # Property: ForeignKey should use simple format
        fk_pattern = rf"ForeignKey\(['\"]({re.escape(expected_fk_ref)})['\"]"
        
        assert re.search(fk_pattern, generated_code), (
            f"When table_prefix is not configured, "
            f"ForeignKey should use format '{expected_fk_ref}', "
            f"but not found in:\n{generated_code}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(fk_model_with_optional_prefix())
    def test_foreign_key_references_correct_column_type(self, test_data):
        """
        Test that ForeignKey references the correct column in the target table.
        
        This verifies Requirement 3.3: THE Generator SHALL use the relationship's
        left_entity to determine the target entity for the ForeignKey constraint.
        """
        model, left_table_name, left_pk_column, table_prefix = test_data
        
        # Generate SQLAlchemy code with table_prefix
        renderer = SQLAlchemyRenderer(table_prefix=table_prefix or '')
        generated_code = renderer.render(model)
        
        # The ForeignKey should reference the left_pk_column (not always 'id')
        # Build the expected reference
        if table_prefix:
            table_ref = f"{table_prefix}_{left_table_name}"
        else:
            table_ref = left_table_name
        
        expected_column_ref = f"{table_ref}.{left_pk_column}"
        
        # Property: ForeignKey should reference the correct column
        fk_pattern = rf"ForeignKey\(['\"]({re.escape(expected_column_ref)})['\"]"
        
        assert re.search(fk_pattern, generated_code), (
            f"ForeignKey should reference column '{left_pk_column}' in table '{table_ref}', "
            f"but pattern not found in:\n{generated_code}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        table_prefix=safe_table_prefix,
        num_relationships=st.integers(min_value=2, max_value=4)
    )
    def test_table_prefix_applied_consistently_to_all_relationships(self, table_prefix, num_relationships):
        """
        Test that table prefix is applied consistently to all ForeignKey constraints.
        
        This validates Requirement 7.4: THE Generator SHALL apply table prefixes
        consistently across all relationship definitions.
        """
        # Create multiple entities and relationships
        entities = {}
        relationships = []
        
        # Create a central entity that others reference
        central_entity_name = 'Central'
        central_table_name = 'central'
        entities[central_entity_name] = Entity(
            name=central_entity_name,
            table_name=central_table_name,
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False)
            ]
        )
        
        # Create multiple entities with FKs to the central entity
        for i in range(num_relationships):
            entity_name = f'Entity{i}'
            table_name = f'entity{i}'
            fk_name = f'central_fk'
            fk_db_column = f'{fk_name}_id'
            
            entities[entity_name] = Entity(
                name=entity_name,
                table_name=table_name,
                columns=[
                    Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False),
                    Column(name=fk_name, type='bigint', db_column=fk_db_column, nullable=True)
                ]
            )
            
            relationships.append(
                Relationship(
                    left_entity=central_entity_name,
                    right_entity=entity_name,
                    relation_type='one-to-many',
                    left_column='id',
                    right_column=fk_db_column
                )
            )
        
        # Create ERModel with table prefix
        model = ERModel(
            entities=entities,
            relationships=relationships
        )
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code with table_prefix
        renderer = SQLAlchemyRenderer(table_prefix=table_prefix)
        generated_code = renderer.render(model)
        
        # Expected ForeignKey reference with prefix
        expected_fk_ref = f"{table_prefix}_{central_table_name}.id"
        
        # Property: All ForeignKey constraints should use the same prefix format
        # Count occurrences of the expected ForeignKey reference
        fk_pattern = rf"ForeignKey\(['\"]({re.escape(expected_fk_ref)})['\"]"
        matches = re.findall(fk_pattern, generated_code)
        
        assert len(matches) == num_relationships, (
            f"Expected {num_relationships} ForeignKey references to '{expected_fk_ref}', "
            f"but found {len(matches)} in:\n{generated_code}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        left_entity_name=safe_identifier,
        right_entity_name=safe_identifier,
        left_pk_column=st.sampled_from(['id', 'pk', 'uuid', 'entity_id']),
        fk_name=safe_column_name
    )
    def test_foreign_key_references_non_standard_primary_key(self, left_entity_name, right_entity_name, left_pk_column, fk_name):
        """
        Test that ForeignKey correctly references non-standard primary key columns.
        
        This verifies that the generator doesn't assume 'id' as the primary key
        and correctly uses the actual primary key column name from the relationship.
        """
        # Ensure entity names are different
        if left_entity_name == right_entity_name:
            right_entity_name = f"{right_entity_name}Other"
        
        fk_db_column = f"{fk_name}_id"
        left_table_name = left_entity_name.lower()
        right_table_name = right_entity_name.lower()
        
        # Create entities
        left_entity = Entity(
            name=left_entity_name,
            table_name=left_table_name,
            columns=[
                Column(name=left_pk_column, type='bigint', db_column=left_pk_column, is_pk=True, nullable=False)
            ]
        )
        
        right_entity = Entity(
            name=right_entity_name,
            table_name=right_table_name,
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False),
                Column(name=fk_name, type='bigint', db_column=fk_db_column, nullable=True)
            ]
        )
        
        # Create relationship referencing the non-standard PK
        relationship = Relationship(
            left_entity=left_entity_name,
            right_entity=right_entity_name,
            relation_type='one-to-many',
            left_column=left_pk_column,
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
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code without table_prefix
        renderer = SQLAlchemyRenderer(table_prefix='')
        generated_code = renderer.render(model)
        
        # Expected ForeignKey reference
        expected_fk_ref = f"{left_table_name}.{left_pk_column}"
        
        # Property: ForeignKey should reference the actual PK column, not assume 'id'
        fk_pattern = rf"ForeignKey\(['\"]({re.escape(expected_fk_ref)})['\"]"
        
        assert re.search(fk_pattern, generated_code), (
            f"ForeignKey should reference '{expected_fk_ref}' (the actual PK column), "
            f"but pattern not found in:\n{generated_code}"
        )
