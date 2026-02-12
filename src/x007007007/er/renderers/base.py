"""Base renderer class for all code generators."""
from abc import ABC, abstractmethod
from typing import Any
from x007007007.er.models import ERModel


class Renderer(ABC):
    """
    Base class for all renderers.
    所有渲染器的基类。
    """
    
    @abstractmethod
    def render(self, model: ERModel) -> str:
        """
        Render the model to code.
        将模型渲染为代码。
        
        Args:
            model: The ERModel to render / 要渲染的 ERModel
            
        Returns:
            Generated code as string / 生成的代码字符串
        """
        pass
    
    def serialize_value(self, value: Any, context: str = 'default') -> str:
        """
        Convert a Python value to its code string representation.
        将 Python 值转换为其代码字符串表示。
        
        This method should be overridden by language-specific renderers
        to provide appropriate serialization for that language.
        此方法应由特定语言的渲染器覆盖，以提供该语言的适当序列化。
        
        Args:
            value: The Python value to serialize / 要序列化的 Python 值
            context: Context hint ('default', 'comment', 'name', etc.) / 上下文提示
            
        Returns:
            A string suitable for direct insertion into code / 适合直接插入代码的字符串
        """
        raise NotImplementedError("Subclasses must implement serialize_value")
