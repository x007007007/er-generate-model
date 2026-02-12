"""
Unit tests for CLI default behavior and backward compatibility.
"""
import os
import tempfile
from click.testing import CliRunner
from x007007007.er.cli import main


def test_cli_default_input_type_is_toml():
    """Test that CLI defaults to TOML input type."""
    runner = CliRunner()
    
    # Create a simple TOML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write("""
[entities.User]
columns = [
    { name = "id", type = "int", is_pk = true, nullable = false },
    { name = "name", type = "varchar", max_length = 100, nullable = false }
]
""")
        toml_file = f.name
    
    try:
        # Run without --input-type flag (should default to toml)
        result = runner.invoke(main, ['convert', toml_file, '--format', 'django'])
        
        # Should succeed with TOML input
        assert result.exit_code == 0, f"CLI failed with: {result.output}"
        assert 'class User' in result.output
        assert 'models.Model' in result.output
    finally:
        os.unlink(toml_file)


def test_cli_explicit_input_type_mermaid():
    """Test that CLI accepts explicit --input-type mermaid for backward compatibility."""
    runner = CliRunner()
    
    # Create a simple Mermaid file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False) as f:
        f.write("""
erDiagram
    User {
        int id PK
        varchar name
    }
""")
        mermaid_file = f.name
    
    try:
        # Run with explicit --input-type mermaid
        result = runner.invoke(main, ['convert', mermaid_file, '--input-type', 'mermaid', '--format', 'django'])
        
        # Should succeed with Mermaid input
        assert result.exit_code == 0, f"CLI failed with: {result.output}"
        assert 'class User' in result.output
        assert 'models.Model' in result.output
    finally:
        os.unlink(mermaid_file)


def test_cli_explicit_input_type_plantuml():
    """Test that CLI accepts explicit --input-type plantuml."""
    runner = CliRunner()
    
    # Create a simple PlantUML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False) as f:
        f.write("""
@startuml
entity User {
    * id : int <<PK>>
    name : varchar
}
@enduml
""")
        plantuml_file = f.name
    
    try:
        # Run with explicit --input-type plantuml
        result = runner.invoke(main, ['convert', plantuml_file, '--input-type', 'plantuml', '--format', 'django'])
        
        # Should succeed with PlantUML input
        assert result.exit_code == 0, f"CLI failed with: {result.output}"
        assert 'class User' in result.output
        assert 'models.Model' in result.output
    finally:
        os.unlink(plantuml_file)


def test_cli_help_shows_toml_as_default():
    """Test that CLI help text shows 'toml' as the default input type."""
    runner = CliRunner()
    
    # Get help text
    result = runner.invoke(main, ['convert', '--help'])
    
    assert result.exit_code == 0
    # Check that help text mentions toml as default
    assert 'default: toml' in result.output.lower() or 'toml' in result.output


def test_cli_toml_with_default_values():
    """Test that CLI handles TOML files with default values correctly."""
    runner = CliRunner()
    
    # Create a TOML file with default values
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write("""
[entities.Post]
columns = [
    { name = "id", type = "int", is_pk = true, nullable = false },
    { name = "title", type = "varchar", max_length = 200, nullable = false, default = "Untitled" },
    { name = "published", type = "boolean", nullable = false, default = false }
]
""")
        toml_file = f.name
    
    try:
        # Run without --input-type flag (should default to toml)
        result = runner.invoke(main, ['convert', toml_file, '--format', 'django'])
        
        # Should succeed and include default values
        assert result.exit_code == 0, f"CLI failed with: {result.output}"
        assert 'class Post' in result.output
        assert 'default=' in result.output
        # Check that default values are properly serialized
        assert 'Untitled' in result.output
        assert 'False' in result.output
    finally:
        os.unlink(toml_file)


def test_cli_toml_with_comments():
    """Test that CLI handles TOML files with comments (help_text) correctly."""
    runner = CliRunner()
    
    # Create a TOML file with comments
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write("""
[entities.Article]
columns = [
    { name = "id", type = "int", is_pk = true, nullable = false },
    { name = "content", type = "text", nullable = false, comment = "Article content" }
]
""")
        toml_file = f.name
    
    try:
        # Run without --input-type flag (should default to toml)
        result = runner.invoke(main, ['convert', toml_file, '--format', 'django'])
        
        # Should succeed and include help_text
        assert result.exit_code == 0, f"CLI failed with: {result.output}"
        assert 'class Article' in result.output
        assert 'help_text=' in result.output
        assert 'Article content' in result.output
    finally:
        os.unlink(toml_file)


def test_cli_toml_with_quotes_in_values():
    """Test that CLI handles TOML files with quotes in default values and comments."""
    runner = CliRunner()
    
    # Create a TOML file with quotes in values
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write("""
[entities.Product]
columns = [
    { name = "id", type = "int", is_pk = true, nullable = false },
    { name = "name", type = "varchar", max_length = 100, nullable = false, comment = 'Product "name"' }
]
""")
        toml_file = f.name
    
    try:
        # Run without --input-type flag (should default to toml)
        result = runner.invoke(main, ['convert', toml_file, '--format', 'django'])
        
        # Should succeed and properly escape quotes
        assert result.exit_code == 0, f"CLI failed with: {result.output}"
        assert 'class Product' in result.output
        # The output should have properly escaped quotes
        assert 'help_text=' in result.output
    finally:
        os.unlink(toml_file)


def test_cli_backward_compatibility_mermaid_without_flag():
    """Test that Mermaid files still work when explicitly specifying input type."""
    runner = CliRunner()
    
    # Create a Mermaid file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mermaid', delete=False) as f:
        f.write("""
erDiagram
    User {
        int id PK
        varchar name
    }
""")
        mermaid_file = f.name
    
    try:
        # This should work with explicit --input-type mermaid
        result = runner.invoke(main, ['convert', mermaid_file, '--input-type', 'mermaid', '--format', 'django'])
        assert result.exit_code == 0, f"CLI failed with: {result.output}"
        
        # But should fail without --input-type (since default is now toml)
        result_no_flag = runner.invoke(main, ['convert', mermaid_file, '--format', 'django'])
        # This will fail because it tries to parse Mermaid as TOML
        assert result_no_flag.exit_code != 0
    finally:
        os.unlink(mermaid_file)


def test_cli_sqlalchemy_with_toml_default():
    """Test that CLI works with SQLAlchemy output format and TOML input."""
    runner = CliRunner()
    
    # Create a TOML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        f.write("""
[entities.User]
columns = [
    { name = "id", type = "int", is_pk = true, nullable = false },
    { name = "email", type = "varchar", max_length = 255, nullable = false }
]
""")
        toml_file = f.name
    
    try:
        # Run with SQLAlchemy format
        result = runner.invoke(main, ['convert', toml_file, '--format', 'sqlalchemy'])
        
        # Should succeed
        assert result.exit_code == 0, f"CLI failed with: {result.output}"
        assert 'class User' in result.output
        assert 'Base' in result.output or 'declarative_base' in result.output
    finally:
        os.unlink(toml_file)
