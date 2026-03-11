"""
Property-based tests for Foreign Key column attribute preservation.

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
def fk_model_with_attributes(draw):
    """
    Generate an ERModel with a foreign key that has various attributes.
    
    This strategy creates:
    - Two entities (left and right) with a relationship
    - A foreign key column in the right entity with random attributes
    
    Returns a tuple of (model, right_entity_name, fk_db_column, attributes_dict)
    """
    # Generate entity names
    left_entity_name = draw(safe_identifier)
    right_entity_name = draw(safe_identifier.filter(lambda x: x != left_entity_name))
    
    # Generate column names
    left_pk_column = 'id'
    fk_logical_name = draw(safe_column_name)
    fk_db_column = f"{fk_logical_name}_id"
    
    # Generate table names
    left_table_name = left_entity_name.lower()
    right_table_name = right_entity_name.lower()
    
    # Generate random attributes for the FK column
    nullable = draw(st.booleans())
    unique = draw(st.booleans())
    indexed = draw(st.booleans())
    has_default = draw(st.booleans())
    has_comment = draw(st.booleans())
    
    # Generate default value if needed
    default = str(draw(st.integers(min_value=1, max_value=100))) if has_default else None
    
    # Generate comment if needed
    comment = draw(st.text(min_size=5, max_size=50).filter(lambda x: '"' not in x and "'" not in x)) if has_comment else None
    
    # Determine column types
    pk_type = draw(st.sampled_from(['bigint', 'int']))
    
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
            Column(
                name=fk_logical_name,
                type=pk_type,
                db_column=fk_db_column,
                nullable=nullable,
                unique=unique,
                indexed=indexed,
                default=default,
                comment=comment
            )
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
    
    # Store attributes for verification
    attributes = {
        'nullable': nullable,
        'unique': unique,
        'indexed': indexed,
        'default': default,
        'comment': comment
    }
    
    return model, right_entity_name, fk_db_column, attributes


class TestProperty2ForeignKeyAttributePreservation:
    """
    Property 2: Foreign Key Column Attributes Preservation
    
    **Validates: Requirements 2.3**
    
    For any foreign key column with attributes (nullable, unique, indexed, default, comment),
    the generated Column definition SHALL preserve all specified attributes in addition to
    the ForeignKey constraint.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(fk_model_with_attributes())
    def test_foreign_key_preserves_all_attributes(self, test_data):
        """
        Test that FK columns preserve all attributes (nullable, unique, indexed, default, comment).
        
        This verifies Requirement 2.3: THE Foreign_Key_Column SHALL preserve all column
        attributes (nullable, unique, indexed, default, comment).
        """
        model, right_entity_name, fk_db_column, attributes = test_data
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Find the FK column definition
        # We need to extract the entire Column(...) definition
        column_start = generated_code.find(f'{fk_db_column} = Column(')
        assert column_start != -1, f"Column definition for '{fk_db_column}' not found in generated code"
        
        # Find the closing parenthesis for this Column definition
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
        
        # Property: All specified attributes should be preserved in the column definition
        
        # Check nullable
        if attributes['nullable']:
            assert 'nullable=True' in column_definition, (
                f"FK column '{fk_db_column}' should preserve nullable=True, "
                f"but not found in:\n{column_definition}"
            )
        else:
            assert 'nullable=False' in column_definition, (
                f"FK column '{fk_db_column}' should preserve nullable=False, "
                f"but not found in:\n{column_definition}"
            )
        
        # Check unique
        if attributes['unique']:
            assert 'unique=True' in column_definition, (
                f"FK column '{fk_db_column}' should preserve unique=True, "
                f"but not found in:\n{column_definition}"
            )
        
        # Check indexed
        if attributes['indexed']:
            assert 'index=True' in column_definition, (
                f"FK column '{fk_db_column}' should preserve index=True, "
                f"but not found in:\n{column_definition}"
            )
        
        # Check default
        if attributes['default'] is not None:
            assert 'default=' in column_definition, (
                f"FK column '{fk_db_column}' should preserve default value, "
                f"but not found in:\n{column_definition}"
            )
        
        # Check comment
        if attributes['comment'] is not None:
            assert 'comment=' in column_definition, (
                f"FK column '{fk_db_column}' should preserve comment, "
                f"but not found in:\n{column_definition}"
            )
        
        # Property: ForeignKey constraint should also be present
        assert 'ForeignKey' in column_definition, (
            f"FK column '{fk_db_column}' should include ForeignKey constraint, "
            f"but not found in:\n{column_definition}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(fk_model_with_attributes())
    def test_foreign_key_constraint_not_overridden_by_attributes(self, test_data):
        """
        Test that column attributes don't override or remove the ForeignKey constraint.
        
        This verifies that the ForeignKey constraint is correctly rendered alongside
        all the column attributes.
        """
        model, right_entity_name, fk_db_column, attributes = test_data
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        generated_code = renderer.render(model)
        
        # Find the FK column definition
        column_start = generated_code.find(f'{fk_db_column} = Column(')
        assert column_start != -1, f"Column definition for '{fk_db_column}' not found"
        
        # Find the closing parenthesis
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
        
        # Property: ForeignKey constraint must be present regardless of other attributes
        assert 'ForeignKey' in column_definition, (
            f"FK column '{fk_db_column}' must include ForeignKey constraint even with attributes, "
            f"but not found in:\n{column_definition}"
        )
        
        # Verify the ForeignKey references the correct table
        # Get the left entity to find the table name
        left_entity_name = list(model.entities.keys())[0]
        left_table_name = model.entities[left_entity_name].table_name
        
        fk_reference_pattern = rf"ForeignKey\(['\"]({re.escape(left_table_name)}\.id)['\"]"
        assert re.search(fk_reference_pattern, column_definition), (
            f"ForeignKey should reference '{left_table_name}.id', "
            f"but pattern not found in:\n{column_definition}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        left_entity_name=safe_identifier,
        right_entity_name=safe_identifier,
        fk_name=safe_column_name,
        nullable=st.booleans(),
        unique=st.booleans()
    )
    def test_nullable_and_unique_preserved_together(self, left_entity_name, right_entity_name, fk_name, nullable, unique):
        """
        Test that nullable and unique attributes are preserved together.
        
        This is a common combination for one-to-one relationships.
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
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False)
            ]
        )
        
        right_entity = Entity(
            name=right_entity_name,
            table_name=right_table_name,
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False),
                Column(
                    name=fk_name,
                    type='bigint',
                    db_column=fk_db_column,
                    nullable=nullable,
                    unique=unique
                )
            ]
        )
        
        # Create relationship
        relationship = Relationship(
            left_entity=left_entity_name,
            right_entity=right_entity_name,
            relation_type='one-to-one' if unique else 'one-to-many',
            left_column='id',
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
        
        # Find the FK column definition
        column_start = generated_code.find(f'{fk_db_column} = Column(')
        assert column_start != -1, f"Column definition for '{fk_db_column}' not found"
        
        # Extract column definition
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
        
        # Property: Both nullable and unique should be preserved
        if nullable:
            assert 'nullable=True' in column_definition, (
                f"FK column should preserve nullable=True"
            )
        else:
            assert 'nullable=False' in column_definition, (
                f"FK column should preserve nullable=False"
            )
        
        if unique:
            assert 'unique=True' in column_definition, (
                f"FK column should preserve unique=True"
            )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        left_entity_name=safe_identifier,
        right_entity_name=safe_identifier,
        fk_name=safe_column_name,
        indexed=st.booleans(),
        has_comment=st.booleans()
    )
    def test_indexed_and_comment_preserved_together(self, left_entity_name, right_entity_name, fk_name, indexed, has_comment):
        """
        Test that indexed and comment attributes are preserved together.
        
        This is a common combination for performance-optimized foreign keys.
        """
        # Ensure entity names are different
        if left_entity_name == right_entity_name:
            right_entity_name = f"{right_entity_name}Other"
        
        fk_db_column = f"{fk_name}_id"
        left_table_name = left_entity_name.lower()
        right_table_name = right_entity_name.lower()
        
        # Generate comment if needed
        comment = "FK reference for performance" if has_comment else None
        
        # Create entities
        left_entity = Entity(
            name=left_entity_name,
            table_name=left_table_name,
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False)
            ]
        )
        
        right_entity = Entity(
            name=right_entity_name,
            table_name=right_table_name,
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False),
                Column(
                    name=fk_name,
                    type='bigint',
                    db_column=fk_db_column,
                    nullable=True,
                    indexed=indexed,
                    comment=comment
                )
            ]
        )
        
        # Create relationship
        relationship = Relationship(
            left_entity=left_entity_name,
            right_entity=right_entity_name,
            relation_type='one-to-many',
            left_column='id',
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
        
        # Find the FK column definition
        column_start = generated_code.find(f'{fk_db_column} = Column(')
        assert column_start != -1, f"Column definition for '{fk_db_column}' not found"
        
        # Extract column definition
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
        
        # Property: Both indexed and comment should be preserved
        if indexed:
            assert 'index=True' in column_definition, (
                f"FK column should preserve index=True"
            )
        
        if has_comment:
            assert 'comment=' in column_definition, (
                f"FK column should preserve comment"
            )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        num_fk_columns=st.integers(min_value=2, max_value=4),
        all_nullable=st.booleans(),
        all_indexed=st.booleans()
    )
    def test_multiple_foreign_keys_all_preserve_attributes(self, num_fk_columns, all_nullable, all_indexed):
        """
        Test that multiple FKs in the same entity all preserve their attributes.
        
        This verifies that attribute preservation is applied consistently across all FKs.
        """
        left_entity_name = 'Parent'
        right_entity_name = 'Child'
        left_table_name = 'parent'
        right_table_name = 'child'
        
        # Create left entity
        left_entity = Entity(
            name=left_entity_name,
            table_name=left_table_name,
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False)
            ]
        )
        
        # Create right entity with multiple FKs
        fk_columns = []
        relationships = []
        fk_names = []
        
        for i in range(num_fk_columns):
            fk_logical_name = f'fk_{i}'
            fk_db_column = f'fk_{i}_id'
            fk_names.append((fk_logical_name, fk_db_column))
            
            fk_columns.append(
                Column(
                    name=fk_logical_name,
                    type='bigint',
                    db_column=fk_db_column,
                    nullable=all_nullable,
                    indexed=all_indexed
                )
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
        
        # Property: All FK columns should preserve their attributes
        for fk_logical_name, fk_db_column in fk_names:
            # Find the FK column definition
            column_start = generated_code.find(f'{fk_db_column} = Column(')
            assert column_start != -1, f"Column definition for '{fk_db_column}' not found"
            
            # Extract column definition
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
            
            # Check attributes
            if all_nullable:
                assert 'nullable=True' in column_definition, (
                    f"FK column '{fk_db_column}' should preserve nullable=True"
                )
            else:
                assert 'nullable=False' in column_definition, (
                    f"FK column '{fk_db_column}' should preserve nullable=False"
                )
            
            if all_indexed:
                assert 'index=True' in column_definition, (
                    f"FK column '{fk_db_column}' should preserve index=True"
                )
            
            # Verify ForeignKey is present
            assert 'ForeignKey' in column_definition, (
                f"FK column '{fk_db_column}' should include ForeignKey constraint"
            )
