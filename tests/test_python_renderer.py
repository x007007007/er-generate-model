"""
Unit tests for PythonRenderer base class.
"""
import pytest
from jinja2 import Environment
from x007007007.er.renderers.python.base import PythonRenderer
from x007007007.er.models import ERModel


class ConcretePythonRenderer(PythonRenderer):
    """Concrete implementation for testing."""
    def render(self, model: ERModel) -> str:
        return "rendered code"


class TestSerializeValue:
    """Tests for serialize_value method covering all data types."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.renderer = ConcretePythonRenderer()
    
    def test_serialize_none(self):
        """Test serialization of None."""
        result = self.renderer.serialize_value(None)
        assert result == "None"
    
    def test_serialize_bool_true(self):
        """Test serialization of True."""
        result = self.renderer.serialize_value(True)
        assert result == "True"
    
    def test_serialize_bool_false(self):
        """Test serialization of False."""
        result = self.renderer.serialize_value(False)
        assert result == "False"
    
    def test_serialize_int_positive(self):
        """Test serialization of positive integer."""
        result = self.renderer.serialize_value(42)
        assert result == "42"
    
    def test_serialize_int_negative(self):
        """Test serialization of negative integer."""
        result = self.renderer.serialize_value(-42)
        assert result == "-42"
    
    def test_serialize_int_zero(self):
        """Test serialization of zero."""
        result = self.renderer.serialize_value(0)
        assert result == "0"
    
    def test_serialize_float_positive(self):
        """Test serialization of positive float."""
        result = self.renderer.serialize_value(3.14)
        assert result == "3.14"
    
    def test_serialize_float_negative(self):
        """Test serialization of negative float."""
        result = self.renderer.serialize_value(-3.14)
        assert result == "-3.14"
    
    def test_serialize_float_zero(self):
        """Test serialization of 0.0."""
        result = self.renderer.serialize_value(0.0)
        assert result == "0.0"
    
    def test_serialize_string_simple(self):
        """Test serialization of simple string."""
        result = self.renderer.serialize_value("hello")
        assert result == '"hello"'
    
    def test_serialize_string_empty(self):
        """Test serialization of empty string."""
        result = self.renderer.serialize_value("")
        assert result == '""'
    
    def test_serialize_list_empty(self):
        """Test serialization of empty list."""
        result = self.renderer.serialize_value([])
        assert result == "[]"
    
    def test_serialize_list_simple(self):
        """Test serialization of simple list."""
        result = self.renderer.serialize_value([1, 2, 3])
        assert result == "[1, 2, 3]"
    
    def test_serialize_list_mixed_types(self):
        """Test serialization of list with mixed types."""
        result = self.renderer.serialize_value([1, "hello", True, None])
        assert result == '[1, "hello", True, None]'
    
    def test_serialize_dict_empty(self):
        """Test serialization of empty dict."""
        result = self.renderer.serialize_value({})
        assert result == "{}"
    
    def test_serialize_dict_simple(self):
        """Test serialization of simple dict."""
        result = self.renderer.serialize_value({"key": "value"})
        assert result == '{"key": "value"}'
    
    def test_serialize_dict_multiple_items(self):
        """Test serialization of dict with multiple items."""
        result = self.renderer.serialize_value({"a": 1, "b": 2})
        # Dict order is preserved in Python 3.7+
        assert result == '{"a": 1, "b": 2}'
    
    def test_serialize_dict_mixed_types(self):
        """Test serialization of dict with mixed value types."""
        result = self.renderer.serialize_value({"int": 42, "str": "hello", "bool": True, "none": None})
        assert '"int": 42' in result
        assert '"str": "hello"' in result
        assert '"bool": True' in result
        assert '"none": None' in result
    
    def test_serialize_nested_list(self):
        """Test serialization of nested list."""
        result = self.renderer.serialize_value([[1, 2], [3, 4]])
        assert result == "[[1, 2], [3, 4]]"
    
    def test_serialize_nested_dict(self):
        """Test serialization of nested dict."""
        result = self.renderer.serialize_value({"outer": {"inner": "value"}})
        assert result == '{"outer": {"inner": "value"}}'
    
    def test_serialize_list_with_dict(self):
        """Test serialization of list containing dict."""
        result = self.renderer.serialize_value([{"key": "value"}])
        assert result == '[{"key": "value"}]'
    
    def test_serialize_dict_with_list(self):
        """Test serialization of dict containing list."""
        result = self.renderer.serialize_value({"key": [1, 2, 3]})
        assert result == '{"key": [1, 2, 3]}'
    
    def test_serialize_unsupported_type_raises_error(self):
        """Test that unsupported types raise ValueError."""
        class CustomClass:
            pass
        
        with pytest.raises(ValueError, match="Unsupported type for serialization"):
            self.renderer.serialize_value(CustomClass())
    
    def test_serialize_function_raises_error(self):
        """Test that functions raise ValueError."""
        def test_func():
            pass
        
        with pytest.raises(ValueError, match="Unsupported type for serialization"):
            self.renderer.serialize_value(test_func)
    
    def test_serialize_with_context_parameter(self):
        """Test that context parameter is accepted."""
        # Context parameter should be accepted but doesn't affect basic types
        result = self.renderer.serialize_value(42, context='comment')
        assert result == "42"


class TestSerializeString:
    """Tests for _serialize_string method covering all quote scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.renderer = ConcretePythonRenderer()
    
    def test_string_no_quotes(self):
        """Test string with no quotes uses double quotes."""
        result = self.renderer._serialize_string("hello world")
        assert result == '"hello world"'
    
    def test_string_only_double_quotes(self):
        """Test string with only double quotes uses single quotes."""
        result = self.renderer._serialize_string('say "hi"')
        assert result == '\'say "hi"\''
    
    def test_string_only_single_quotes(self):
        """Test string with only single quotes uses double quotes."""
        result = self.renderer._serialize_string("it's nice")
        assert result == '"it\'s nice"'
    
    def test_string_both_quotes(self):
        """Test string with both quotes uses double quotes and escapes."""
        result = self.renderer._serialize_string('say "it\'s nice"')
        assert result == '"say \\"it\'s nice\\""'
    
    def test_string_with_newline(self):
        """Test string with newline is escaped."""
        result = self.renderer._serialize_string("line1\nline2")
        assert result == '"line1\\nline2"'
    
    def test_string_with_tab(self):
        """Test string with tab is escaped."""
        result = self.renderer._serialize_string("col1\tcol2")
        assert result == '"col1\\tcol2"'
    
    def test_string_with_carriage_return(self):
        """Test string with carriage return is escaped."""
        result = self.renderer._serialize_string("line1\rline2")
        assert result == '"line1\\rline2"'
    
    def test_string_with_backslash(self):
        """Test string with backslash is escaped."""
        result = self.renderer._serialize_string("path\\to\\file")
        assert result == '"path\\\\to\\\\file"'
    
    def test_string_with_backslash_and_newline(self):
        """Test string with backslash and newline."""
        result = self.renderer._serialize_string("line1\\\nline2")
        assert result == '"line1\\\\\\nline2"'
    
    def test_string_with_all_special_chars(self):
        """Test string with multiple special characters."""
        result = self.renderer._serialize_string("test\n\t\r\\")
        assert result == '"test\\n\\t\\r\\\\"'
    
    def test_empty_string(self):
        """Test empty string."""
        result = self.renderer._serialize_string("")
        assert result == '""'
    
    def test_string_with_unicode(self):
        """Test string with unicode characters."""
        result = self.renderer._serialize_string("你好世界")
        assert result == '"你好世界"'
    
    def test_string_with_emoji(self):
        """Test string with emoji."""
        result = self.renderer._serialize_string("Hello 👋")
        assert result == '"Hello 👋"'


