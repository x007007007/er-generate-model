"""
TOML语法验证器。
"""
import toml
from typing import Tuple, Optional
from x007007007.er.parser.toml_parser import TomlERParser


def validate_toml_syntax(content: str) -> Tuple[bool, Optional[str]]:
    """
    验证TOML语法是否正确。
    
    Args:
        content: TOML格式的字符串内容
        
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        如果有效，返回(True, None)
        如果无效，返回(False, 错误描述)
    """
    assert isinstance(content, str), "content must be a string"
    
    if not content.strip():
        return False, "TOML内容为空"
    
    # 步骤1: 验证TOML语法
    try:
        toml.loads(content)
    except toml.TomlDecodeError as e:
        return False, f"TOML语法错误: {str(e)}"
    except Exception as e:
        return False, f"TOML解析异常: {str(e)}"
    
    # 步骤2: 验证ER模型结构（使用TOML ER解析器）
    try:
        parser = TomlERParser()
        model = parser.parse(content)
        
        # 验证模型结构
        errors = model.validate()
        if errors:
            return False, f"ER模型验证失败: {'; '.join(errors)}"
        
        return True, None
    except ValueError as e:
        return False, f"ER模型解析错误: {str(e)}"
    except Exception as e:
        return False, f"ER模型验证异常: {str(e)}"


def extract_toml_from_markdown(content: str) -> str:
    """
    从markdown代码块中提取TOML内容。
    
    Args:
        content: 可能包含markdown代码块的文本
        
    Returns:
        str: 提取的TOML内容
    """
    assert isinstance(content, str), "content must be a string"
    
    content = content.strip()
    
    # 如果包含```toml或```，提取代码块内容
    if "```" in content:
        lines = content.split("\n")
        start_idx = None
        end_idx = None
        
        for i, line in enumerate(lines):
            if line.strip().startswith("```"):
                if start_idx is None:
                    start_idx = i + 1
                else:
                    end_idx = i
                    break
        
        if start_idx is not None and end_idx is not None:
            return "\n".join(lines[start_idx:end_idx])
    
    return content

