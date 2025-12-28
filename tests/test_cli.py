from click.testing import CliRunner
from x007007007.er.cli import main
import os

def test_cli_mermaid_to_django(tmp_path):
    runner = CliRunner()
    input_file = tmp_path / "test.mermaid"
    input_file.write_text("""
erDiagram
    USER {
        int id PK
        string name
    }
""", encoding='utf-8')
    
    output_file = tmp_path / "output.py"
    result = runner.invoke(main, ['convert', str(input_file), '--format', 'django', '--output', str(output_file)])
    
    assert result.exit_code == 0
    assert os.path.exists(output_file)
    content = output_file.read_text(encoding='utf-8')
    assert "class USER(models.Model):" in content

def test_cli_mermaid_to_sqlalchemy(tmp_path):
    runner = CliRunner()
    input_file = tmp_path / "test.mermaid"
    input_file.write_text("""
erDiagram
    USER {
        int id PK
        string name
    }
""", encoding='utf-8')
    
    output_file = tmp_path / "output_sa.py"
    result = runner.invoke(main, ['convert', str(input_file), '--format', 'sqlalchemy', '--output', str(output_file)])
    
    assert result.exit_code == 0
    assert os.path.exists(output_file)
    content = output_file.read_text(encoding='utf-8')
    assert "class USER(Base):" in content
