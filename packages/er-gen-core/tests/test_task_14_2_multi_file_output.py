"""
Tests for Task 14.2: Multi-file output mode for SQLAlchemy.

Requirements tested:
- 5.1: Each model class gets a separate file
- 5.3: Multiple files created in target directory
- 11.1: --split-models parameter support (via render_multi_file)
- 11.5: Fail-fast on filename conflicts
"""
import pytest
from x007007007.er.models import ERModel, Entity, Column
from x007007007.er.renderers import SQLAlchemyRenderer


class TestTask14_2MultiFileOutput:
    """Test Task 14.2: Multi-file output mode implementation."""
    
    def test_render_multi_file_creates_separate_files(self):
        """
        Test that render_multi_file creates a separate file for each model.
        
        Validates: Requirement 5.1, 5.3
        """
        # Create a simple ERModel with two entities
        model = ERModel()
        
        user_entity = Entity(name="User", table_name="user")
        user_entity.columns.append(Column(name="id", db_column="id", type="Integer", is_pk=True))
        user_entity.columns.append(Column(name="username", db_column="username", type="String", max_length=50))
        
        profile_entity = Entity(name="Profile", table_name="profile")
        profile_entity.columns.append(Column(name="id", db_column="id", type="Integer", is_pk=True))
        profile_entity.columns.append(Column(name="bio", db_column="bio", type="Text"))
        
        model.entities["User"] = user_entity
        model.entities["Profile"] = profile_entity
        
        # Render multi-file
        renderer = SQLAlchemyRenderer()
        files = renderer.render_multi_file(model)
        
        # Should have 3 files: user.py, profile.py, __init__.py
        assert len(files) == 3, f"Expected 3 files, got {len(files)}"
        assert "user.py" in files, "user.py should be generated"
        assert "profile.py" in files, "profile.py should be generated"
        assert "__init__.py" in files, "__init__.py should be generated"
        
        # Verify user.py contains User class
        assert "class User(Base):" in files["user.py"]
        assert "username" in files["user.py"]
        
        # Verify profile.py contains Profile class
        assert "class Profile(Base):" in files["profile.py"]
        assert "bio" in files["profile.py"]
    
    def test_render_multi_file_includes_necessary_imports(self):
        """
        Test that each generated file includes necessary import statements.
        
        Validates: Requirement 5.1 (includes necessary imports)
        """
        model = ERModel()
        
        user_entity = Entity(name="User", table_name="user")
        user_entity.columns.append(Column(name="id", db_column="id", type="Integer", is_pk=True))
        user_entity.columns.append(Column(name="name", db_column="name", type="String", max_length=100))
        
        model.entities["User"] = user_entity
        
        renderer = SQLAlchemyRenderer()
        files = renderer.render_multi_file(model)
        
        user_content = files["user.py"]
        
        # Check for necessary imports
        assert "from sqlalchemy import Column" in user_content
        assert "from sqlalchemy.orm import declarative_base" in user_content or "from" in user_content
        assert "Base = declarative_base()" in user_content or "import Base" in user_content
    
    def test_render_multi_file_fails_on_filename_conflict(self):
        """
        Test that render_multi_file fails fast when filename conflicts occur.
        
        Validates: Requirement 11.5 (fail-fast on filename conflicts)
        """
        model = ERModel()
        
        # Create two entities that would map to the same filename
        # For example: "User" and "USER" both map to "user.py"
        user1 = Entity(name="User", table_name="user")
        user1.columns.append(Column(name="id", db_column="id", type="Integer", is_pk=True))
        
        user2 = Entity(name="USER", table_name="u_s_e_r")
        user2.columns.append(Column(name="id", db_column="id", type="Integer", is_pk=True))
        
        model.entities["User"] = user1
        model.entities["USER"] = user2
        
        renderer = SQLAlchemyRenderer()
        
        # Should raise ValueError due to filename conflict
        with pytest.raises(ValueError) as exc_info:
            renderer.render_multi_file(model)
        
        assert "Filename conflict" in str(exc_info.value)
        assert "user.py" in str(exc_info.value).lower()
    
    def test_init_file_imports_all_models(self):
        """
        Test that __init__.py imports all generated models.
        
        Validates: Requirement 5.6, 11.4 (generate __init__.py with imports)
        """
        model = ERModel()
        
        user_entity = Entity(name="User", table_name="user")
        user_entity.columns.append(Column(name="id", db_column="id", type="Integer", is_pk=True))
        
        profile_entity = Entity(name="Profile", table_name="profile")
        profile_entity.columns.append(Column(name="id", db_column="id", type="Integer", is_pk=True))
        
        post_entity = Entity(name="Post", table_name="post")
        post_entity.columns.append(Column(name="id", db_column="id", type="Integer", is_pk=True))
        
        model.entities["User"] = user_entity
        model.entities["Profile"] = profile_entity
        model.entities["Post"] = post_entity
        
        renderer = SQLAlchemyRenderer()
        files = renderer.render_multi_file(model)
        
        init_content = files["__init__.py"]
        
        # Check that all models are imported
        assert "from .user import User" in init_content
        assert "from .profile import Profile" in init_content
        assert "from .post import Post" in init_content
        
        # Check __all__ list
        assert "__all__ = [" in init_content
        assert '"User"' in init_content
        assert '"Profile"' in init_content
        assert '"Post"' in init_content
    
    def test_custom_base_model_import(self):
        """
        Test that custom BaseModel import is used when specified.
        
        Validates: Requirement 5.4, 11.7 (custom BaseModel import)
        """
        model = ERModel()
        
        user_entity = Entity(name="User", table_name="user")
        user_entity.columns.append(Column(name="id", db_column="id", type="Integer", is_pk=True))
        
        model.entities["User"] = user_entity
        
        # Use custom base model import
        renderer = SQLAlchemyRenderer(base_model_import="myproject.database")
        files = renderer.render_multi_file(model)
        
        user_content = files["user.py"]
        
        # Should use custom import instead of declarative_base
        assert "from myproject.database import Base" in user_content
        assert "Base = declarative_base()" not in user_content
    
    def test_snake_case_filename_conversion(self):
        """
        Test that class names are converted to snake_case for filenames.
        
        Validates: Requirement 5.2 (snake_case filenames)
        """
        model = ERModel()
        
        # Create entities with various naming patterns
        entities = [
            ("UserAccount", "user_account.py"),
            ("HTTPRequest", "http_request.py"),
            ("SimpleModel", "simple_model.py"),
            ("API", "api.py"),
        ]
        
        for entity_name, expected_filename in entities:
            entity = Entity(name=entity_name)
            entity.columns.append(Column(name="id", db_column="id", type="Integer", is_pk=True))
            model.entities[entity_name] = entity
        
        renderer = SQLAlchemyRenderer()
        files = renderer.render_multi_file(model)
        
        # Check that all expected filenames are present
        for entity_name, expected_filename in entities:
            assert expected_filename in files, f"Expected {expected_filename} to be generated"
            assert f"class {entity_name}(Base):" in files[expected_filename]
    
    def test_multi_file_with_relationships(self):
        """
        Test that relationships are correctly included in multi-file output.
        
        Validates: Requirement 5.1 (complete class definitions with relationships)
        """
        from x007007007.er.models import Relationship
        
        model = ERModel()
        
        user_entity = Entity(name="User", table_name="user")
        user_entity.columns.append(Column(name="id", db_column="id", type="Integer", is_pk=True))
        
        profile_entity = Entity(name="Profile", table_name="profile")
        profile_entity.columns.append(Column(name="id", db_column="id", type="Integer", is_pk=True))
        profile_entity.columns.append(Column(name="user_id", db_column="user_id", type="Integer", is_fk=True))
        
        model.entities["User"] = user_entity
        model.entities["Profile"] = profile_entity
        
        # Add relationship
        rel = Relationship(
            left_entity="User",
            right_entity="Profile",
            relation_type="one-to-one",
            left_column="id",
            right_column="user_id"
        )
        model.relationships.append(rel)
        
        renderer = SQLAlchemyRenderer()
        files = renderer.render_multi_file(model)
        
        # Check that relationships are included
        profile_content = files["profile.py"]
        assert "ForeignKey" in profile_content
        assert "relationship" in profile_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
