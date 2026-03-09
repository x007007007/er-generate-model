"""
Property-based tests for Django-style foreign key detection.

These tests use hypothesis to verify universal properties across many generated inputs.
Each test runs a minimum of 100 iterations.
"""
import pytest
from hypothesis import given, settings, strategies as st, HealthCheck
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.models import ERModel, Entity, Column, Relationship


# Custom strategies for generating valid identifiers
safe_identifier = st.from_regex(r'[A-Z][a-zA-Z0-9]*', fullmatch=True).filter(lambda s: len(s) < 50)
safe_column_name = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(lambda s: len(s) < 30 and not s.endswith('_id'))


@st.composite
def relationship_with_fk_column(draw):
    """
    Generate a relationship with corresponding foreign key column.
    
    This strategy creates:
    - Two entities (left and right)
    - A relationship between them
    - A column in the right entity that should be marked as FK
    
    Returns a tuple of (left_entity, right_entity, relationship, fk_column_name, match_type)
    where match_type is either 'name' or 'db_column' indicating which field should match.
    """
    # Generate entity names
    left_entity_name = draw(safe_identifier)
    right_entity_name = draw(safe_identifier.filter(lambda x: x != left_entity_name))
    
    # Generate column names
    pk_column_name = 'id'
    fk_logical_name = draw(safe_column_name)
    
    # Decide whether to test matching by name or db_column
    match_type = draw(st.sampled_from(['name', 'db_column', 'both']))
    
    if match_type == 'name':
        # Relationship's right_column matches the column's name
        right_column = fk_logical_name
        fk_db_column = fk_logical_name  # Initially same as name, will be inferred to name_id
    elif match_type == 'db_column':
        # Relationship's right_column matches the column's db_column
        right_column = f"{fk_logical_name}_id"
        fk_db_column = f"{fk_logical_name}_id"  # Explicitly set to match right_column
    else:  # both
        # Both name and db_column could match
        right_column = fk_logical_name
        fk_db_column = fk_logical_name  # Initially same as name, will be inferred to name_id
    
    # Create entities
    left_entity = Entity(
        name=left_entity_name,
        table_name=left_entity_name.lower(),
        columns=[
            Column(name=pk_column_name, type='int', db_column=pk_column_name, is_pk=True, nullable=False)
        ]
    )
    
    right_entity = Entity(
        name=right_entity_name,
        table_name=right_entity_name.lower(),
        columns=[
            Column(name='id', type='int', db_column='id', is_pk=True, nullable=False),
            Column(name=fk_logical_name, type='int', db_column=fk_db_column, nullable=True)
        ]
    )
    
    # Create relationship
    relationship = Relationship(
        left_entity=left_entity_name,
        right_entity=right_entity_name,
        relation_type=draw(st.sampled_from(['one-to-many', 'one-to-one', 'many-to-one'])),
        left_column=pk_column_name,
        right_column=right_column
    )
    
    return left_entity, right_entity, relationship, fk_logical_name, match_type


