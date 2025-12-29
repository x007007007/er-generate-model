"""
ER AI验证器测试。
"""
import pytest
from x007007007.er_ai.validator import validate_toml_syntax, extract_toml_from_markdown


def test_validate_toml_syntax_valid():
    """测试有效的TOML语法。"""
    valid_toml = """
[entities.USER]
columns = [
    {name = "id", type = "int", is_pk = true},
    {name = "username", type = "string"},
]
"""
    is_valid, error = validate_toml_syntax(valid_toml)
    assert is_valid is True
    assert error is None


def test_validate_toml_syntax_invalid():
    """测试无效的TOML语法。"""
    invalid_toml = "[entities.USER\ncolumns = [\n"
    is_valid, error = validate_toml_syntax(invalid_toml)
    assert is_valid is False
    assert error is not None
    assert "TOML语法错误" in error or "TOML解析" in error


def test_validate_toml_syntax_empty():
    """测试空内容。"""
    is_valid, error = validate_toml_syntax("")
    assert is_valid is False
    assert error is not None
    assert "空" in error


def test_extract_toml_from_markdown():
    """测试从markdown代码块中提取TOML。"""
    markdown = """```toml
[entities.USER]
columns = []
```
"""
    toml = extract_toml_from_markdown(markdown)
    assert "[entities.USER]" in toml
    assert "```" not in toml


def test_extract_toml_from_plain():
    """测试从普通文本中提取TOML（无markdown）。"""
    plain = "[entities.USER]\ncolumns = []"
    toml = extract_toml_from_markdown(plain)
    assert toml == plain

