"""
Property-based tests for PythonRenderer base class.

These tests use hypothesis to verify universal properties across many generated inputs.
Each test runs a minimum of 100 iterations.
"""
import ast
import pytest
from hypothesis import given, settings, strategies as st, HealthCheck
from x007007007.er.renderers.python.base import PythonRenderer
from x007007007.er.models import ERModel


class ConcretePythonRenderer(PythonRenderer):
    """Concrete implementation for testing."""
    def render(self, model: ERModel) -> str:
        return "rendered code"


# Custom strategies for generating Python values
# Filter out null bytes which cause syntax errors in eval()
safe_text = st.text().filter(lambda s: '\x00' not in s)

@st.composite
def python_values(draw):
    """Generate random Python values that can be serialized."""
    return draw(st.one_of(
        st.none(),
        st.booleans(),
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False),
        safe_text,
        st.lists(st.one_of(
            st.none(),
            st.booleans(),
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            safe_text
        ), max_size=10),
        st.dictionaries(
            safe_text.filter(lambda s: len(s) > 0),
            st.one_of(
                st.none(),
                st.booleans(),
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                safe_text
            ),
            max_size=10
        )
    ))


@st.composite
def nested_python_values(draw, max_depth=3):
    """Generate nested Python values (lists and dicts)."""
    if max_depth == 0:
        return draw(st.one_of(
            st.none(),
            st.booleans(),
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            safe_text
        ))
    
    return draw(st.one_of(
        st.none(),
        st.booleans(),
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False),
        safe_text,
        st.lists(nested_python_values(max_depth=max_depth-1), max_size=5),
        st.dictionaries(
            safe_text.filter(lambda s: len(s) > 0),
            nested_python_values(max_depth=max_depth-1),
            max_size=5
        )
    ))


class TestProperty1SerializationRoundTrip:
    """
    Property 1: Serialization Round Trip
    
    **Validates: Requirements 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**
    
    For any Python value that can be serialized (None, bool, int, float, str, list, dict),
    serializing the value and then evaluating the result should produce an equivalent value.
    """
    
    def setup_method(self):
        """Set up test fixtures."""
        self.renderer = ConcretePythonRenderer()
    
    @settings(max_examples=100)
    @given(python_values())
    def test_serialization_round_trip(self, value):
        """Test that serialization and evaluation produces equivalent value."""
        # Serialize the value
        serialized = self.renderer.serialize_value(value)
        
        # Evaluate the serialized string
        evaluated = eval(serialized)
        
        # Assert the evaluated value equals the original
        assert evaluated == value, f"Round trip failed for {value!r}: got {evaluated!r}"
    
    @settings(max_examples=100)
    @given(st.none())
    def test_none_round_trip(self, value):
        """Test None serialization round trip."""
        serialized = self.renderer.serialize_value(value)
        assert serialized == "None"
        assert eval(serialized) is None
    
    @settings(max_examples=100)
    @given(st.booleans())
    def test_bool_round_trip(self, value):
        """Test boolean serialization round trip."""
        serialized = self.renderer.serialize_value(value)
        assert serialized in ("True", "False")
        assert eval(serialized) == value
    
    @settings(max_examples=100)
    @given(st.integers())
    def test_int_round_trip(self, value):
        """Test integer serialization round trip."""
        serialized = self.renderer.serialize_value(value)
        assert eval(serialized) == value
    
    @settings(max_examples=100)
    @given(st.floats(allow_nan=False, allow_infinity=False))
    def test_float_round_trip(self, value):
        """Test float serialization round trip."""
        serialized = self.renderer.serialize_value(value)
        assert eval(serialized) == value
    
    @settings(max_examples=100)
    @given(safe_text)
    def test_string_round_trip(self, value):
        """Test string serialization round trip."""
        serialized = self.renderer.serialize_value(value)
        assert eval(serialized) == value
    
    @settings(max_examples=100)
    @given(st.lists(python_values(), max_size=10))
    def test_list_round_trip(self, value):
        """Test list serialization round trip."""
        serialized = self.renderer.serialize_value(value)
        assert eval(serialized) == value
    
    @settings(max_examples=100)
    @given(st.dictionaries(safe_text.filter(lambda s: len(s) > 0), python_values(), max_size=10))
    def test_dict_round_trip(self, value):
        """Test dict serialization round trip."""
        serialized = self.renderer.serialize_value(value)
        assert eval(serialized) == value


