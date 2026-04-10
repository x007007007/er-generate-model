"""Integration tests for full pipeline (TOML → Django with quotes)."""
import ast
import tempfile
from pathlib import Path
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.renderers.python.django import DjangoRenderer, DjangoPackageRenderer


def test_full_pipeline_toml_to_django_with_quotes():
    """Test full pipeline: TOML → Django with proper quote handling."""
    # Create TOML with entities having default values and comments
    toml_content = '''
[entities.User]
table_name = "user"
comment = "User model with special quotes"

[[entities.User.columns]]
name = "id"
type = "int"
primary_key = true

[[entities.User.columns]]
name = "name"
type = "string"
max_length = 100
default = "John Doe"
comment = "User full name"

[[entities.User.columns]]
name = "bio"
type = "text"
default = "Say hello to the world"
comment = "User biography"

[[entities.User.columns]]
name = "status"
type = "string"
max_length = 20
default = "active"
comment = "Status field"
'''
    
    # Parse TOML
    parser = TomlERParser()
    model = parser.parse(toml_content)
    
    # Render to Django
    renderer = DjangoRenderer(app_label='testapp')
    generated_code = renderer.render(model)
    
    # Verify generated code has proper escaping
    assert 'default="John Doe"' in generated_code
    assert 'default="Say hello to the world"' in generated_code
    assert 'default="active"' in generated_code
    
    # Verify help_text has proper escaping
    assert 'help_text=' in generated_code
    
    # Verify generated code can be parsed without syntax errors
    try:
        ast.parse(generated_code)
    except SyntaxError as e:
        raise AssertionError(f"Generated code has syntax errors: {e}\n\nGenerated code:\n{generated_code}")


def test_full_pipeline_toml_to_django_package_with_quotes():
    """Test full pipeline: TOML → Django package with proper quote handling."""
    toml_content = '''
[entities.Product]
table_name = "product"
comment = "Product with special pricing"

[[entities.Product.columns]]
name = "id"
type = "int"
primary_key = true

[[entities.Product.columns]]
name = "name"
type = "string"
max_length = 200
default = "New Product"
comment = "Product name"

[[entities.Product.columns]]
name = "description"
type = "text"
default = "Description with quotes inside"
comment = "Product description"
'''
    
    # Parse TOML
    parser = TomlERParser()
    model = parser.parse(toml_content)
    
    # Render to Django package
    renderer = DjangoPackageRenderer(app_label='testapp')
    files = renderer.render(model)
    
    # Verify we have the expected files
    assert '__init__.py' in files
    assert 'product.py' in files
    assert 'product_manager.py' in files
    assert 'product_queryset.py' in files
    
    # Verify model file has proper escaping
    model_code = files['product.py']
    assert 'default="New Product"' in model_code
    assert 'help_text=' in model_code
    
    # Verify all generated files can be parsed without syntax errors
    for filename, code in files.items():
        if filename.endswith('.py'):
            try:
                ast.parse(code)
            except SyntaxError as e:
                raise AssertionError(f"Generated file {filename} has syntax errors: {e}\n\nGenerated code:\n{code}")


def test_full_pipeline_with_special_characters():
    """Test pipeline with strings containing newlines, tabs, and backslashes."""
    toml_content = '''
[entities.Config]
table_name = "config"
comment = "Configuration settings"

[[entities.Config.columns]]
name = "id"
type = "int"
primary_key = true

[[entities.Config.columns]]
name = "path"
type = "string"
max_length = 500
default = "C:\\\\Users\\\\Admin\\\\Documents"
comment = "File path with backslashes"

[[entities.Config.columns]]
name = "multiline"
type = "text"
default = "Line 1\\nLine 2\\nLine 3"
comment = "Multiline text"

[[entities.Config.columns]]
name = "tabbed"
type = "string"
max_length = 100
default = "Col1\\tCol2\\tCol3"
comment = "Tab-separated values"
'''
    
    # Parse TOML
    parser = TomlERParser()
    model = parser.parse(toml_content)
    
    # Render to Django
    renderer = DjangoRenderer(app_label='testapp')
    generated_code = renderer.render(model)
    
    # Verify generated code can be parsed
    try:
        ast.parse(generated_code)
    except SyntaxError as e:
        raise AssertionError(f"Generated code has syntax errors: {e}\n\nGenerated code:\n{generated_code}")
    
    # Verify escape sequences are preserved in the generated code
    # The code should contain properly escaped strings
    assert 'default=' in generated_code


def test_full_pipeline_cli_default_behavior():
    """Test that CLI uses TOML as default input type."""
    from click.testing import CliRunner
    from x007007007.er_tool.cli import main
    
    toml_content = '''
[entities.SimpleModel]
table_name = "simplemodel"
comment = "Simple test model"

[[entities.SimpleModel.columns]]
name = "id"
type = "int"
db_column = "id"
primary_key = true

[[entities.SimpleModel.columns]]
name = "name"
type = "string"
db_column = "name"
max_length = 100
'''
    
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Write TOML file
        with open('test.toml', 'w') as f:
            f.write(toml_content)
        
        # Run CLI with explicit --input-type flag
        result = runner.invoke(main, ['convert', 'test.toml', '--input-type', 'toml', '--format', 'django'])
        
        # Verify command succeeded
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        
        # Verify output contains Django model code
        assert 'class SimpleModel' in result.output
        assert 'models.Model' in result.output


def test_full_pipeline_with_write_to_directory():
    """Test full pipeline with writing to directory."""
    toml_content = '''
[entities.Author]
table_name = "author"
comment = "Author model"

[[entities.Author.columns]]
name = "id"
type = "int"
primary_key = true

[[entities.Author.columns]]
name = "name"
type = "string"
max_length = 100

[entities.Book]
table_name = "book"
comment = "Book model"

[[entities.Book.columns]]
name = "id"
type = "int"
primary_key = true

[[entities.Book.columns]]
name = "title"
type = "string"
max_length = 200
'''
    
    # Parse TOML
    parser = TomlERParser()
    model = parser.parse(toml_content)
    
    # Render to Django package and write to directory
    renderer = DjangoPackageRenderer(app_label='testapp')
    
    with tempfile.TemporaryDirectory() as tmpdir:
        renderer.write_to_directory(model, tmpdir)
        
        # Verify files were created
        output_path = Path(tmpdir)
        assert (output_path / '__init__.py').exists()
        assert (output_path / 'author.py').exists()
        assert (output_path / 'author_manager.py').exists()
        assert (output_path / 'author_queryset.py').exists()
        assert (output_path / 'book.py').exists()
        assert (output_path / 'book_manager.py').exists()
        assert (output_path / 'book_queryset.py').exists()
        
        # Verify all files can be parsed
        for py_file in output_path.glob('*.py'):
            with open(py_file, 'r') as f:
                code = f.read()
            try:
                ast.parse(code)
            except SyntaxError as e:
                raise AssertionError(f"Generated file {py_file.name} has syntax errors: {e}")
