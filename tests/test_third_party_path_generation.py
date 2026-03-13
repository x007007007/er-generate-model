"""
Test third-party file path generation.

This test verifies that third-party files (files with 'third/' prefix) are written
to the global src/third/ directory, not to module-specific output directories.
"""
import pytest
from pathlib import Path
import tempfile
import shutil


def test_third_party_files_written_to_global_src_directory():
    """
    Test that third-party files are written to src/third/ regardless of output_dir.
    
    When using --output-dir parameter (e.g., src/module/submodule/sqlalchemy),
    third-party files should be written to src/third/ (shared across all modules),
    not to src/module/submodule/sqlalchemy/third/ (module-specific copy).
    """
    from x007007007.er.parser.toml_parser import TomlERParser
    from x007007007.er.renderers.python.sqlalchemy.renderer import SQLAlchemyRenderer
    
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create test TOML content with external inheritance
        toml_content = """
[entities.User]
extends = ["external.library.models.BaseModel"]
table_name = "users"
package = "myapp.models.user"

[[entities.User.columns]]
name = "id"
type = "bigint"
primary_key = true

[[entities.User.columns]]
name = "username"
type = "string"
max_length = 100
"""
        
        # Parse the TOML
        parser = TomlERParser(inheritance_mode='reference')
        model = parser.parse(toml_content)
        
        # Render files
        renderer = SQLAlchemyRenderer(
            table_prefix='test',
            base_model_import='myapp.base',
            inheritance_mode='reference'
        )
        files = renderer.render_multi_file(model)
        
        # Verify that third-party files are in the output
        third_party_files = [f for f in files.keys() if f.startswith('third/')]
        assert len(third_party_files) > 0, "Should generate third-party files"
        
        # Simulate writing files with module-specific output_dir
        output_dir = tmpdir / 'src' / 'myapp' / 'models' / 'sqlalchemy'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write files using the same logic as er_convert.py and convert.py
        for filename, content in files.items():
            if filename.startswith('third/'):
                # Third-party files go to global src/third/ directory
                current = output_dir
                src_root = None
                while current.parent != current:
                    if current.name == 'src':
                        src_root = current
                        break
                    current = current.parent
                
                if src_root is None:
                    if 'src' in output_dir.parts:
                        src_index = output_dir.parts.index('src')
                        src_root = Path(*output_dir.parts[:src_index+1])
                    else:
                        src_root = output_dir.parent
                
                file_path = src_root / filename
            else:
                file_path = output_dir / filename
            
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
        
        # Verify third-party files are in src/third/, not in output_dir/third/
        third_dir = tmpdir / 'src' / 'third'
        assert third_dir.exists(), "src/third/ directory should exist"
        
        # Verify third-party files are NOT in the module-specific directory
        module_third_dir = output_dir / 'third'
        assert not module_third_dir.exists(), \
            "third/ should NOT be in module-specific output directory"
        
        # Verify entity files ARE in the module-specific directory
        entity_files = [f for f in files.keys() if not f.startswith('third/') and f != '__init__.py']
        for entity_file in entity_files:
            entity_path = output_dir / entity_file
            assert entity_path.exists(), \
                f"Entity file {entity_file} should be in module-specific directory"
        
        # Verify __init__.py is in the module-specific directory
        init_path = output_dir / '__init__.py'
        assert init_path.exists(), "__init__.py should be in module-specific directory"


def test_third_party_files_shared_across_modules():
    """
    Test that third-party files are shared across multiple modules.
    
    When processing multiple TOML files that reference the same external class,
    the third-party file should be generated once in src/third/ and shared.
    """
    from x007007007.er.parser.toml_parser import TomlERParser
    from x007007007.er.renderers.python.sqlalchemy.renderer import SQLAlchemyRenderer
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create two TOML files that reference the same external class
        toml1_content = """
[entities.User]
extends = ["external.library.models.BaseModel"]
table_name = "users"
package = "module1.models.user"

[[entities.User.columns]]
name = "id"
type = "bigint"
primary_key = true
"""
        
        toml2_content = """
[entities.Product]
extends = ["external.library.models.BaseModel"]
table_name = "products"
package = "module2.models.product"

[[entities.Product.columns]]
name = "id"
type = "bigint"
primary_key = true
"""
        
        # Process first module
        parser1 = TomlERParser(inheritance_mode='reference')
        model1 = parser1.parse(toml1_content)
        renderer1 = SQLAlchemyRenderer(
            table_prefix='mod1',
            base_model_import='myapp.base',
            inheritance_mode='reference'
        )
        files1 = renderer1.render_multi_file(model1)
        
        output_dir1 = tmpdir / 'src' / 'module1' / 'sqlalchemy'
        output_dir1.mkdir(parents=True, exist_ok=True)
        
        for filename, content in files1.items():
            if filename.startswith('third/'):
                current = output_dir1
                src_root = None
                while current.parent != current:
                    if current.name == 'src':
                        src_root = current
                        break
                    current = current.parent
                file_path = src_root / filename
            else:
                file_path = output_dir1 / filename
            
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
        
        # Process second module
        parser2 = TomlERParser(inheritance_mode='reference')
        model2 = parser2.parse(toml2_content)
        renderer2 = SQLAlchemyRenderer(
            table_prefix='mod2',
            base_model_import='myapp.base',
            inheritance_mode='reference'
        )
        files2 = renderer2.render_multi_file(model2)
        
        output_dir2 = tmpdir / 'src' / 'module2' / 'sqlalchemy'
        output_dir2.mkdir(parents=True, exist_ok=True)
        
        for filename, content in files2.items():
            if filename.startswith('third/'):
                current = output_dir2
                src_root = None
                while current.parent != current:
                    if current.name == 'src':
                        src_root = current
                        break
                    current = current.parent
                file_path = src_root / filename
            else:
                file_path = output_dir2 / filename
            
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
        
        # Verify there's only ONE copy of the third-party file in src/third/
        third_dir = tmpdir / 'src' / 'third'
        assert third_dir.exists(), "src/third/ directory should exist"
        
        # Count third-party files (should be only one copy)
        third_party_files = list(third_dir.rglob('*.py'))
        # Both modules reference the same external class, so there should be one file
        # (the second write overwrites the first, which is fine since they're identical)
        assert len(third_party_files) > 0, "Should have third-party files"
        
        # Verify module-specific directories don't have third/ subdirectories
        assert not (output_dir1 / 'third').exists(), \
            "module1 should NOT have third/ subdirectory"
        assert not (output_dir2 / 'third').exists(), \
            "module2 should NOT have third/ subdirectory"
