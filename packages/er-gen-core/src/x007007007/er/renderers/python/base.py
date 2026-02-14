"""Base class for Python code renderers."""
from typing import Any
from x007007007.er.renderers.base import Renderer


class PythonRenderer(Renderer):
    """
    Base class for Python code renderers (Django, SQLAlchemy, etc.)
    Python 代码渲染器的基类（Django、SQLAlchemy 等）
    
    Provides shared Python code serialization logic.
    提供共享的 Python 代码序列化逻辑。
    """
    
    def serialize_value(self, value: Any, context: str = 'default') -> str:
        """
        Serialize a Python value to its code representation.
        将 Python 值序列化为其代码表示。
        
        Examples / 示例:
            serialize_value(None) -> "None"
            serialize_value(True) -> "True"
            serialize_value(42) -> "42"
            serialize_value("hello") -> '"hello"'
            serialize_value('say "hi"') -> '\'say "hi"\''
            serialize_value([1, 2, 3]) -> "[1, 2, 3]"
        """
        if value is None:
            return "None"
        
        if isinstance(value, bool):
            return "True" if value else "False"
        
        if isinstance(value, (int, float)):
            return str(value)
        
        if isinstance(value, str):
            return self._serialize_string(value)
        
        if isinstance(value, list):
            elements = [self.serialize_value(item, context) for item in value]
            return "[" + ", ".join(elements) + "]"
        
        if isinstance(value, dict):
            items = [
                f"{self.serialize_value(k, context)}: {self.serialize_value(v, context)}"
                for k, v in value.items()
            ]
            return "{" + ", ".join(items) + "}"
        
        raise ValueError(f"Unsupported type for serialization: {type(value)}")

    def _serialize_string(self, s: str) -> str:
        """
        Serialize a string with smart quote selection.
        使用智能引号选择序列化字符串。
        
        Strategy / 策略:
        1. If string has only double quotes (no single), use single quotes
           如果字符串只有双引号（无单引号），使用单引号
        2. If string has only single quotes (no double), use double quotes
           如果字符串只有单引号（无双引号），使用双引号
        3. If string has both or neither, use double quotes
           如果字符串两者都有或都没有，使用双引号
        """
        # First, escape special characters / 首先，转义特殊字符
        s = s.replace('\\', '\\\\')  # Backslash must be first / 反斜杠必须首先
        s = s.replace('\n', '\\n')
        s = s.replace('\t', '\\t')
        s = s.replace('\r', '\\r')
        
        has_single = "'" in s
        has_double = '"' in s
        
        if has_double and not has_single:
            # Use single quotes / 使用单引号
            return f"'{s}'"
        elif has_single and not has_double:
            # Use double quotes / 使用双引号
            return f'"{s}"'
        elif has_double and has_single:
            # Use double quotes and escape them / 使用双引号并转义
            s = s.replace('"', '\\"')
            return f'"{s}"'
        else:
            # No quotes, use double quotes / 无引号，使用双引号
            return f'"{s}"'
    
    def _setup_jinja_env(self, loader):
        """
        Set up Jinja2 environment with proper whitespace control.
        设置 Jinja2 环境并进行适当的空白控制。
        
        This configures Jinja2 to automatically strip whitespace from lines
        that contain only Jinja2 directives, preventing extra blank lines
        in generated code while maintaining template readability.
        
        这配置 Jinja2 自动从仅包含 Jinja2 指令的行中删除空白，
        防止生成的代码中出现额外的空行，同时保持模板的可读性。
        """
        from jinja2 import Environment, select_autoescape
        
        env = Environment(
            loader=loader,
            autoescape=select_autoescape(),
            # Whitespace control settings / 空白控制设置
            trim_blocks=True,        # Remove first newline after block
            lstrip_blocks=True,      # Strip leading spaces/tabs from block lines
            keep_trailing_newline=True  # Keep final newline in template
        )
        
        return env