class TestProperty2SmartQuoteSelection:
    """
    Property 2: Smart Quote Selection
    
    **Validates: Requirements 4.1, 4.2, 4.3, 4.4**
    
    For any string value, the serializer should choose the quote style that minimizes escaping.
    """
    
    def setup_method(self):
        """Set up test fixtures."""
        self.renderer = ConcretePythonRenderer()
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.filter_too_much])
    @given(st.from_regex(r'[^\'\\]*"[^\'\\]*', fullmatch=True).filter(lambda s: '"' in s and "'" not in s and '\\' not in s))
    def test_only_double_quotes_uses_single_quotes(self, value):
        """Test that strings with only double quotes (no backslashes) use single quotes."""
        serialized = self.renderer.serialize_value(value)
        # Should start and end with single quotes
        assert serialized.startswith("'") and serialized.endswith("'")
        # Should not have escaped double quotes (since we're using single quotes)
        assert '\\"' not in serialized
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.filter_too_much])
    @given(st.from_regex(r'[^"\\]*\'[^"\\]*', fullmatch=True).filter(lambda s: "'" in s and '"' not in s and '\\' not in s))
    def test_only_single_quotes_uses_double_quotes(self, value):
        """Test that strings with only single quotes (no backslashes) use double quotes."""
        serialized = self.renderer.serialize_value(value)
        # Should start and end with double quotes
        assert serialized.startswith('"') and serialized.endswith('"')
        # Should not have escaped single quotes (since we're using double quotes)
        assert "\\'" not in serialized
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.filter_too_much])
    @given(st.from_regex(r'.*".*\'.*', fullmatch=True).filter(lambda s: '"' in s and "'" in s))
    def test_both_quotes_uses_double_quotes_with_escaping(self, value):
        """Test that strings with both quotes use double quotes and escape."""
        serialized = self.renderer.serialize_value(value)
        # Should start and end with double quotes
        assert serialized.startswith('"') and serialized.endswith('"')
        # Should have escaped double quotes
        assert '\\"' in serialized
    
    @settings(max_examples=100)
    @given(safe_text.filter(lambda s: '"' not in s and "'" not in s))
    def test_no_quotes_uses_double_quotes(self, value):
        """Test that strings with no quotes use double quotes."""
        serialized = self.renderer.serialize_value(value)
        # Should start and end with double quotes
        assert serialized.startswith('"') and serialized.endswith('"')
    
    @settings(max_examples=100)
    @given(safe_text)
    def test_minimal_escaping(self, value):
        """Test that serialization uses minimal escaping."""
        serialized = self.renderer.serialize_value(value)
        # Verify the serialized string can be evaluated
        evaluated = eval(serialized)
        assert evaluated == value
        
        # Count escapes in serialized string
        has_single = "'" in value
        has_double = '"' in value
        
        if has_double and not has_single:
            # Should use single quotes, no escaped double quotes
            assert '\\"' not in serialized
        elif has_single and not has_double:
            # Should use double quotes, no escaped single quotes
            assert "\\'" not in serialized


class TestProperty3EscapeSequencePreservation:
    """
    Property 3: Escape Sequence Preservation
    
    **Validates: Requirements 4.5, 9.2, 9.3, 9.4**
    
    For any string containing special characters (newlines, tabs, backslashes),
    the serialized output should preserve these characters correctly.
    """
    
    def setup_method(self):
        """Set up test fixtures."""
        self.renderer = ConcretePythonRenderer()
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.filter_too_much])
    @given(st.from_regex(r'.*[\n\t\r\\].*', fullmatch=True).filter(lambda s: '\x00' not in s))
    def test_special_characters_preserved(self, value):
        """Test that special characters are preserved in round trip."""
        serialized = self.renderer.serialize_value(value)
        evaluated = eval(serialized)
        assert evaluated == value
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.filter_too_much])
    @given(st.from_regex(r'.*\n.*', fullmatch=True).filter(lambda s: '\x00' not in s))
    def test_newline_preserved(self, value):
        """Test that newlines are preserved."""
        serialized = self.renderer.serialize_value(value)
        # Should contain escaped newline
        assert '\\n' in serialized
        # Round trip should work
        assert eval(serialized) == value
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.filter_too_much])
    @given(st.from_regex(r'.*\t.*', fullmatch=True).filter(lambda s: '\x00' not in s))
    def test_tab_preserved(self, value):
        """Test that tabs are preserved."""
        serialized = self.renderer.serialize_value(value)
        # Should contain escaped tab
        assert '\\t' in serialized
        # Round trip should work
        assert eval(serialized) == value
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.filter_too_much])
    @given(st.from_regex(r'.*\\.*', fullmatch=True).filter(lambda s: '\x00' not in s))
    def test_backslash_preserved(self, value):
        """Test that backslashes are preserved."""
        serialized = self.renderer.serialize_value(value)
        # Should contain escaped backslash
        assert '\\\\' in serialized
        # Round trip should work
        assert eval(serialized) == value
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.filter_too_much])
    @given(st.from_regex(r'.*\r.*', fullmatch=True).filter(lambda s: '\x00' not in s))
    def test_carriage_return_preserved(self, value):
        """Test that carriage returns are preserved."""
        serialized = self.renderer.serialize_value(value)
        # Should contain escaped carriage return
        assert '\\r' in serialized
        # Round trip should work
        assert eval(serialized) == value


