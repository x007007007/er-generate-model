"""
Integration tests for Task 14.2: er_convert command with multi-file SQLAlchemy output.

Requirements tested:
- 5.1: Each model class gets a separate file
- 5.3: Multiple files created in target directory
- 11.1: Multi-file output mode
- 11.5: Fail-fast on filename conflicts
"""
import pytest
from pathlib import Path
import tempfile
import toml

# Skip all tests if Django is not available
pytest.importorskip("django")

import django
from django.conf import settings

# Configure Django settings for testing
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'x007007007.er_django',
        ],
        SECRET_KEY='test-secret-key',
    )
    django.setup()

from django.core.management.base import CommandError
from django.test import TestCase
from x007007007.er_django.management.commands.er_convert import Command
from io import StringIO


class TestTask14_2ErConvertMultiFile(TestCase):
    """Test Task 14.2: er_convert command multi-file SQLAlchemy output."""
    
    def test_generate_sqlalchemy_code_creates_multiple_files(self):
        """
        Test that _generate_sqlalchemy_code creates multiple files.
        
        Validates: Requirement 5.1, 5.3, 11.1
        """
        from x007007007.er.models import ERModel, Entity, Column
        from x007007007.er.parser.toml_parser import TomlERParser
        
        # Create a TOML string with multiple entities
        toml_content = """
[entities.User]
[[entities.User.columns]]
name = "id"
type = "Integer"
primary_key = true

[[entities.User.columns]]
name = "username"
type = "String"
max_length = 50

[entities.Profile]
[[entities.Profile.columns]]
name = "id"
type = "Integer"
primary_key = true

[[entities.Profile.columns]]
name = "bio"
type = "Text"
"""
        
        # Parse TOML to ERModel
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            
            # Call _generate_sqlalchemy_code
            cmd = Command()
            cmd.stdout = StringIO()
            
            file_count = cmd._generate_sqlalchemy_code(
                er_model=er_model,
                output_dir=output_dir,
                base_model_import=None
            )
            
            # Should generate 3 files: user.py, profile.py, __init__.py
            assert file_count == 3, f"Expected 3 files, got {file_count}"
            
            # Check files exist
            user_file = output_dir / 'user.py'
            profile_file = output_dir / 'profile.py'
            init_file = output_dir / '__init__.py'
            
            assert user_file.exists(), "user.py should be generated"
            assert profile_file.exists(), "profile.py should be generated"
            assert init_file.exists(), "__init__.py should be generated"
            
            # Verify content
            user_content = user_file.read_text()
            assert "class User(Base):" in user_content
            assert "username" in user_content
            
            profile_content = profile_file.read_text()
            assert "class Profile(Base):" in profile_content
            assert "bio" in profile_content
            
            # Verify __init__.py
            init_content = init_file.read_text()
            assert "from .user import User" in init_content
            assert "from .profile import Profile" in init_content
    
    def test_generate_sqlalchemy_code_with_custom_base_model(self):
        """
        Test that custom BaseModel import is used.
        
        Validates: Requirement 5.4, 11.7
        """
        from x007007007.er.models import ERModel, Entity, Column
        from x007007007.er.parser.toml_parser import TomlERParser
        
        toml_content = """
[entities.User]
[[entities.User.columns]]
name = "id"
type = "Integer"
primary_key = true
"""
        
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            
            cmd = Command()
            cmd.stdout = StringIO()
            
            file_count = cmd._generate_sqlalchemy_code(
                er_model=er_model,
                output_dir=output_dir,
                base_model_import='myproject.database'
            )
            
            assert file_count == 2  # user.py and __init__.py
            
            user_file = output_dir / 'user.py'
            user_content = user_file.read_text()
            
            # Should use custom import
            assert "from myproject.database import Base" in user_content
            assert "Base = declarative_base()" not in user_content
    
    def test_generate_sqlalchemy_code_fails_on_filename_conflict(self):
        """
        Test that generation fails fast on filename conflicts.
        
        Validates: Requirement 11.5
        """
        from x007007007.er.models import ERModel, Entity, Column
        
        # Create ERModel with conflicting entity names
        er_model = ERModel()
        
        user1 = Entity(name="User")
        user1.columns.append(Column(name="id", type="Integer", is_pk=True))
        
        user2 = Entity(name="USER")
        user2.columns.append(Column(name="id", type="Integer", is_pk=True))
        
        er_model.entities["User"] = user1
        er_model.entities["USER"] = user2
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            
            cmd = Command()
            cmd.stdout = StringIO()
            
            # Should raise CommandError due to filename conflict
            with pytest.raises(CommandError) as exc_info:
                cmd._generate_sqlalchemy_code(
                    er_model=er_model,
                    output_dir=output_dir,
                    base_model_import=None
                )
            
            assert "Filename conflict" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

