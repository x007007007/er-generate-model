"""
Property-based tests for Column model.

These tests use hypothesis to verify universal properties across many generated inputs.
Each test runs a minimum of 100 iterations.

Feature: field-db-column-and-path-separation
"""
import pytest
from hypothesis import given, settings, strategies as st
from x007007007.er.models import Column


# Custom strategies for generating Column objects
safe_identifier = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(lambda s: len(s) < 50)
column_types = st.sampled_from(['int', 'varchar', 'text', 'boolean', 'float', 'date', 'datetime'])


@st.composite
def random_column(draw):
    """Generate a random Column object with all required fields."""
    name = draw(safe_identifier)
    col_type = draw(column_types)
    db_column = draw(safe_identifier)
    
    return Column(
        name=name,
        type=col_type,
        db_column=db_column,
        is_pk=draw(st.booleans()),
        is_fk=draw(st.booleans()),
        nullable=draw(st.booleans()),
        comment=draw(st.one_of(st.none(), st.text(max_size=100))),
        default=draw(st.one_of(st.none(), st.text(max_size=50))),
        max_length=draw(st.one_of(st.none(), st.integers(min_value=1, max_value=1000))),
        precision=draw(st.one_of(st.none(), st.integers(min_value=1, max_value=65))),
        scale=draw(st.one_of(st.none(), st.integers(min_value=0, max_value=30))),
        unique=draw(st.booleans()),
        indexed=draw(st.booleans())
    )


class TestProperty2FieldNameFallbackCorrectness:
    """
    Property 2: 字段名回退正确性
    
    **Validates: Requirements 1.2**
    
    For any Column object, the database_column_name property should equal
    the db_column field value, and db_column must be a non-empty string.
    """
    
    @settings(max_examples=100)
    @given(random_column())
    def test_database_column_name_equals_db_column(self, column):
        """Test that database_column_name property returns db_column value."""
        # Property: database_column_name should always equal db_column
        assert column.database_column_name == column.db_column, \
            f"database_column_name ({column.database_column_name}) != db_column ({column.db_column})"
    
    @settings(max_examples=100)
    @given(random_column())
    def test_db_column_is_non_empty_string(self, column):
        """Test that db_column is always a non-empty string."""
        # Property: db_column must be a non-empty string
        assert isinstance(column.db_column, str), \
            f"db_column must be a string, got {type(column.db_column)}"
        assert len(column.db_column) > 0, \
            "db_column must be non-empty"
    
    @settings(max_examples=100)
    @given(random_column())
    def test_database_column_name_is_non_empty_string(self, column):
        """Test that database_column_name is always a non-empty string."""
        # Property: database_column_name must be a non-empty string
        assert isinstance(column.database_column_name, str), \
            f"database_column_name must be a string, got {type(column.database_column_name)}"
        assert len(column.database_column_name) > 0, \
            "database_column_name must be non-empty"
