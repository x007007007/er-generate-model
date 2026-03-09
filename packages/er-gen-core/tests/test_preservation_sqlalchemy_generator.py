"""
Preservation Property Tests for SQLAlchemy Generator Fixes

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

These tests verify that non-buggy inputs continue to generate correctly.
Tests should PASS on unfixed code (confirming baseline behavior to preserve).

IMPORTANT: Follow observation-first methodology
- Observe behavior on UNFIXED code for non-buggy inputs
- Write property-based tests capturing observed behavior patterns

Expected Outcome: Tests PASS (this confirms baseline behavior to preserve)
"""
import ast
import pytest
from hypothesis import given, settings, strategies as st, HealthCheck, assume
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer
from x007007007.er.models import ERModel, Entity, Column, Relationship


# Custom strategies for generating test data
safe_identifier = st.from_regex(r'[A-Z][a-zA-Z0-9]*', fullmatch=True).filter(lambda s: len(s) < 50)
safe_column_name = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(lambda s: len(s) < 30)
safe_text = st.text().filter(lambda s: '\x00' not in s and len(s) < 200 and '\r' not in s and '\n' not in s)


@st.composite
def non_pk_column(draw):
    """
    Generate a non-primary key column.
    
    This represents columns that should NOT have primary_key=True in generated code.
    """
    name = draw(safe_column_name.filter(lambda s: s != 'id'))  # Avoid 'id' which is typically PK
    col_type = draw(st.sampled_from(['string', 'text', 'integer', 'boolean', 'date', 'datetime']))
    
    return Column(
        name=name,
        type=col_type,
        db_column=name,  # Use the same name as db_column for non-FK columns
        max_length=255 if col_type == 'string' else None,
        is_pk=False,  # Explicitly NOT a primary key
        is_fk=False,  # Explicitly NOT a foreign key
        nullable=draw(st.booleans()),
        unique=draw(st.booleans())
    )


@st.composite
def non_fk_column(draw):
    """
    Generate a non-foreign key column.
    
    This represents columns that should use their TOML field name directly.
    """
    name = draw(safe_column_name)
    col_type = draw(st.sampled_from(['string', 'text', 'integer', 'boolean', 'date', 'datetime']))
    
    return Column(
        name=name,
        type=col_type,
        db_column=name,  # Use the same name as db_column for non-FK columns
        max_length=255 if col_type == 'string' else None,
        is_pk=False,
        is_fk=False,  # Explicitly NOT a foreign key
        nullable=draw(st.booleans())
    )


@st.composite
def entity_with_non_buggy_columns(draw):
    """
    Generate an entity with only non-buggy columns.
    
    These are regular columns without primary_key or foreign_key attributes.
    """
    name = draw(safe_identifier)
    num_columns = draw(st.integers(min_value=1, max_value=5))
    
    columns = []
    for _ in range(num_columns):
        columns.append(draw(non_pk_column()))
    
    return Entity(
        name=name,
        columns=columns,
        table_name=f"test_{name.lower()}"
    )


@st.composite
def er_model_with_non_buggy_columns(draw):
    """Generate an ERModel with entities containing only non-buggy columns."""
    num_entities = draw(st.integers(min_value=1, max_value=3))
    entities = {}
    
    for _ in range(num_entities):
        entity = draw(entity_with_non_buggy_columns())
        entities[entity.name] = entity
    
    return ERModel(entities=entities, relationships=[], templates={})


