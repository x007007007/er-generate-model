"""
Property-based tests for Column db_column field.

These tests use hypothesis to verify universal properties across many generated inputs.
Each test runs a minimum of 100 iterations.
"""
import pytest
from hypothesis import given, settings, strategies as st
from x007007007.er.models import Column


# Strategy for generating valid field names
field_names = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(lambda s: len(s) < 50)

# Strategy for generating valid database column names
db_column_names = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(lambda s: len(s) < 50)

# Strategy for generating field types
field_types = st.sampled_from(['int', 'varchar', 'text', 'boolean', 'float', 'date', 'datetime'])


@st.composite
def random_column(draw):
    """Generate a random Column object with all fields."""
    name = draw(field_names)
    db_column = draw(db_column_names)
    field_type = draw(field_types)
    
    return Column(
        name=name,
        type=field_type,
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
        indexed=draw(st.booleans()),
    )


class TestProperty2FieldNameFallbackCorrectness:
    """
    Property 2: 字段名回退正确性
    
    **Validates: Requirements 1.2**
    
    对于任何Column对象，database_column_name属性应该等于db_column字段的值，
    且db_column必须是非空字符串。
    """
    
    @settings(max_examples=100)
    @given(random_column())
    def test_database_column_name_equals_db_column(self, column):
        """Test that database_column_name property always equals db_column field."""
        # Property: database_column_name should always equal db_column
        assert column.database_column_name == column.db_column, \
            f"database_column_name ({column.database_column_name}) != db_column ({column.db_column})"
    
    @settings(max_examples=100)
    @given(random_column())
    def test_db_column_is_non_empty_string(self, column):
        """Test that db_column is always a non-empty string."""
        # Property: db_column must be a non-empty string
        assert isinstance(column.db_column, str), \
            f"db_column is not a string: {type(column.db_column)}"
        assert len(column.db_column) > 0, \
            "db_column is an empty string"
    
    @settings(max_examples=100)
    @given(random_column())
    def test_database_column_name_is_non_empty_string(self, column):
        """Test that database_column_name is always a non-empty string."""
        # Property: database_column_name must be a non-empty string
        assert isinstance(column.database_column_name, str), \
            f"database_column_name is not a string: {type(column.database_column_name)}"
        assert len(column.database_column_name) > 0, \
            "database_column_name is an empty string"
