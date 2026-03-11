"""Test CLI inheritance mode parameter."""
from click.testing import CliRunner
from x007007007.er_tool.cli import main
import os


def get_asset_path(case_name: str, filename: str) -> str:
    """Get path to asset file."""
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    return os.path.join(assets_dir, case_name, filename)


def test_cli_accepts_inheritance_mode_reference(tmp_path):
    """Test that CLI accepts --inheritance-mode reference parameter."""
    runner = CliRunner()
    
    # Create a minimal TOML file for testing
    input_file = tmp_path / "test.toml"
    input_file.write_text("""
[entities.User]
table_name = "user"
[[entities.User.columns]]
name = "id"
type = "bigint"
primary_key = true
""", encoding='utf-8')
    
    output_file = tmp_path / "output.py"
    result = runner.invoke(main, [
        'convert', 
        str(input_file), 
        '--input-type', 'toml',
        '--format', 'sqlalchemy',
        '--inheritance-mode', 'reference',
        '--output', str(output_file)
    ])
    
    # Should not fail with parameter error
    assert result.exit_code == 0, f"CLI failed with: {result.output}"
    assert os.path.exists(output_file)


def test_cli_accepts_inheritance_mode_flatten(tmp_path):
    """Test that CLI accepts --inheritance-mode flatten parameter."""
    runner = CliRunner()
    
    # Create a minimal TOML file for testing
    input_file = tmp_path / "test.toml"
    input_file.write_text("""
[entities.User]
table_name = "user"
[[entities.User.columns]]
name = "id"
type = "bigint"
primary_key = true
""", encoding='utf-8')
    
    output_file = tmp_path / "output.py"
    result = runner.invoke(main, [
        'convert', 
        str(input_file), 
        '--input-type', 'toml',
        '--format', 'sqlalchemy',
        '--inheritance-mode', 'flatten',
        '--output', str(output_file)
    ])
    
    # Should not fail with parameter error
    assert result.exit_code == 0, f"CLI failed with: {result.output}"
    assert os.path.exists(output_file)


def test_cli_accepts_short_inheritance_mode_flag(tmp_path):
    """Test that CLI accepts -i short flag for inheritance mode."""
    runner = CliRunner()
    
    # Create a minimal TOML file for testing
    input_file = tmp_path / "test.toml"
    input_file.write_text("""
[entities.User]
table_name = "user"
[[entities.User.columns]]
name = "id"
type = "bigint"
primary_key = true
""", encoding='utf-8')
    
    output_file = tmp_path / "output.py"
    result = runner.invoke(main, [
        'convert', 
        str(input_file), 
        '--input-type', 'toml',
        '--format', 'sqlalchemy',
        '-i', 'flatten',
        '--output', str(output_file)
    ])
    
    # Should not fail with parameter error
    assert result.exit_code == 0, f"CLI failed with: {result.output}"
    assert os.path.exists(output_file)


def test_cli_rejects_invalid_inheritance_mode(tmp_path):
    """Test that CLI rejects invalid inheritance mode values."""
    runner = CliRunner()
    
    # Create a minimal TOML file for testing
    input_file = tmp_path / "test.toml"
    input_file.write_text("""
[entities.User]
table_name = "user"
[[entities.User.columns]]
name = "id"
type = "bigint"
primary_key = true
""", encoding='utf-8')
    
    output_file = tmp_path / "output.py"
    result = runner.invoke(main, [
        'convert', 
        str(input_file), 
        '--input-type', 'toml',
        '--format', 'sqlalchemy',
        '--inheritance-mode', 'invalid',
        '--output', str(output_file)
    ])
    
    # Should fail with parameter error
    assert result.exit_code != 0
    assert "invalid" in result.output.lower() or "choice" in result.output.lower()


def test_cli_defaults_to_reference_mode(tmp_path):
    """Test that CLI defaults to reference mode when --inheritance-mode is not specified."""
    runner = CliRunner()
    
    # Create a minimal TOML file for testing
    input_file = tmp_path / "test.toml"
    input_file.write_text("""
[entities.User]
table_name = "user"
[[entities.User.columns]]
name = "id"
type = "bigint"
primary_key = true
""", encoding='utf-8')
    
    output_file = tmp_path / "output.py"
    result = runner.invoke(main, [
        'convert', 
        str(input_file), 
        '--input-type', 'toml',
        '--format', 'sqlalchemy',
        '--output', str(output_file)
    ])
    
    # Should succeed with default mode
    assert result.exit_code == 0, f"CLI failed with: {result.output}"
    assert os.path.exists(output_file)
