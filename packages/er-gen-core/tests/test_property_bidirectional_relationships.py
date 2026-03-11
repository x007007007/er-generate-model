"""
Property-based tests for bidirectional relationship configuration.

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
def bidirectional_relationship_model(draw, relation_type=None):
    """
    Generate an ERModel with a bidirectional relationship.
    
    This strategy creates:
    - Two entities (left and right)
    - A relationship between them with specified type
    - Appropriate columns for the relationship
    
    Returns a tuple of (model, left_entity_name, right_entity_name, relation_type, fk_logical_name, fk_db_column)
    """
    # Generate entity names
    left_entity_name = draw(safe_identifier)
    right_entity_name = draw(safe_identifier.filter(lambda x: x != left_entity_name))
    
    # Determine relationship type
    if relation_type is None:
        relation_type = draw(st.sampled_from(['one-to-one', 'one-to-many']))
    
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
        relation_type=relation_type,
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
    
    return model, left_entity_name, right_entity_name, relation_type, fk_logical_name, fk_db_column


class TestProperty5BidirectionalRelationships:
    """
    Property 5: Bidirectional Relationship Configuration
    
    **Validates: Requirements 3.1, 3.4, 5.2**
    
    For any relationship definition, the generator SHALL create relationship objects
    on both entities with correct back_populates parameters that reference each other,
    and the uselist parameter SHALL be set correctly based on the relationship type
    (False for one-to-one, True for one-to-many).
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(bidirectional_relationship_model())
    def test_both_entities_have_relationship_objects(self, test_data):
        """
        Test that both entities in a relationship have relationship objects.
        
        This verifies Requirement 3.1: WHEN a TOML definition includes a relationship
        with type = "one-to-many", THE Generator SHALL create appropriate
        Relationship_Objects on both entities.
        """
        model, left_entity_name, right_entity_name, relation_type, fk_logical_name, fk_db_column = test_data
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Find the left entity class definition
        left_class_pattern = rf'class {re.escape(left_entity_name)}\('
        left_class_match = re.search(left_class_pattern, generated_code)
        assert left_class_match, f"Left entity class '{left_entity_name}' not found in generated code"
        
        # Find the right entity class definition
        right_class_pattern = rf'class {re.escape(right_entity_name)}\('
        right_class_match = re.search(right_class_pattern, generated_code)
        assert right_class_match, f"Right entity class '{right_entity_name}' not found in generated code"
        
        # Extract the class bodies
        left_class_start = left_class_match.end()
        right_class_start = right_class_match.end()
        
        # Find where each class ends (next class definition or end of file)
        next_class_pattern = r'\nclass '
        left_class_end_match = re.search(next_class_pattern, generated_code[left_class_start:])
        if left_class_end_match:
            left_class_end = left_class_start + left_class_end_match.start()
        else:
            left_class_end = len(generated_code)
        
        right_class_end_match = re.search(next_class_pattern, generated_code[right_class_start:])
        if right_class_end_match:
            right_class_end = right_class_start + right_class_end_match.start()
        else:
            right_class_end = len(generated_code)
        
        left_class_body = generated_code[left_class_start:left_class_end]
        right_class_body = generated_code[right_class_start:right_class_end]
        
        # Property: Both entities should have relationship objects
        # Left entity should have a relationship (the "one" side)
        left_relationship_pattern = r'=\s*relationship\('
        assert re.search(left_relationship_pattern, left_class_body), (
            f"Left entity '{left_entity_name}' should have a relationship object, "
            f"but none found in:\n{left_class_body}"
        )
        
        # Right entity should have a relationship (the "many" side)
        right_relationship_pattern = r'=\s*relationship\('
        assert re.search(right_relationship_pattern, right_class_body), (
            f"Right entity '{right_entity_name}' should have a relationship object, "
            f"but none found in:\n{right_class_body}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(bidirectional_relationship_model())
    def test_back_populates_parameters_reference_each_other(self, test_data):
        """
        Test that back_populates parameters correctly reference each other.
        
        This verifies Requirement 3.4: THE Generator SHALL generate the back_populates
        parameter based on the relationship type and entity names.
        """
        model, left_entity_name, right_entity_name, relation_type, fk_logical_name, fk_db_column = test_data
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Extract relationship definitions
        # Pattern: relationship_name = relationship("TargetEntity", ..., back_populates="...", ...)
        relationship_pattern = r'(\w+)\s*=\s*relationship\([^)]+back_populates=["\']([^"\']+)["\'][^)]*\)'
        relationships = re.findall(relationship_pattern, generated_code)
        
        assert len(relationships) >= 2, (
            f"Expected at least 2 relationship definitions with back_populates, "
            f"but found {len(relationships)}: {relationships}"
        )
        
        # Build a mapping of relationship names to their back_populates values
        rel_map = {rel_name: back_pop for rel_name, back_pop in relationships}
        
        # Property: For each relationship, its back_populates should reference
        # another relationship that back_populates to it
        for rel_name, back_pop_name in relationships:
            # The back_populates should reference another relationship
            assert back_pop_name in rel_map, (
                f"Relationship '{rel_name}' has back_populates='{back_pop_name}', "
                f"but no relationship named '{back_pop_name}' exists. "
                f"Available relationships: {list(rel_map.keys())}"
            )
            
            # The referenced relationship should back_populate to this one
            reverse_back_pop = rel_map[back_pop_name]
            assert reverse_back_pop == rel_name, (
                f"Relationship '{rel_name}' has back_populates='{back_pop_name}', "
                f"but '{back_pop_name}' has back_populates='{reverse_back_pop}' "
                f"instead of '{rel_name}'. Bidirectional relationships must reference each other."
            )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(bidirectional_relationship_model(relation_type='one-to-one'))
    def test_one_to_one_has_uselist_false_on_both_sides(self, test_data):
        """
        Test that one-to-one relationships have uselist=False on both sides.
        
        This verifies Requirement 5.2: THE Relationship_Object SHALL use the correct
        relationship type (uselist parameter) based on the relationship definition.
        For one-to-one, uselist should be False on both sides.
        """
        model, left_entity_name, right_entity_name, relation_type, fk_logical_name, fk_db_column = test_data
        
        assert relation_type == 'one-to-one', "Test data should be one-to-one relationship"
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Find all relationship definitions
        relationship_pattern = r'(\w+)\s*=\s*relationship\(([^)]+)\)'
        relationships = re.findall(relationship_pattern, generated_code)
        
        assert len(relationships) >= 2, (
            f"Expected at least 2 relationship definitions for one-to-one, "
            f"but found {len(relationships)}"
        )
        
        # Property: For one-to-one relationships, both sides should have uselist=False
        for rel_name, rel_params in relationships:
            assert 'uselist=False' in rel_params, (
                f"One-to-one relationship '{rel_name}' should have uselist=False, "
                f"but it's missing in: {rel_params}"
            )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(bidirectional_relationship_model(relation_type='one-to-many'))
    def test_one_to_many_has_correct_uselist(self, test_data):
        """
        Test that one-to-many relationships have correct uselist parameter.
        
        This verifies Requirement 5.2: For one-to-many relationships:
        - The "many" side (with FK) should NOT have uselist=False (defaults to True)
        - The "one" side should have uselist=True (or omitted, as True is default)
        """
        model, left_entity_name, right_entity_name, relation_type, fk_logical_name, fk_db_column = test_data
        
        assert relation_type == 'one-to-many', "Test data should be one-to-many relationship"
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Find the right entity class (the "many" side with FK)
        right_class_pattern = rf'class {re.escape(right_entity_name)}\(.*?\):(.*?)(?=\nclass |\Z)'
        right_class_match = re.search(right_class_pattern, generated_code, re.DOTALL)
        assert right_class_match, f"Right entity class '{right_entity_name}' not found"
        right_class_body = right_class_match.group(1)
        
        # Find the left entity class (the "one" side)
        left_class_pattern = rf'class {re.escape(left_entity_name)}\(.*?\):(.*?)(?=\nclass |\Z)'
        left_class_match = re.search(left_class_pattern, generated_code, re.DOTALL)
        assert left_class_match, f"Left entity class '{left_entity_name}' not found"
        left_class_body = left_class_match.group(1)
        
        # Find relationship in right entity (many side - should NOT have uselist=False)
        right_rel_pattern = r'(\w+)\s*=\s*relationship\(([^)]+)\)'
        right_rel_match = re.search(right_rel_pattern, right_class_body)
        if right_rel_match:
            right_rel_params = right_rel_match.group(2)
            # Property: The "many" side should NOT have uselist=False
            # (it should either have uselist=True or omit it, as True is the default)
            assert 'uselist=False' not in right_rel_params, (
                f"One-to-many relationship on 'many' side should NOT have uselist=False, "
                f"but found it in: {right_rel_params}"
            )
        
        # Find relationship in left entity (one side - should have uselist=True or omitted)
        left_rel_pattern = r'(\w+)\s*=\s*relationship\(([^)]+)\)'
        left_rel_match = re.search(left_rel_pattern, left_class_body)
        if left_rel_match:
            left_rel_params = left_rel_match.group(2)
            # Property: The "one" side should NOT have uselist=False
            # (it represents a collection, so uselist should be True or omitted)
            assert 'uselist=False' not in left_rel_params, (
                f"One-to-many relationship on 'one' side should NOT have uselist=False, "
                f"but found it in: {left_rel_params}"
            )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(bidirectional_relationship_model())
    def test_relationship_names_are_unique_within_entity(self, test_data):
        """
        Test that relationship names are unique within each entity.
        
        This ensures that the generator creates valid Python code without
        duplicate attribute names.
        """
        model, left_entity_name, right_entity_name, relation_type, fk_logical_name, fk_db_column = test_data
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Extract each entity class
        for entity_name in [left_entity_name, right_entity_name]:
            class_pattern = rf'class {re.escape(entity_name)}\(.*?\):(.*?)(?=\nclass |\Z)'
            class_match = re.search(class_pattern, generated_code, re.DOTALL)
            assert class_match, f"Entity class '{entity_name}' not found"
            class_body = class_match.group(1)
            
            # Find all attribute definitions (columns and relationships)
            attr_pattern = r'^\s+(\w+)\s*='
            attributes = re.findall(attr_pattern, class_body, re.MULTILINE)
            
            # Property: All attribute names should be unique
            seen = set()
            duplicates = []
            for attr in attributes:
                if attr in seen:
                    duplicates.append(attr)
                seen.add(attr)
            
            assert not duplicates, (
                f"Entity '{entity_name}' has duplicate attribute names: {duplicates}. "
                f"All attributes must be unique.\nClass body:\n{class_body}"
            )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(bidirectional_relationship_model())
    def test_foreign_keys_parameter_present_on_many_side(self, test_data):
        """
        Test that the relationship on the "many" side includes foreign_keys parameter.
        
        This verifies that Django-style naming works correctly with bidirectional
        relationships - the side with the FK column should have foreign_keys parameter.
        """
        model, left_entity_name, right_entity_name, relation_type, fk_logical_name, fk_db_column = test_data
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Find the right entity class (the side with FK)
        right_class_pattern = rf'class {re.escape(right_entity_name)}\(.*?\):(.*?)(?=\nclass |\Z)'
        right_class_match = re.search(right_class_pattern, generated_code, re.DOTALL)
        assert right_class_match, f"Right entity class '{right_entity_name}' not found"
        right_class_body = right_class_match.group(1)
        
        # Find relationship in right entity
        right_rel_pattern = r'(\w+)\s*=\s*relationship\(([^)]+)\)'
        right_rel_match = re.search(right_rel_pattern, right_class_body)
        assert right_rel_match, f"No relationship found in right entity '{right_entity_name}'"
        
        right_rel_params = right_rel_match.group(2)
        
        # Property: The relationship should include foreign_keys parameter
        foreign_keys_pattern = rf'foreign_keys\s*=\s*\[\s*{re.escape(fk_db_column)}\s*\]'
        assert re.search(foreign_keys_pattern, right_rel_params), (
            f"Relationship in '{right_entity_name}' should have foreign_keys=[{fk_db_column}], "
            f"but it's missing in: {right_rel_params}"
        )