class TestProperty4NestedStructureSerialization:
    """
    Property 4: Nested Structure Serialization
    
    **Validates: Requirements 9.5**
    
    For any nested data structure (lists containing dicts, dicts containing lists, etc.),
    the serializer should recursively serialize all elements correctly.
    """
    
    def setup_method(self):
        """Set up test fixtures."""
        self.renderer = ConcretePythonRenderer()
    
    @settings(max_examples=100)
    @given(nested_python_values(max_depth=3))
    def test_nested_structure_round_trip(self, value):
        """Test that nested structures serialize and evaluate correctly."""
        serialized = self.renderer.serialize_value(value)
        evaluated = eval(serialized)
        assert evaluated == value
    
    @settings(max_examples=100)
    @given(st.lists(st.lists(st.integers(), max_size=5), max_size=5))
    def test_nested_lists(self, value):
        """Test nested lists serialization."""
        serialized = self.renderer.serialize_value(value)
        evaluated = eval(serialized)
        assert evaluated == value
    
    @settings(max_examples=100)
    @given(st.dictionaries(
        safe_text.filter(lambda s: len(s) > 0),
        st.dictionaries(safe_text.filter(lambda s: len(s) > 0), st.integers(), max_size=5),
        max_size=5
    ))
    def test_nested_dicts(self, value):
        """Test nested dicts serialization."""
        serialized = self.renderer.serialize_value(value)
        evaluated = eval(serialized)
        assert evaluated == value
    
    @settings(max_examples=100)
    @given(st.lists(st.dictionaries(safe_text.filter(lambda s: len(s) > 0), st.integers(), max_size=5), max_size=5))
    def test_list_of_dicts(self, value):
        """Test list of dicts serialization."""
        serialized = self.renderer.serialize_value(value)
        evaluated = eval(serialized)
        assert evaluated == value
    
    @settings(max_examples=100)
    @given(st.dictionaries(safe_text.filter(lambda s: len(s) > 0), st.lists(st.integers(), max_size=5), max_size=5))
    def test_dict_of_lists(self, value):
        """Test dict of lists serialization."""
        serialized = self.renderer.serialize_value(value)
        evaluated = eval(serialized)
        assert evaluated == value
    
    @settings(max_examples=100)
    @given(st.lists(st.one_of(
        st.integers(),
        safe_text,
        st.lists(st.integers(), max_size=3),
        st.dictionaries(safe_text.filter(lambda s: len(s) > 0), st.integers(), max_size=3)
    ), max_size=5))
    def test_mixed_nested_structures(self, value):
        """Test mixed nested structures serialization."""
        serialized = self.renderer.serialize_value(value)
        evaluated = eval(serialized)
        assert evaluated == value


class TestProperty15NoExtraBlankLines:
    """
    Property 15: No Extra Blank Lines in Generated Code
    
    **Validates: Requirements 14.4, 14.5**
    
    For any ERModel rendered to code, the generated code should not contain
    consecutive blank lines caused by Jinja2 directive lines.
    """
    
    def setup_method(self):
        """Set up test fixtures."""
        self.renderer = ConcretePythonRenderer()
    
    @settings(max_examples=100)
    @given(st.booleans(), st.text())
    def test_no_consecutive_blank_lines_in_template_output(self, has_comment, comment):
        """Test that template output doesn't have consecutive blank lines."""
        from jinja2 import DictLoader
        
        # Template with conditional that could create blank lines
        template_str = """class MyClass:
{% if has_comment %}
    \"\"\"{{ comment }}\"\"\"
{% endif %}
    def method(self):
        pass"""
        
        loader = DictLoader({"test.j2": template_str})
        env = self.renderer._setup_jinja_env(loader)
        template = env.get_template("test.j2")
        
        result = template.render(has_comment=has_comment, comment=comment)
        
        # Check for consecutive blank lines (more than one \n in a row)
        assert '\n\n\n' not in result, "Found triple newline (consecutive blank lines)"
    
    def test_whitespace_control_settings_prevent_blank_lines(self):
        """Test that whitespace control settings are properly configured."""
        from jinja2 import PackageLoader
        
        loader = PackageLoader("x007007007.er", "templates")
        env = self.renderer._setup_jinja_env(loader)
        
        # Verify settings that prevent blank lines
        assert env.trim_blocks is True
        assert env.lstrip_blocks is True


