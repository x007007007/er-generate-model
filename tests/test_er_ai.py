"""
ER AI工具测试。
"""
import pytest
import os
from unittest.mock import Mock, patch
from x007007007.er_ai.modeler import ERModeler
from x007007007.er_ai.sdk import generate_er_model


def test_er_modeler_init_without_api_key():
    """测试没有API密钥时抛出错误。"""
    # 清除环境变量
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="API key is required"):
            ERModeler()


def test_er_modeler_init_with_api_key():
    """测试使用API密钥初始化。"""
    with patch('x007007007.er_ai.modeler.ChatOpenAI') as mock_chat:
        modeler = ERModeler(api_key="test-key")
        assert modeler is not None
        mock_chat.assert_called_once()


def test_er_modeler_generate_toml():
    """测试生成TOML配置。"""
    mock_response = Mock()
    mock_response.content = """
[templates.create_update_time]
columns = [
    {name = "created_at", type = "datetime"},
]

[entities.USER]
extends = ["create_update_time"]
columns = [
    {name = "id", type = "int", is_pk = true},
    {name = "username", type = "string"},
]
"""
    
    with patch('x007007007.er_ai.modeler.ChatOpenAI') as mock_chat_class:
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_chat_class.return_value = mock_llm
        
        modeler = ERModeler(api_key="test-key")
        
        # Mock chain invoke
        with patch.object(modeler, 'prompt') as mock_prompt:
            mock_chain = Mock()
            mock_chain.invoke.return_value = mock_response
            modeler.prompt.__or__ = Mock(return_value=mock_chain)
            
            result = modeler.generate_toml("设计一个用户系统")
            assert "entities.USER" in result
            assert "templates.create_update_time" in result


def test_er_modeler_clean_output():
    """测试清理输出功能。"""
    with patch('x007007007.er_ai.modeler.ChatOpenAI'):
        modeler = ERModeler(api_key="test-key")
        
        # 测试移除markdown代码块
        output_with_markdown = "```toml\n[entities.USER]\n```"
        cleaned = modeler._clean_output(output_with_markdown)
        assert "```" not in cleaned
        assert "[entities.USER]" in cleaned


def test_sdk_generate_er_model():
    """测试SDK接口。"""
    with patch('x007007007.er_ai.sdk.ERModeler') as mock_modeler_class:
        mock_modeler = Mock()
        mock_modeler.generate_toml.return_value = "[entities.USER]\ncolumns = []"
        mock_modeler_class.return_value = mock_modeler
        
        result = generate_er_model("设计一个用户系统", api_key="test-key")
        assert "[entities.USER]" in result
        mock_modeler.generate_toml.assert_called_once_with("设计一个用户系统")

