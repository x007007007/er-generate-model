"""
Property-based tests for SQLAlchemy renderer.

These tests use hypothesis to verify universal properties across many generated inputs.
Each test runs a minimum of 100 iterations.
"""
import ast
import pytest
from hypothesis import given, settings, strategies as st, HealthCheck
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer
from x007007007.er.models import ERModel, Entity, Column


# Custom strategies for generating ER models
safe_text = st.text().filter(lambda s: '\x00' not in s and len(s) < 200 and '\r' not in s and '\n' not in s)
safe_identifier = st.from_regex(r'[A-Z][a-zA-Z0-9]*', fullmatch=True).filter(lambda s: len(s) < 50)
safe_comment = st.text().filter(lambda s: '\x00' not in s and '"""' not in s and len(s) < 200 and '\r' not in s and '\n' not in s)


@st.composite
def column_with_values(draw):
    """Generate a column with default values and comments."""
    name = draw(st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(lambda s: len(s) < 30))
    col_type = draw(st.sampled_from(['int', 'varchar', 'text', 'boolean', 'float']))
    
    # Generate default value based on type
    if col_type == 'int':
        default = draw(st.one_of(st.none(), st.integers()))
    elif col_type == 'boolean':
        default = draw(st.one_of(st.none(), st.booleans()))
    elif col_type == 'float':
        default = draw(st.one_of(st.none(), st.floats(allow_nan=False, allow_infinity=False)))
    else:
        default = draw(st.one_of(st.none(), safe_text))
    
    comment = draw(st.one_of(st.none(), safe_text))
    
    return Column(
        name=name,
        type=col_type,
        max_length=100 if col_type == 'varchar' else None,
        is_pk=(name == 'id'),
        nullable=True,
        default=default,
        comment=comment
    )


@st.composite
def simple_entity(draw):
    """Generate a simple entity with columns."""
    name = draw(safe_identifier)
    num_columns = draw(st.integers(min_value=1, max_value=5))
    
    # Always include an id column
    columns = [Column(name='id', type='int', is_pk=True, nullable=False)]
    
    # Add additional columns
    for _ in range(num_columns - 1):
        columns.append(draw(column_with_values()))
    
    return Entity(
        name=name,
        columns=columns,
        comment=draw(st.one_of(st.none(), safe_comment))
    )


@st.composite
def er_model_with_values(draw):
    """Generate an ERModel with entities containing default values and comments."""
    num_entities = draw(st.integers(min_value=1, max_value=3))
    entities = {}
    
    for _ in range(num_entities):
        entity = draw(simple_entity())
        entities[entity.name] = entity
    
    return ERModel(entities=entities, relationships=[], templates={})


class TestProperty6SQLAlchemyTemplateIntegration:
    """
    Property 6: SQLAlchemy Template Integration
    
    **Validates: Requirements 8.1, 8.2**
    
    For any ERModel with entities containing columns with default values or comments,
    rendering the model with SQLAlchemy renderer should produce code where all default
    values and comments are properly serialized using the code_value filter.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(er_model_with_values())
    def test_sqlalchemy_renderer_serializes_default_values(self, model):
        """Test that SQLAlchemy renderer properly serializes default values."""
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Check that columns with non-None default values have them serialized
        has_default = any(
            col.default is not None 
            for entity in model.entities.values() 
            for col in entity.columns
        )
        
        if has_default:
            # The default should appear in the output
            assert 'default=' in result
        
        # The generated code should be valid Python
        try:
            ast.parse(result)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{result}")
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(er_model_with_values())
    def test_sqlalchemy_renderer_serializes_comments(self, model):
        """Test that SQLAlchemy renderer properly serializes comments."""
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Check that all columns with comments have them serialized
        for entity in model.entities.values():
            for col in entity.columns:
                if col.comment is not None and col.comment != '':
                    # The comment should appear in the output
                    assert 'comment=' in result
                    # The generated code should be valid Python
                    try:
                        ast.parse(result)
                    except SyntaxError as e:
                        pytest.fail(f"Generated code has syntax error: {e}\nColumn: {col.name}, Comment: {col.comment}")
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(er_model_with_values())
    def test_sqlalchemy_renderer_handles_quotes_in_values(self, model):
        """Test that SQLAlchemy renderer handles quotes in default values and comments."""
        renderer = SQLAlchemyRenderer()
        
        # Add some columns with quotes in values
        for entity in model.entities.values():
            if len(entity.columns) > 1:
                # Add a column with quotes in default
                entity.columns.append(Column(
                    name='quoted_field',
                    type='varchar',
                    max_length=100,
                    nullable=True,
                    default='say "hello"',
                    comment='Field with "quotes"'
                ))
        
        result = renderer.render(model)
        
        # The generated code should be valid Python despite quotes
        try:
            ast.parse(result)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error with quotes: {e}\n{result}")


class TestProperty7GeneratedCodeValiditySQLAlchemy:
    """
    Property 7: Generated Code Validity (SQLAlchemy)
    
    **Validates: Requirements 8.3**
    
    For any ERModel rendered to SQLAlchemy code, the generated code should be
    syntactically valid Python that can be parsed without errors.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(er_model_with_values())
    def test_sqlalchemy_generated_code_is_valid_python(self, model):
        """Test that all SQLAlchemy generated code is syntactically valid."""
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Should be able to parse without syntax errors
        try:
            ast.parse(result)
        except SyntaxError as e:
            pytest.fail(f"Generated SQLAlchemy code has syntax error: {e}\n{result}")
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(er_model_with_values())
    def test_sqlalchemy_generated_code_has_no_unescaped_quotes(self, model):
        """Test that generated code doesn't have unescaped quotes causing errors."""
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Parse to ensure no syntax errors from unescaped quotes
        try:
            ast.parse(result)
        except SyntaxError as e:
            # Check if error is related to quotes
            if 'unterminated string' in str(e).lower() or 'invalid syntax' in str(e).lower():
                pytest.fail(f"Generated code has quote escaping issue: {e}\n{result}")
            raise
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(er_model_with_values())
    def test_sqlalchemy_handles_falsy_default_values(self, model):
        """Test that SQLAlchemy renderer handles falsy default values (0, False, '')."""
        renderer = SQLAlchemyRenderer()
        
        # Add columns with falsy default values
        for entity in model.entities.values():
            entity.columns.extend([
                Column(name='zero_field', type='int', nullable=True, default=0),
                Column(name='false_field', type='boolean', nullable=True, default=False),
                Column(name='empty_field', type='varchar', max_length=100, nullable=True, default='')
            ])
        
        result = renderer.render(model)
        
        # Should include all falsy defaults
        assert 'default=0' in result
        assert 'default=False' in result
        assert 'default=""' in result
        
        # Should be valid Python
        try:
            ast.parse(result)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error with falsy defaults: {e}\n{result}")
