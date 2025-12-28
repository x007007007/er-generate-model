from click.testing import CliRunner
from x007007007.er.cli import main
import os

def get_asset_path(case_name: str, filename: str) -> str:
    """Get path to asset file."""
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    return os.path.join(assets_dir, case_name, filename)

def test_cli_mermaid_to_django(tmp_path):
    runner = CliRunner()
    input_file = get_asset_path("cli_django", "input.mermaid")
    expected_file = get_asset_path("cli_django", "django.py")
    
    output_file = tmp_path / "output.py"
    result = runner.invoke(main, ['convert', input_file, '--format', 'django', '--output', str(output_file)])
    
    assert result.exit_code == 0
    assert os.path.exists(output_file)
    actual_content = output_file.read_text(encoding='utf-8')
    
    # Compare with expected output
    with open(expected_file, "r", encoding="utf-8") as f:
        expected_content = f.read()
    assert actual_content == expected_content, "CLI Django output does not match expected file"

def test_cli_mermaid_to_sqlalchemy(tmp_path):
    runner = CliRunner()
    input_file = get_asset_path("cli_sqlalchemy", "input.mermaid")
    expected_file = get_asset_path("cli_sqlalchemy", "sqlalchemy.py")
    
    output_file = tmp_path / "output_sa.py"
    result = runner.invoke(main, ['convert', input_file, '--format', 'sqlalchemy', '--output', str(output_file)])
    
    assert result.exit_code == 0
    assert os.path.exists(output_file)
    actual_content = output_file.read_text(encoding='utf-8')
    
    # Compare with expected output
    with open(expected_file, "r", encoding="utf-8") as f:
        expected_content = f.read()
    assert actual_content == expected_content, "CLI SQLAlchemy output does not match expected file"