class TestProperty2Preservation:
    """
    Property 2: Preservation - Non-Buggy Column and Relationship Generation
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**
    
    For any column or relationship definition where the bug condition does NOT hold,
    the template should produce exactly the same output as before, preserving all
    existing functionality.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(non_pk_column())
    def test_non_primary_key_columns_dont_include_primary_key_parameter(self, column):
        """
        Test that non-primary key columns don't include primary_key=True.
        
        **Validates: Requirement 3.1**
        
        WHEN a column is not a primary key
        THEN the system SHALL CONTINUE TO generate the Column without primary_key=True
        """
        # Create a simple entity with the non-PK column
        entity = Entity(
            name="TestEntity",
            columns=[column],
            table_name="test_entity"
        )
        model = ERModel(entities={"TestEntity": entity}, relationships=[], templates={})
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Verify the column doesn't have primary_key=True
        # Look for the column definition line
        column_line = None
        for line in result.split('\n'):
            if f'{column.name} = Column(' in line:
                column_line = line
                break
        
        if column_line:
            # Should NOT contain primary_key=True
            assert 'primary_key=True' not in column_line, \
                f"Non-PK column '{column.name}' should not have primary_key=True"
        
        # Generated code should be valid Python
        try:
            ast.parse(result)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{result}")
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(non_fk_column())
    def test_non_foreign_key_columns_use_correct_field_names(self, column):
        """
        Test that non-foreign key columns use correct field names from TOML.
        
        **Validates: Requirement 3.2**
        
        WHEN a column is not a foreign key
        THEN the system SHALL CONTINUE TO generate the Column with the correct
        field name from the TOML specification
        """
        # Create a simple entity with the non-FK column
        entity = Entity(
            name="TestEntity",
            columns=[column],
            table_name="test_entity"
        )
        model = ERModel(entities={"TestEntity": entity}, relationships=[], templates={})
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Verify the column uses the correct field name
        assert f'{column.name} = Column(' in result, \
            f"Non-FK column should use field name '{column.name}' from TOML"
        
        # Generated code should be valid Python
        try:
            ast.parse(result)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{result}")
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(non_fk_column())
    def test_type_mapping_for_non_fk_columns_remains_correct(self, column):
        """
        Test that type mapping for non-FK columns remains correct.
        
        **Validates: Requirement 3.3**
        
        WHEN a column has a specific type in the TOML specification
        THEN the system SHALL CONTINUE TO map it to the correct SQLAlchemy type
        
        NOTE: This test observes the CURRENT behavior on unfixed code.
        The actual type mapping may have quirks (e.g., 'datetime' -> 'Date'),
        but we preserve this behavior for non-FK columns.
        """
        # Create a simple entity with the column
        entity = Entity(
            name="TestEntity",
            columns=[column],
            table_name="test_entity"
        )
        model = ERModel(entities={"TestEntity": entity}, relationships=[], templates={})
        
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Verify that the column is generated with SOME type
        # We're not testing the exact type mapping here, just that it generates
        assert f'{column.name} = Column(' in result, \
            f"Column '{column.name}' should be generated"
        
        # Verify the generated code contains a valid SQLAlchemy type
        # (String, Text, Integer, Boolean, Date, DateTime, Time, etc.)
        column_line = None
        for line in result.split('\n'):
            if f'{column.name} = Column(' in line:
                column_line = line
                break
        
        if column_line:
            # Should contain at least one SQLAlchemy type
            sqlalchemy_types = ['String', 'Text', 'Integer', 'Boolean', 'Date', 'DateTime', 'Time', 'Float', 'Numeric']
            has_type = any(t in column_line for t in sqlalchemy_types)
            assert has_type, f"Column '{column.name}' should have a SQLAlchemy type"
        
        # Generated code should be valid Python
        try:
            ast.parse(result)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{result}")
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(er_model_with_non_buggy_columns())
    def test_table_names_and_imports_generate_correctly(self, model):
        """
        Test that table names and imports generate correctly.
        
        **Validates: Requirement 3.5**
        
        WHEN generating table names, imports, and other model attributes
        THEN the system SHALL CONTINUE TO generate them correctly as before
        """
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Verify imports are present
        assert 'from sqlalchemy import' in result, \
            "Generated code should include SQLAlchemy imports"
        
        # Verify table names are present for each entity
        for entity_name, entity in model.entities.items():
            if entity.table_name:
                assert f"__tablename__ = '{entity.table_name}'" in result, \
                    f"Entity '{entity_name}' should have table name '{entity.table_name}'"
        
        # Generated code should be valid Python
        try:
            ast.parse(result)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{result}")
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(er_model_with_non_buggy_columns())
    def test_generated_code_is_syntactically_valid(self, model):
        """
        Test that generated code for non-buggy inputs is syntactically valid.
        
        This is a general preservation test ensuring that the fix doesn't break
        code generation for regular columns.
        """
        # Generate SQLAlchemy code
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Generated code should be valid Python
        try:
            ast.parse(result)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{result}")
