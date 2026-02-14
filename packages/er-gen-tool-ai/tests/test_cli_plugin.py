"""
Tests for CLI plugin interface.
"""
import pytest
from click.testing import CliRunner
from x007007007.er_tool_ai.cli_plugin import ai_assist_cmd, generate, refine, chat


def test_ai_assist_cmd_group():
    """Test that ai_assist_cmd is a Click group."""
    assert hasattr(ai_assist_cmd, 'commands')
    assert 'generate' in ai_assist_cmd.commands
    assert 'refine' in ai_assist_cmd.commands
    assert 'chat' in ai_assist_cmd.commands


def test_generate_command_exists():
    """Test that generate command is registered."""
    runner = CliRunner()
    result = runner.invoke(ai_assist_cmd, ['generate', '--help'])
    assert result.exit_code == 0
    assert 'Generate ER model from requirements' in result.output


def test_refine_command_exists():
    """Test that refine command is registered."""
    runner = CliRunner()
    result = runner.invoke(ai_assist_cmd, ['refine', '--help'])
    assert result.exit_code == 0
    assert 'Refine existing TOML configuration' in result.output


def test_chat_command_exists():
    """Test that chat command is registered."""
    runner = CliRunner()
    result = runner.invoke(ai_assist_cmd, ['chat', '--help'])
    assert result.exit_code == 0
    assert 'Interactive refinement' in result.output


def test_generate_missing_requirement():
    """Test that generate command fails without requirement."""
    runner = CliRunner()
    result = runner.invoke(ai_assist_cmd, ['generate'])
    assert result.exit_code == 1
    assert 'Error: requirement is required' in result.output


def test_generate_with_stdin(tmp_path):
    """Test that generate command accepts input from stdin."""
    runner = CliRunner()
    # This will fail without API key, but we're testing the input handling
    result = runner.invoke(ai_assist_cmd, ['generate'], input='设计一个博客系统')
    # Should fail due to missing API key, not missing requirement
    assert 'requirement is required' not in result.output


def test_refine_missing_file():
    """Test that refine command fails with non-existent file."""
    runner = CliRunner()
    result = runner.invoke(ai_assist_cmd, ['refine', 'nonexistent.toml', '添加评论功能'])
    assert result.exit_code != 0


def test_refine_missing_modification_request(tmp_path):
    """Test that refine command fails without modification request."""
    # Create a temporary TOML file
    toml_file = tmp_path / "test.toml"
    toml_file.write_text("[entities]\n")
    
    runner = CliRunner()
    result = runner.invoke(ai_assist_cmd, ['refine', str(toml_file)])
    assert result.exit_code == 1
    assert 'Error: modification_request is required' in result.output


def test_chat_missing_file():
    """Test that chat command fails with non-existent file."""
    runner = CliRunner()
    result = runner.invoke(ai_assist_cmd, ['chat', 'nonexistent.toml'])
    assert result.exit_code != 0
