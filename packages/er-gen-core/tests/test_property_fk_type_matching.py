"""
Property-based tests for Foreign Key type matching.

These tests use hypothesis to verify universal properties across many generated inputs.
Each test runs a minimum of 100 iterations.
"""
import re
import pytest
from hypothesis import given, settings, strategies as st, HealthCheck
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.models import ERModel, Entity, Column, Relationship
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer
from x007007007.er.type_mapper import TypeMapper


# Custom strategies for generating valid identifiers
safe_identifier = st.from_regex(r'[A-Z][a-zA-Z0-9]*', fullmatch=True).filter(lambda s: len(s) < 50)
safe_column_name = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(lambda s: len(s) < 30 and not s.endswith('_id'))


@st.composite
def fk_model_with_type_matching(draw):
    """
    Generate an ERModel with a foreign key that should match the referenced PK type.
    
    This strategy creates:
    - Two entities (left and right) with a relationship
    - A primary key in the left entity with a specific type
    - A foreign key column in the right entity that should match the PK type
    
    Returns a tuple of (model, left_entity_name, right_entity_name, pk_type, fk_db_column)
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
    
    # Choose a primary key type
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
    
    return model, left_entity_name, right_entity_name, pk_type, fk_db_column


class TestProperty4ForeignKeyTypeMatching:
    """
    Property 4: Foreign Key Type Matching
    
    **Validates: Requirements 5.3**
    
    For any foreign key column, the generated Column type (BigInteger, Integer, etc.)
    SHALL match the type of the referenced primary key column in the target entity.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(fk_model_with_type_matching())
    def test_foreign_key_type_matches_referenced_primary_key(self, test_data):
        """
        Test that FK column type matches the referenced PK column type.
        
        This verifies Requirement 5.3: THE Foreign_Key_Column SHALL use the correct
        SQLAlchemy column type (BigInteger, Integer, etc.) matching the referenced
        primary key.
        """
        model, left_entity_name, right_entity_name, pk_type, fk_db_column = test_data
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Get the expected SQLAlchemy type for the PK type
        expected_sqlalchemy_type, _ = TypeMapper.get_sqlalchemy_type(pk_type)
        
        # Property: The FK column should use the same type as the PK
        # Pattern: {fk_db_column} = Column({expected_type}, ForeignKey(...), ...)
        # We need to find the FK column definition and check its type
        
        # Find the FK column definition
        # Pattern needs to handle types with parentheses like String(255)
        # We need to match everything up to the first comma that's NOT inside parentheses
        fk_column_pattern = rf'{re.escape(fk_db_column)}\s*=\s*Column\(\s*([^,\(]+(?:\([^\)]*\))?)'
        match = re.search(fk_column_pattern, generated_code)
        
        assert match, (
            f"Could not find FK column definition for '{fk_db_column}' in generated code:\n{generated_code}"
        )
        
        actual_type = match.group(1).strip()
        
        # The actual type should match the expected type
        assert actual_type == expected_sqlalchemy_type, (
            f"FK column '{fk_db_column}' has type '{actual_type}', "
            f"but should match referenced PK type '{expected_sqlalchemy_type}' (from '{pk_type}')\n"
            f"Generated code:\n{generated_code}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        left_entity_name=safe_identifier,
        right_entity_name=safe_identifier,
        pk_type=st.sampled_from(['bigint', 'int', 'uuid', 'string']),
        fk_name=safe_column_name
    )
    def test_foreign_key_type_matches_for_various_types(self, left_entity_name, right_entity_name, pk_type, fk_name):
        """
        Test FK type matching for various column types (bigint, int, uuid, string).
        
        This ensures the type matching property holds for all common column types.
        """
        # Ensure entity names are different
        if left_entity_name == right_entity_name:
            right_entity_name = f"{right_entity_name}Other"
        
        fk_db_column = f"{fk_name}_id"
        left_table_name = left_entity_name.lower()
        right_table_name = right_entity_name.lower()
        left_pk_column = 'id'
        
        # Create entities
        left_entity = Entity(
            name=left_entity_name,
            table_name=left_table_name,
            columns=[
                Column(name=left_pk_column, type=pk_type, db_column=left_pk_column, is_pk=True, nullable=False, max_length=255 if pk_type == 'string' else None)
            ]
        )
        
        right_entity = Entity(
            name=right_entity_name,
            table_name=right_table_name,
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False),
                Column(name=fk_name, type=pk_type, db_column=fk_db_column, nullable=True, max_length=255 if pk_type == 'string' else None)
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
        
        # Mark foreign keys
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Get the expected SQLAlchemy type
        expected_sqlalchemy_type, _ = TypeMapper.get_sqlalchemy_type(pk_type, max_length=255 if pk_type == 'string' else None)
        
        # Find the FK column definition
        # Pattern needs to handle types with parentheses like String(255)
        # We need to match everything up to the first comma that's NOT inside parentheses
        fk_column_pattern = rf'{re.escape(fk_db_column)}\s*=\s*Column\(\s*([^,\(]+(?:\([^\)]*\))?)'
        match = re.search(fk_column_pattern, generated_code)
        
        assert match, (
            f"Could not find FK column definition for '{fk_db_column}' in generated code"
        )
        
        actual_type = match.group(1).strip()
        
        # The actual type should match the expected type
        assert actual_type == expected_sqlalchemy_type, (
            f"FK column '{fk_db_column}' has type '{actual_type}', "
            f"but should match referenced PK type '{expected_sqlalchemy_type}' (from '{pk_type}')"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        left_entity_name=safe_identifier,
        right_entity_name=safe_identifier,
        num_fk_columns=st.integers(min_value=2, max_value=4),
        pk_type=st.sampled_from(['bigint', 'int', 'uuid'])
    )
    def test_multiple_foreign_keys_all_match_referenced_type(self, left_entity_name, right_entity_name, num_fk_columns, pk_type):
        """
        Test that multiple FKs to the same entity all use the correct type.
        
        This verifies that type matching is applied consistently across all FKs.
        """
        # Ensure entity names are different
        if left_entity_name == right_entity_name:
            right_entity_name = f"{right_entity_name}Other"
        
        left_table_name = left_entity_name.lower()
        right_table_name = right_entity_name.lower()
        left_pk_column = 'id'
        
        # Create left entity with specific PK type
        left_entity = Entity(
            name=left_entity_name,
            table_name=left_table_name,
            columns=[
                Column(name=left_pk_column, type=pk_type, db_column=left_pk_column, is_pk=True, nullable=False)
            ]
        )
        
        # Create right entity with multiple FKs to left entity
        fk_columns = []
        relationships = []
        fk_names = []
        
        for i in range(num_fk_columns):
            fk_logical_name = f'fk_{i}'
            fk_db_column = f'fk_{i}_id'
            fk_names.append((fk_logical_name, fk_db_column))
            
            fk_columns.append(
                Column(name=fk_logical_name, type=pk_type, db_column=fk_db_column, nullable=True)
            )
            relationships.append(
                Relationship(
                    left_entity=left_entity_name,
                    right_entity=right_entity_name,
                    relation_type='one-to-many',
                    left_column=left_pk_column,
                    right_column=fk_db_column
                )
            )
        
        right_entity = Entity(
            name=right_entity_name,
            table_name=right_table_name,
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
        
        # Get the expected SQLAlchemy type
        expected_sqlalchemy_type, _ = TypeMapper.get_sqlalchemy_type(pk_type)
        
        # Property: All FK columns should use the same type as the referenced PK
        for fk_logical_name, fk_db_column in fk_names:
            # Pattern needs to handle types with parentheses like String(255)
            # We need to match everything up to the first comma that's NOT inside parentheses
            fk_column_pattern = rf'{re.escape(fk_db_column)}\s*=\s*Column\(\s*([^,\(]+(?:\([^\)]*\))?)'
            match = re.search(fk_column_pattern, generated_code)
            
            assert match, (
                f"Could not find FK column definition for '{fk_db_column}' in generated code"
            )
            
            actual_type = match.group(1).strip()
            
            assert actual_type == expected_sqlalchemy_type, (
                f"FK column '{fk_db_column}' has type '{actual_type}', "
                f"but should match referenced PK type '{expected_sqlalchemy_type}' (from '{pk_type}')"
            )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(fk_model_with_type_matching())
    def test_bigint_pk_requires_biginteger_fk(self, test_data):
        """
        Test that BigInteger PK requires BigInteger FK (not Integer).
        
        This is a specific case to ensure we don't accidentally use Integer
        when the PK is BigInteger.
        """
        model, left_entity_name, right_entity_name, pk_type, fk_db_column = test_data
        
        # Only test when PK type is bigint
        if pk_type != 'bigint':
            return
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Find the FK column definition
        # Pattern needs to handle types with parentheses like String(255)
        # We need to match everything up to the first comma that's NOT inside parentheses
        fk_column_pattern = rf'{re.escape(fk_db_column)}\s*=\s*Column\(\s*([^,\(]+(?:\([^\)]*\))?)'
        match = re.search(fk_column_pattern, generated_code)
        
        assert match, (
            f"Could not find FK column definition for '{fk_db_column}' in generated code"
        )
        
        actual_type = match.group(1).strip()
        
        # Property: When PK is bigint, FK must be BigInteger (not Integer)
        assert actual_type == 'BigInteger', (
            f"When PK type is 'bigint', FK column '{fk_db_column}' must use 'BigInteger', "
            f"but found '{actual_type}' instead"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(fk_model_with_type_matching())
    def test_int_pk_requires_integer_fk(self, test_data):
        """
        Test that Integer PK requires Integer FK (not BigInteger).
        
        This ensures we use the correct integer type based on the PK.
        """
        model, left_entity_name, right_entity_name, pk_type, fk_db_column = test_data
        
        # Only test when PK type is int
        if pk_type != 'int':
            return
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Find the FK column definition
        # Pattern needs to handle types with parentheses like String(255)
        # We need to match everything up to the first comma that's NOT inside parentheses
        fk_column_pattern = rf'{re.escape(fk_db_column)}\s*=\s*Column\(\s*([^,\(]+(?:\([^\)]*\))?)'
        match = re.search(fk_column_pattern, generated_code)
        
        assert match, (
            f"Could not find FK column definition for '{fk_db_column}' in generated code"
        )
        
        actual_type = match.group(1).strip()
        
        # Property: When PK is int, FK must be Integer (not BigInteger)
        assert actual_type == 'Integer', (
            f"When PK type is 'int', FK column '{fk_db_column}' must use 'Integer', "
            f"but found '{actual_type}' instead"
        )
