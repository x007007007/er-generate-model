"""
Test for Task 5.5: Migration commands integration

This test verifies that:
1. The migration code has been moved to er-gen-tool
2. The makemigration command works
3. The migrate showmigrations command works
"""
import subprocess
import tempfile
import shutil
import sys
from pathlib import Path

# Get the er-gen-tool command path
ER_GEN_TOOL = str(Path(__file__).parent.parent.parent / '.venv' / 'bin' / 'er-gen-tool')


def test_migration_commands_available():
    """Test that migration commands are available in er-gen-tool"""
    # Test main help
    result = subprocess.run(
        [ER_GEN_TOOL, '--help'],
        capture_output=True,
        text=True
    )
    print("Return code:", result.returncode)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    assert result.returncode == 0
    assert 'makemigration' in result.stdout
    assert 'migrate' in result.stdout
    
    # Test makemigration help
    result = subprocess.run(
        [ER_GEN_TOOL, 'makemigration', '--help'],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert 'Generate migration from ER diagram' in result.stdout
    assert '--namespace' in result.stdout
    assert '--er-file' in result.stdout
    
    # Test migrate help
    result = subprocess.run(
        [ER_GEN_TOOL, 'migrate', '--help'],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert 'Database migration management' in result.stdout
    
    # Test migrate showmigrations help
    result = subprocess.run(
        [ER_GEN_TOOL, 'migrate', 'showmigrations', '--help'],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert 'Show migration status' in result.stdout


def test_makemigration_command():
    """Test that makemigration command works end-to-end"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create a simple ER diagram
        er_file = tmpdir / 'schema.mmd'
        er_file.write_text('''erDiagram
    User {
        uuid id PK
        string username UK
        string email UK
    }
''')
        
        # Run makemigration
        result = subprocess.run(
            [
                ER_GEN_TOOL, 'makemigration',
                '-n', 'test',
                '-e', str(er_file),
                '-d', str(tmpdir / '.migrations')
            ],
            capture_output=True,
            text=True,
            cwd=tmpdir
        )
        
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        
        assert result.returncode == 0
        assert 'Parsing ER diagram' in result.stdout
        assert 'Generating migration' in result.stdout
        assert 'Migration saved to' in result.stdout
        
        # Check that migration file was created
        migrations_dir = tmpdir / '.migrations' / 'test'
        assert migrations_dir.exists()
        migration_files = list(migrations_dir.glob('*.yaml'))
        assert len(migration_files) == 1
        assert migration_files[0].name.startswith('0001_')


def test_showmigrations_command():
    """Test that showmigrations command works"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create a simple ER diagram
        er_file = tmpdir / 'schema.mmd'
        er_file.write_text('''erDiagram
    User {
        uuid id PK
        string username
    }
''')
        
        # First create a migration
        subprocess.run(
            [
                ER_GEN_TOOL, 'makemigration',
                '-n', 'test',
                '-e', str(er_file),
                '-d', str(tmpdir / '.migrations')
            ],
            capture_output=True,
            text=True,
            cwd=tmpdir
        )
        
        # Now show migrations
        result = subprocess.run(
            [
                ER_GEN_TOOL, 'migrate', 'showmigrations',
                '-n', 'test',
                '-d', str(tmpdir / '.migrations')
            ],
            capture_output=True,
            text=True,
            cwd=tmpdir
        )
        
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        
        assert result.returncode == 0
        assert 'test:' in result.stdout
        assert '0001_' in result.stdout


def test_showmigrations_all_namespaces():
    """Test showmigrations without namespace shows all"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create ER diagrams for two namespaces
        er_file1 = tmpdir / 'schema1.mmd'
        er_file1.write_text('''erDiagram
    User {
        uuid id PK
    }
''')
        
        er_file2 = tmpdir / 'schema2.mmd'
        er_file2.write_text('''erDiagram
    Post {
        uuid id PK
    }
''')
        
        # Create migrations for both namespaces
        subprocess.run(
            [
                ER_GEN_TOOL, 'makemigration',
                '-n', 'auth',
                '-e', str(er_file1),
                '-d', str(tmpdir / '.migrations')
            ],
            capture_output=True,
            cwd=tmpdir
        )
        
        subprocess.run(
            [
                ER_GEN_TOOL, 'makemigration',
                '-n', 'blog',
                '-e', str(er_file2),
                '-d', str(tmpdir / '.migrations')
            ],
            capture_output=True,
            cwd=tmpdir
        )
        
        # Show all migrations
        result = subprocess.run(
            [
                ER_GEN_TOOL, 'migrate', 'showmigrations',
                '-d', str(tmpdir / '.migrations')
            ],
            capture_output=True,
            text=True,
            cwd=tmpdir
        )
        
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        
        assert result.returncode == 0
        assert 'auth:' in result.stdout
        assert 'blog:' in result.stdout


if __name__ == '__main__':
    print("Testing migration commands availability...")
    test_migration_commands_available()
    print("✓ Migration commands are available\n")
    
    print("Testing makemigration command...")
    test_makemigration_command()
    print("✓ makemigration command works\n")
    
    print("Testing showmigrations command...")
    test_showmigrations_command()
    print("✓ showmigrations command works\n")
    
    print("Testing showmigrations all namespaces...")
    test_showmigrations_all_namespaces()
    print("✓ showmigrations all namespaces works\n")
    
    print("All tests passed! ✓")