class TestSetupJinjaEnv:
    """Tests for _setup_jinja_env method verifying whitespace settings."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.renderer = ConcretePythonRenderer()
    
    def test_setup_jinja_env_returns_environment(self):
        """Test that _setup_jinja_env returns a Jinja2 Environment."""
        from jinja2 import PackageLoader
        loader = PackageLoader("x007007007.er", "templates")
        env = self.renderer._setup_jinja_env(loader)
        assert isinstance(env, Environment)
    
    def test_jinja_env_has_trim_blocks(self):
        """Test that Jinja2 environment has trim_blocks=True."""
        from jinja2 import PackageLoader
        loader = PackageLoader("x007007007.er", "templates")
        env = self.renderer._setup_jinja_env(loader)
        assert env.trim_blocks is True
    
    def test_jinja_env_has_lstrip_blocks(self):
        """Test that Jinja2 environment has lstrip_blocks=True."""
        from jinja2 import PackageLoader
        loader = PackageLoader("x007007007.er", "templates")
        env = self.renderer._setup_jinja_env(loader)
        assert env.lstrip_blocks is True
    
    def test_jinja_env_has_keep_trailing_newline(self):
        """Test that Jinja2 environment has keep_trailing_newline=True."""
        from jinja2 import PackageLoader
        loader = PackageLoader("x007007007.er", "templates")
        env = self.renderer._setup_jinja_env(loader)
        assert env.keep_trailing_newline is True
    
    def test_jinja_env_has_autoescape(self):
        """Test that Jinja2 environment has autoescape configured."""
        from jinja2 import PackageLoader
        loader = PackageLoader("x007007007.er", "templates")
        env = self.renderer._setup_jinja_env(loader)
        # Autoescape should be configured (not None)
        assert env.autoescape is not None
    
    def test_jinja_env_whitespace_control_prevents_blank_lines(self):
        """Test that whitespace control prevents extra blank lines."""
        from jinja2 import DictLoader
        
        # Template with conditional that would create blank line without whitespace control
        template_str = """class MyClass:
{% if has_comment %}
    \"\"\"{{ comment }}\"\"\"
{% endif %}
    def method(self):
        pass"""
        
        loader = DictLoader({"test.j2": template_str})
        env = self.renderer._setup_jinja_env(loader)
        template = env.get_template("test.j2")
        
        # Render with comment
        result_with = template.render(has_comment=True, comment="My comment")
        # Should not have extra blank line between class and docstring
        assert 'class MyClass:\n    """My comment"""' in result_with
        
        # Render without comment
        result_without = template.render(has_comment=False)
        # Should not have extra blank line between class and method
        assert 'class MyClass:\n    def method(self):' in result_without


class TestPythonRendererInheritance:
    """Tests for PythonRenderer inheritance and abstract methods."""
    
    def test_python_renderer_inherits_from_renderer(self):
        """Test that PythonRenderer inherits from Renderer."""
        from x007007007.er.renderers.base import Renderer
        assert issubclass(PythonRenderer, Renderer)
    
    def test_python_renderer_is_abstract(self):
        """Test that PythonRenderer cannot be instantiated directly."""
        with pytest.raises(TypeError):
            PythonRenderer()
    
    def test_concrete_implementation_can_be_instantiated(self):
        """Test that concrete implementations can be instantiated."""
        renderer = ConcretePythonRenderer()
        assert isinstance(renderer, PythonRenderer)
    
    def test_python_renderer_has_serialize_value(self):
        """Test that PythonRenderer has serialize_value method."""
        assert hasattr(PythonRenderer, 'serialize_value')
        assert callable(getattr(PythonRenderer, 'serialize_value'))
    
    def test_python_renderer_has_serialize_string(self):
        """Test that PythonRenderer has _serialize_string method."""
        assert hasattr(PythonRenderer, '_serialize_string')
        assert callable(getattr(PythonRenderer, '_serialize_string'))
    
    def test_python_renderer_has_setup_jinja_env(self):
        """Test that PythonRenderer has _setup_jinja_env method."""
        assert hasattr(PythonRenderer, '_setup_jinja_env')
        assert callable(getattr(PythonRenderer, '_setup_jinja_env'))


class TestPythonRendererDocumentation:
    """Tests for PythonRenderer documentation."""
    
    def test_class_has_docstring(self):
        """Test that PythonRenderer class has docstring."""
        assert PythonRenderer.__doc__ is not None
        assert "Base class for Python code renderers" in PythonRenderer.__doc__
    
    def test_serialize_value_has_docstring(self):
        """Test that serialize_value method has docstring."""
        assert PythonRenderer.serialize_value.__doc__ is not None
        assert "Serialize a Python value" in PythonRenderer.serialize_value.__doc__
    
    def test_serialize_string_has_docstring(self):
        """Test that _serialize_string method has docstring."""
        assert PythonRenderer._serialize_string.__doc__ is not None
        assert "smart quote selection" in PythonRenderer._serialize_string.__doc__
    
    def test_setup_jinja_env_has_docstring(self):
        """Test that _setup_jinja_env method has docstring."""
        assert PythonRenderer._setup_jinja_env.__doc__ is not None
        assert "whitespace control" in PythonRenderer._setup_jinja_env.__doc__