class TestProperty8ForeignKeyDetection:
    """
    Property 8: Foreign Key Detection from Relationships
    
    **Validates: Requirements 3.2**
    
    For any column where the column's name or db_column matches a relationship's
    right_column, the generator SHALL mark that column as a foreign key (is_fk=True)
    and generate appropriate ForeignKey constraint.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(relationship_with_fk_column())
    def test_foreign_key_detection_marks_column_as_fk(self, test_data):
        """
        Test that columns matching relationship's right_column are marked as foreign keys.
        
        This test verifies that the _mark_foreign_keys method correctly identifies
        foreign key columns by matching against both the column's name and db_column
        attributes.
        """
        left_entity, right_entity, relationship, fk_column_name, match_type = test_data
        
        # Create ERModel
        model = ERModel(
            entities={
                left_entity.name: left_entity,
                right_entity.name: right_entity
            },
            relationships=[relationship]
        )
        
        # Apply foreign key detection (simulating what the parser does)
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Find the FK column in the right entity
        fk_column = None
        for col in right_entity.columns:
            if col.name == fk_column_name:
                fk_column = col
                break
        
        assert fk_column is not None, f"FK column '{fk_column_name}' not found in entity"
        
        # Property: The column should be marked as a foreign key
        assert fk_column.is_fk is True, (
            f"Column '{fk_column_name}' should be marked as FK when relationship's "
            f"right_column='{relationship.right_column}' matches (match_type={match_type})"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(relationship_with_fk_column())
    def test_foreign_key_detection_infers_db_column(self, test_data):
        """
        Test that db_column is inferred as {name}_id for FK columns without explicit db_column.
        
        This test verifies that when a column is marked as a foreign key and its db_column
        equals its name (wasn't explicitly set), the parser infers db_column as {name}_id
        following Django-style conventions.
        """
        left_entity, right_entity, relationship, fk_column_name, match_type = test_data
        
        # Only test when matching by name (db_column should be inferred)
        if match_type != 'name' and match_type != 'both':
            return
        
        # Create ERModel
        model = ERModel(
            entities={
                left_entity.name: left_entity,
                right_entity.name: right_entity
            },
            relationships=[relationship]
        )
        
        # Apply foreign key detection
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Find the FK column
        fk_column = None
        for col in right_entity.columns:
            if col.name == fk_column_name:
                fk_column = col
                break
        
        assert fk_column is not None
        
        # Property: db_column should be inferred as {name}_id
        expected_db_column = f"{fk_column_name}_id"
        assert fk_column.db_column == expected_db_column, (
            f"FK column db_column should be inferred as '{expected_db_column}', "
            f"but got '{fk_column.db_column}'"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(relationship_with_fk_column())
    def test_foreign_key_type_matches_referenced_column(self, test_data):
        """
        Test that FK column type is set to match the referenced primary key type.
        
        This test verifies that when a foreign key is detected, its type is updated
        to match the type of the column it references in the left entity.
        """
        left_entity, right_entity, relationship, fk_column_name, match_type = test_data
        
        # Create ERModel
        model = ERModel(
            entities={
                left_entity.name: left_entity,
                right_entity.name: right_entity
            },
            relationships=[relationship]
        )
        
        # Get the referenced column type
        ref_column = None
        for col in left_entity.columns:
            if col.name == relationship.left_column:
                ref_column = col
                break
        
        assert ref_column is not None
        ref_type = ref_column.type
        
        # Apply foreign key detection
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Find the FK column
        fk_column = None
        for col in right_entity.columns:
            if col.name == fk_column_name:
                fk_column = col
                break
        
        assert fk_column is not None
        
        # Property: FK column type should match referenced column type
        assert fk_column.type == ref_type, (
            f"FK column type should match referenced column type '{ref_type}', "
            f"but got '{fk_column.type}'"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        entity_name=safe_identifier,
        num_fk_columns=st.integers(min_value=2, max_value=4)
    )
    def test_multiple_foreign_keys_all_marked(self, entity_name, num_fk_columns):
        """
        Test that multiple foreign key columns in the same entity are all marked correctly.
        
        This test verifies that when an entity has multiple foreign key relationships,
        all corresponding columns are correctly identified and marked as foreign keys.
        """
        # Create a target entity
        target_entity = Entity(
            name='Target',
            table_name='target',
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False)
            ]
        )
        
        # Create an entity with multiple FK columns
        fk_columns = []
        relationships = []
        
        for i in range(num_fk_columns):
            fk_name = f'fk_{i}'
            fk_columns.append(
                Column(name=fk_name, type='int', db_column=fk_name, nullable=True)
            )
            relationships.append(
                Relationship(
                    left_entity='Target',
                    right_entity=entity_name,
                    relation_type='one-to-many',
                    left_column='id',
                    right_column=fk_name
                )
            )
        
        entity = Entity(
            name=entity_name,
            table_name=entity_name.lower(),
            columns=[
                Column(name='id', type='int', db_column='id', is_pk=True, nullable=False)
            ] + fk_columns
        )
        
        # Create ERModel
        model = ERModel(
            entities={
                'Target': target_entity,
                entity_name: entity
            },
            relationships=relationships
        )
        
        # Apply foreign key detection
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Property: All FK columns should be marked
        marked_fk_count = sum(1 for col in entity.columns if col.is_fk)
        assert marked_fk_count == num_fk_columns, (
            f"Expected {num_fk_columns} columns to be marked as FK, "
            f"but only {marked_fk_count} were marked"
        )
        
        # Verify each specific FK column is marked
        for i in range(num_fk_columns):
            fk_name = f'fk_{i}'
            fk_col = next((col for col in entity.columns if col.name == fk_name), None)
            assert fk_col is not None
            assert fk_col.is_fk is True, f"Column '{fk_name}' should be marked as FK"
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        entity_name=safe_identifier,
        fk_name=safe_column_name,
        non_fk_name=safe_column_name
    )
    def test_non_foreign_key_columns_not_marked(self, entity_name, fk_name, non_fk_name):
        """
        Test that columns not referenced in relationships are not marked as foreign keys.
        
        This test verifies that the FK detection is precise and doesn't incorrectly
        mark columns that are not part of any relationship.
        """
        # Ensure names are different
        if fk_name == non_fk_name:
            non_fk_name = f"{non_fk_name}_other"
        
        # Create entities
        target_entity = Entity(
            name='Target',
            table_name='target',
            columns=[
                Column(name='id', type='int', db_column='id', is_pk=True, nullable=False)
            ]
        )
        
        entity = Entity(
            name=entity_name,
            table_name=entity_name.lower(),
            columns=[
                Column(name='id', type='int', db_column='id', is_pk=True, nullable=False),
                Column(name=fk_name, type='int', db_column=fk_name, nullable=True),
                Column(name=non_fk_name, type='int', db_column=non_fk_name, nullable=True)
            ]
        )
        
        # Create relationship only for fk_name
        relationship = Relationship(
            left_entity='Target',
            right_entity=entity_name,
            relation_type='one-to-many',
            left_column='id',
            right_column=fk_name
        )
        
        # Create ERModel
        model = ERModel(
            entities={
                'Target': target_entity,
                entity_name: entity
            },
            relationships=[relationship]
        )
        
        # Apply foreign key detection
        parser = TomlERParser()
        parser._mark_foreign_keys(model.entities, model.relationships)
        
        # Find columns
        fk_col = next((col for col in entity.columns if col.name == fk_name), None)
        non_fk_col = next((col for col in entity.columns if col.name == non_fk_name), None)
        
        assert fk_col is not None
        assert non_fk_col is not None
        
        # Property: FK column should be marked, non-FK column should not be marked
        assert fk_col.is_fk is True, f"Column '{fk_name}' should be marked as FK"
        assert non_fk_col.is_fk is False, (
            f"Column '{non_fk_name}' should NOT be marked as FK "
            f"(it's not referenced in any relationship)"
        )