class TestProperty16CorrectPythonIndentation:
    """
    Property 16: Correct Python Indentation
    
    **Validates: Requirements 14.6**
    
    For any generated Python code, all lines should have correct indentation
    according to Python syntax rules, regardless of how the template is formatted.
    """
    
    def setup_method(self):
        """Set up test fixtures."""
        self.renderer = ConcretePythonRenderer()
    
    @settings(max_examples=100)
    @given(st.from_regex(r'[A-Z][a-zA-Z0-9]*', fullmatch=True), st.booleans())
    def test_generated_code_has_valid_indentation(self, class_name, has_method):
        """Test that generated code has valid Python indentation."""
        from jinja2 import DictLoader
        import keyword
        
        # Template with indentation
        template_str = """class {{ class_name }}:
    pass
{% if has_method %}
    def method(self):
        return True
{% endif %}"""
        
        loader = DictLoader({"test.j2": template_str})
        env = self.renderer._setup_jinja_env(loader)
        template = env.get_template("test.j2")
        
        # Skip Python keywords
        if keyword.iskeyword(class_name):
            class_name = "Test" + class_name
        
        result = template.render(class_name=class_name, has_method=has_method)
        
        # Try to parse the generated code - will raise SyntaxError if indentation is wrong
        try:
            ast.parse(result)
        except SyntaxError as e:
            pytest.fail(f"Generated code has invalid indentation: {e}\n{result}")
    
    def test_template_indentation_preserved(self):
        """Test that template indentation is preserved in output."""
        from jinja2 import DictLoader
        
        template_str = """class MyClass:
    def __init__(self):
        self.value = 42
    
    def method(self):
        return self.value"""
        
        loader = DictLoader({"test.j2": template_str})
        env = self.renderer._setup_jinja_env(loader)
        template = env.get_template("test.j2")
        
        result = template.render()
        
        # Should be valid Python
        ast.parse(result)
        
        # Check specific indentation
        lines = result.split('\n')
        assert lines[0] == "class MyClass:"
        assert lines[1].startswith("    def __init__")
        assert lines[2].startswith("        self.value")



class TestProperty8FilterRegistration:
    """
    Property 8: Filter Registration
    
    **Validates: Requirements 6.1, 6.2, 6.3**
    
    For any renderer instance (Django or SQLAlchemy), the Jinja2 environment
    should have the 'code_value' filter registered and callable.
    """
    
    @settings(max_examples=100)
    @given(st.sampled_from(['django', 'sqlalchemy']))
    def test_code_value_filter_is_registered(self, renderer_type):
        """Test that code_value filter is registered in all renderers."""
        if renderer_type == 'django':
            from x007007007.er.renderers.python.django import DjangoRenderer
            renderer = DjangoRenderer()
        else:
            from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer
            renderer = SQLAlchemyRenderer()
        
        # Filter should be registered
        assert 'code_value' in renderer.env.filters, \
            f"{renderer_type} renderer doesn't have code_value filter"
    
    @settings(max_examples=100)
    @given(st.sampled_from(['django', 'sqlalchemy']))
    def test_code_value_filter_is_callable(self, renderer_type):
        """Test that code_value filter is callable."""
        if renderer_type == 'django':
            from x007007007.er.renderers.python.django import DjangoRenderer
            renderer = DjangoRenderer()
        else:
            from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer
            renderer = SQLAlchemyRenderer()
        
        # Filter should be callable
        code_value_filter = renderer.env.filters['code_value']
        assert callable(code_value_filter), \
            f"{renderer_type} renderer's code_value filter is not callable"
    
    @settings(max_examples=100)
    @given(
        st.sampled_from(['django', 'sqlalchemy']),
        python_values()
    )
    def test_code_value_filter_works_correctly(self, renderer_type, value):
        """Test that code_value filter produces correct output."""
        if renderer_type == 'django':
            from x007007007.er.renderers.python.django import DjangoRenderer
            renderer = DjangoRenderer()
        else:
            from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer
            renderer = SQLAlchemyRenderer()
        
        # Filter should work correctly
        code_value_filter = renderer.env.filters['code_value']
        serialized = code_value_filter(value)
        
        # Should be a string
        assert isinstance(serialized, str), \
            f"code_value filter returned {type(serialized)} instead of str"
        
        # Should be valid Python that evaluates to the original value
        evaluated = eval(serialized)
        assert evaluated == value, \
            f"code_value filter round trip failed: {value} -> {serialized} -> {evaluated}"
    
    @settings(max_examples=100)
    @given(st.sampled_from(['django', 'sqlalchemy']))
    def test_django_package_renderer_has_filter(self, _):
        """Test that DjangoPackageRenderer also has code_value filter."""
        from x007007007.er.renderers.python.django import DjangoPackageRenderer
        renderer = DjangoPackageRenderer()
        
        # Filter should be registered
        assert 'code_value' in renderer.env.filters
        assert callable(renderer.env.filters['code_value'])
