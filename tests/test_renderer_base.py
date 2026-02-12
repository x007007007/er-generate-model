"""
Unit tests for Renderer base class.
"""
import pytest
from abc import ABC
from x007007007.er.renderers.base import Renderer
from x007007007.er.models import ERModel


def test_renderer_is_abstract():
    """Test that Renderer is an abstract base class."""
    assert issubclass(Renderer, ABC)
    
    # Should not be able to instantiate directly
    with pytest.raises(TypeError):
        Renderer()


def test_renderer_has_render_method():
    """Test that Renderer has abstract render method."""
    assert hasattr(Renderer, 'render')
    assert callable(getattr(Renderer, 'render'))


def test_renderer_has_serialize_value_method():
    """Test that Renderer has serialize_value method."""
    assert hasattr(Renderer, 'serialize_value')
    assert callable(getattr(Renderer, 'serialize_value'))


def test_concrete_renderer_must_implement_render():
    """Test that concrete renderers must implement render method."""
    
    class IncompleteRenderer(Renderer):
        """Renderer without render implementation."""
        def serialize_value(self, value, context='default'):
            return str(value)
    
    # Should not be able to instantiate without implementing render
    with pytest.raises(TypeError):
        IncompleteRenderer()


def test_concrete_renderer_can_be_instantiated():
    """Test that concrete renderers with all methods can be instantiated."""
    
    class CompleteRenderer(Renderer):
        """Complete renderer implementation."""
        def render(self, model):
            return "rendered code"
        
        def serialize_value(self, value, context='default'):
            return str(value)
    
    # Should be able to instantiate
    renderer = CompleteRenderer()
    assert isinstance(renderer, Renderer)


def test_serialize_value_raises_not_implemented_by_default():
    """Test that base serialize_value raises NotImplementedError."""
    
    class MinimalRenderer(Renderer):
        """Minimal renderer with only render implemented."""
        def render(self, model):
            return "rendered code"
    
    renderer = MinimalRenderer()
    
    # serialize_value should raise NotImplementedError
    with pytest.raises(NotImplementedError, match="Subclasses must implement serialize_value"):
        renderer.serialize_value("test")


def test_render_method_signature():
    """Test that render method has correct signature."""
    
    class TestRenderer(Renderer):
        """Test renderer."""
        def render(self, model):
            assert isinstance(model, ERModel)
            return "code"
        
        def serialize_value(self, value, context='default'):
            return str(value)
    
    renderer = TestRenderer()
    
    # Create a minimal ERModel
    model = ERModel(entities={}, relationships=[], templates={})
    
    # Should accept ERModel
    result = renderer.render(model)
    assert result == "code"


def test_serialize_value_method_signature():
    """Test that serialize_value method has correct signature."""
    
    class TestRenderer(Renderer):
        """Test renderer."""
        def render(self, model):
            return "code"
        
        def serialize_value(self, value, context='default'):
            return f"value={value}, context={context}"
    
    renderer = TestRenderer()
    
    # Should accept value and optional context
    result1 = renderer.serialize_value("test")
    assert "value=test" in result1
    assert "context=default" in result1
    
    result2 = renderer.serialize_value("test", "comment")
    assert "value=test" in result2
    assert "context=comment" in result2


def test_renderer_docstrings():
    """Test that Renderer class and methods have proper documentation."""
    assert Renderer.__doc__ is not None
    assert "Base class for all renderers" in Renderer.__doc__
    
    assert Renderer.render.__doc__ is not None
    assert "Render the model to code" in Renderer.render.__doc__
    
    assert Renderer.serialize_value.__doc__ is not None
    assert "Convert a Python value to its code string representation" in Renderer.serialize_value.__doc__
