"""
ER建模的Prompt模板管理。

使用Jinja2模板来管理prompt，便于维护和修改。
"""
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from langchain_core.prompts import PromptTemplate

# 获取模板目录路径
_TEMPLATE_DIR = Path(__file__).parent / "templates"
assert _TEMPLATE_DIR.exists(), f"Template directory not found: {_TEMPLATE_DIR}"

# 创建Jinja2环境
_jinja_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True
)


def get_er_modeling_prompt() -> PromptTemplate:
    """
    获取ER建模的Prompt模板。
    
    从Jinja2模板文件加载prompt，支持变量替换。
    策略：直接读取模板文件，将所有{ }转义为{{ }}（除了{{ requirement }}），
    然后将{{ requirement }}转换为{requirement}（LangChain格式）。
    这样LangChain会将{{ }}解析为字面的{ }，不会识别为变量。
    
    Returns:
        PromptTemplate: LangChain的PromptTemplate对象
    """
    # 直接读取模板文件
    template_file = _TEMPLATE_DIR / "er_modeling_prompt.j2"
    assert template_file.exists(), f"Template file not found: {template_file}"
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    import re
    
    # 策略：将所有{ }转义为{{ }}，但保留{{ requirement }}不变
    # 步骤1: 先保护{{ requirement }}，用占位符替换
    placeholder = "___REQUIREMENT_PLACEHOLDER___"
    content = re.sub(r'\{\{\s*requirement\s*\}\}', placeholder, content)
    
    # 步骤2: 将所有剩余的{转义为{{，}转义为}}
    content = content.replace("{", "{{").replace("}", "}}")
    
    # 步骤3: 将占位符替换回{requirement}（LangChain格式，单个大括号）
    content = content.replace(placeholder, "{requirement}")
    
    # 创建LangChain的PromptTemplate
    return PromptTemplate(
        input_variables=["requirement"],
        template=content
    )


def get_er_modeling_prompt_text(requirement: str) -> str:
    """
    直接获取渲染后的prompt文本。
    
    Args:
        requirement: 用户需求描述
        
    Returns:
        str: 渲染后的prompt文本
    """
    assert isinstance(requirement, str), "requirement must be a string"
    template = _jinja_env.get_template("er_modeling_prompt.j2")
    return template.render(requirement=requirement)


def get_refine_prompt() -> PromptTemplate:
    """
    获取基于现有TOML进行修改的Prompt模板。
    
    当需要基于现有TOML进行修改时，使用此模板。
    
    Returns:
        PromptTemplate: LangChain的PromptTemplate对象
    """
    # 直接读取模板文件
    template_file = _TEMPLATE_DIR / "refine_prompt.j2"
    assert template_file.exists(), f"Template file not found: {template_file}"
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    import re
    
    # 策略：将所有{ }转义为{{ }}，但保留{{ existing_toml }}和{{ modification_request }}
    # 步骤1: 先保护变量，用占位符替换
    existing_placeholder = "___EXISTING_TOML_PLACEHOLDER___"
    mod_placeholder = "___MODIFICATION_REQUEST_PLACEHOLDER___"
    content = re.sub(r'\{\{\s*existing_toml\s*\}\}', existing_placeholder, content)
    content = re.sub(r'\{\{\s*modification_request\s*\}\}', mod_placeholder, content)
    
    # 步骤2: 将所有剩余的{转义为{{，}转义为}}
    content = content.replace("{", "{{").replace("}", "}}")
    
    # 步骤3: 将占位符替换回变量（LangChain格式，单个大括号）
    content = content.replace(existing_placeholder, "{existing_toml}")
    content = content.replace(mod_placeholder, "{modification_request}")
    
    # 创建LangChain的PromptTemplate
    return PromptTemplate(
        input_variables=["existing_toml", "modification_request"],
        template=content
    )


def get_error_feedback_prompt() -> PromptTemplate:
    """
    获取错误反馈的Prompt模板。
    
    当TOML验证失败时，使用此模板生成错误反馈prompt。
    
    Returns:
        PromptTemplate: LangChain的PromptTemplate对象
    """
    # 直接读取模板文件
    template_file = _TEMPLATE_DIR / "error_feedback_prompt.j2"
    assert template_file.exists(), f"Template file not found: {template_file}"
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    import re
    
    # 策略：将所有{ }转义为{{ }}，但保留{{ error_message }}和{{ requirement }}
    # 步骤1: 先保护变量，用占位符替换
    error_placeholder = "___ERROR_MESSAGE_PLACEHOLDER___"
    req_placeholder = "___REQUIREMENT_PLACEHOLDER___"
    content = re.sub(r'\{\{\s*error_message\s*\}\}', error_placeholder, content)
    content = re.sub(r'\{\{\s*requirement\s*\}\}', req_placeholder, content)
    
    # 步骤2: 将所有剩余的{转义为{{，}转义为}}
    content = content.replace("{", "{{").replace("}", "}}")
    
    # 步骤3: 将占位符替换回变量（LangChain格式，单个大括号）
    content = content.replace(error_placeholder, "{error_message}")
    content = content.replace(req_placeholder, "{requirement}")
    
    # 创建LangChain的PromptTemplate
    return PromptTemplate(
        input_variables=["error_message", "requirement"],
        template=content
    )

