"""
Test for task 5.4: Convert subcommand implementation

This test verifies that the convert subcommand is properly implemented
with all required options as specified in the design document.
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from x007007007.er_tool.convert import convert_cmd
import click


def test_convert_command_exists():
    """Test that convert_cmd is a Click command"""
    assert isinstance(convert_cmd, click.Command)
    print("✓ convert_cmd is a Click command")


def test_convert_command_has_required_options():
    """Test that convert command has all required options"""
    # Get all parameters
    params = {p.name: p for p in convert_cmd.params}
    
    # Check required argument
    assert 'input_source' in params
    assert isinstance(params['input_source'], click.Argument)
    print("✓ input_source argument exists")
    
    # Check all required options
    required_options = [
        'input_type',
        'format',
        'output',
        'output_dir',
        'app_label',
        'table_prefix',
        'split_models'
    ]
    
    for option in required_options:
        assert option in params, f"Missing option: {option}"
        assert isinstance(params[option], click.Option), f"{option} is not an Option"
        print(f"✓ {option} option exists")


def test_input_type_choices():
    """Test that input_type has correct choices"""
    params = {p.name: p for p in convert_cmd.params}
    input_type = params['input_type']
    
    # Get the type from the option
    assert hasattr(input_type.type, 'choices')
    choices = input_type.type.choices
    
    expected_choices = ['mermaid', 'plantuml', 'db', 'toml']
    for choice in expected_choices:
        assert choice in choices, f"Missing input type: {choice}"
        print(f"✓ input_type supports: {choice}")


def test_format_choices():
    """Test that format has correct choices"""
    params = {p.name: p for p in convert_cmd.params}
    format_param = params['format']
    
    # Get the type from the option
    assert hasattr(format_param.type, 'choices')
    choices = format_param.type.choices
    
    expected_choices = ['django', 'sqlalchemy', 'mermaid', 'plantuml']
    for choice in expected_choices:
        assert choice in choices, f"Missing format: {choice}"
        print(f"✓ format supports: {choice}")


def test_split_models_is_flag():
    """Test that split_models is a boolean flag"""
    params = {p.name: p for p in convert_cmd.params}
    split_models = params['split_models']
    
    assert split_models.is_flag, "split_models should be a flag"
    print("✓ split_models is a flag")


def test_command_has_help_text():
    """Test that command has help text"""
    assert convert_cmd.help is not None
    assert len(convert_cmd.help) > 0
    print(f"✓ Command has help text: {convert_cmd.help}")


if __name__ == '__main__':
    print("Testing task 5.4: Convert subcommand implementation\n")
    
    test_convert_command_exists()
    test_convert_command_has_required_options()
    test_input_type_choices()
    test_format_choices()
    test_split_models_is_flag()
    test_command_has_help_text()
    
    print("\n✅ All tests passed! Task 5.4 is complete.")
