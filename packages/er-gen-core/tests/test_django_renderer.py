"""
Unit tests for DjangoRenderer and DjangoPackageRenderer.
"""
import pytest
import ast
from x007007007.er.renderers.python.django import DjangoRenderer, DjangoPackageRenderer, to_snake_case
from x007007007.er.models import ERModel, Entity, Column, Relationship


class TestToSnakeCase:
    """Tests for to_snake_case helper function."""
    
    def test_simple_camel_case(self):
        """Test simple CamelCase conversion."""
        assert to_snake_case("User") == "user"
        assert to_snake_case("Post") == "post"
    
    def test_multi_word_camel_case(self):
        """Test multi-word CamelCase conversion."""
        assert to_snake_case("UserProfile") == "user_profile"
        assert to_snake_case("BlogPost") == "blog_post"
    
    def test_complex_camel_case(self):
        """Test complex CamelCase conversion."""
        assert to_snake_case("ConversationSessionModel") == "conversation_session_model"
        assert to_snake_case("FileTypeModel") == "file_type_model"
    
    def test_acronyms(self):
        """Test handling of acronyms."""
        assert to_snake_case("HTTPResponse") == "http_response"
        assert to_snake_case("XMLParser") == "xml_parser"
    
    def test_already_snake_case(self):
        """Test strings already in snake_case."""
        assert to_snake_case("user_profile") == "user_profile"
        assert to_snake_case("blog_post") == "blog_post"
    
    def test_single_letter(self):
        """Test single letter names."""
        assert to_snake_case("A") == "a"
        assert to_snake_case("X") == "x"
    
    def test_with_numbers(self):
        """Test names with numbers."""
        assert to_snake_case("User2") == "user2"
        assert to_snake_case("Model3D") == "model3_d"


class TestDjangoRenderer:
    """Tests for DjangoRenderer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.renderer = DjangoRenderer(app_label='testapp', table_prefix='test')
    
    def test_initialization(self):
        """Test DjangoRenderer initialization."""
        renderer = DjangoRenderer(app_label='myapp', table_prefix='prefix')
        assert renderer.app_label == 'myapp'
        assert renderer.table_prefix == 'prefix'
    
    def test_default_initialization(self):
        """Test DjangoRenderer with default parameters."""
        renderer = DjangoRenderer()
        assert renderer.app_label == 'app'
        assert renderer.table_prefix == ''
    
    def test_has_jinja_environment(self):
        """Test that renderer has Jinja2 environment."""
        assert hasattr(self.renderer, 'env')
        assert self.renderer.env is not None
    
    def test_has_code_value_filter(self):
        """Test that code_value filter is registered."""
        assert 'code_value' in self.renderer.env.filters
        assert callable(self.renderer.env.filters['code_value'])
    
    def test_has_django_field_type_filter(self):
        """Test that django_field_type filter is registered."""
        assert 'django_field_type' in self.renderer.env.filters
        assert callable(self.renderer.env.filters['django_field_type'])
    
    def test_has_template(self):
        """Test that renderer has template loaded."""
        assert hasattr(self.renderer, 'template')
        assert self.renderer.template is not None
    
    def test_render_empty_model(self):
        """Test rendering an empty ERModel."""
        model = ERModel(entities={}, relationships=[], templates={})
        result = self.renderer.render(model)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_render_simple_entity(self):
        """Test rendering a simple entity."""
        entity = Entity(
            name="User",
            columns=[
                Column(name="id", type="int", is_pk=True, nullable=False),
                Column(name="name", type="varchar", max_length=100, nullable=False)
            ],
            comment="User model"
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        # Verify generated code contains expected elements
        assert "class User" in result
        assert "models.Model" in result
        assert "id = models" in result
        assert "name = models" in result
    
    def test_render_entity_with_default_values(self):
        """Test rendering entity with default values."""
        entity = Entity(
            name="Post",
            columns=[
                Column(name="id", type="int", is_pk=True, nullable=False),
                Column(name="title", type="varchar", max_length=200, nullable=False, default="Untitled"),
                Column(name="published", type="boolean", nullable=False, default=False)
            ]
        )
        model = ERModel(entities={"Post": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        # Verify default values are serialized
        assert "default=" in result
        assert '"Untitled"' in result or "'Untitled'" in result
        assert "False" in result
    
    def test_render_entity_with_comments(self):
        """Test rendering entity with help_text."""
        entity = Entity(
            name="Article",
            columns=[
                Column(name="id", type="int", is_pk=True, nullable=False),
                Column(name="content", type="text", nullable=False, comment="Article content")
            ]
        )
        model = ERModel(entities={"Article": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        # Verify help_text is serialized
        assert "help_text=" in result
        assert "Article content" in result
    
    def test_render_entity_with_quotes_in_comment(self):
        """Test rendering entity with quotes in help_text."""
        entity = Entity(
            name="Product",
            columns=[
                Column(name="id", type="int", is_pk=True, nullable=False),
                Column(name="name", type="varchar", max_length=100, nullable=False, comment='Product "name"')
            ]
        )
        model = ERModel(entities={"Product": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        # Verify generated code is valid Python
        # Should not have syntax errors from unescaped quotes
        assert "help_text=" in result
        # The serializer should handle quotes properly
        assert 'Product "name"' in result or 'Product \\"name\\"' in result
    
    def test_render_multiple_entities(self):
        """Test rendering multiple entities."""
        user = Entity(
            name="User",
            columns=[Column(name="id", type="int", is_pk=True, nullable=False)]
        )
        post = Entity(
            name="Post",
            columns=[Column(name="id", type="int", is_pk=True, nullable=False)]
        )
        model = ERModel(
            entities={"User": user, "Post": post},
            relationships=[],
            templates={}
        )
        result = self.renderer.render(model)
        
        assert "class User" in result
        assert "class Post" in result
    
    def test_render_with_table_prefix(self):
        """Test rendering with table prefix."""
        renderer = DjangoRenderer(table_prefix='myapp')
        entity = Entity(
            name="User",
            columns=[Column(name="id", type="int", is_pk=True, nullable=False)]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        result = renderer.render(model)
        
        assert "db_table" in result
        assert "myapp" in result
    
    def test_render_with_app_label(self):
        """Test rendering with custom app label."""
        renderer = DjangoRenderer(app_label='customapp')
        entity = Entity(
            name="User",
            columns=[Column(name="id", type="int", is_pk=True, nullable=False)]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        result = renderer.render(model)
        
        assert "app_label" in result
        assert "customapp" in result
    
    def test_render_validates_model_type(self):
        """Test that render validates model type."""
        with pytest.raises(AssertionError, match="Model must be an ERModel instance"):
            self.renderer.render("not a model")
    
    def test_generated_code_is_valid_python(self):
        """Test that generated code is syntactically valid."""
        entity = Entity(
            name="User",
            columns=[
                Column(name="id", type="int", is_pk=True, nullable=False),
                Column(name="name", type="varchar", max_length=100, nullable=False),
                Column(name="email", type="varchar", max_length=255, nullable=False)
            ]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        # Should be able to parse without syntax errors
        try:
            ast.parse(result)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{result}")


class TestDjangoPackageRenderer:
    """Tests for DjangoPackageRenderer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.renderer = DjangoPackageRenderer(app_label='testapp', table_prefix='test')
    
    def test_initialization(self):
        """Test DjangoPackageRenderer initialization."""
        renderer = DjangoPackageRenderer(app_label='myapp', table_prefix='prefix')
        assert renderer.app_label == 'myapp'
        assert renderer.table_prefix == 'prefix'
    
    def test_default_initialization(self):
        """Test DjangoPackageRenderer with default parameters."""
        renderer = DjangoPackageRenderer()
        assert renderer.app_label == 'app'
        assert renderer.table_prefix == ''
    
    def test_has_jinja_environment(self):
        """Test that renderer has Jinja2 environment."""
        assert hasattr(self.renderer, 'env')
        assert self.renderer.env is not None
    
    def test_has_all_templates(self):
        """Test that renderer has all required templates."""
        assert hasattr(self.renderer, 'model_template')
        assert hasattr(self.renderer, 'manager_template')
        assert hasattr(self.renderer, 'queryset_template')
        assert hasattr(self.renderer, 'init_template')
    
    def test_has_code_value_filter(self):
        """Test that code_value filter is registered."""
        assert 'code_value' in self.renderer.env.filters
        assert callable(self.renderer.env.filters['code_value'])
    
    def test_render_returns_dict(self):
        """Test that render returns a dictionary."""
        model = ERModel(entities={}, relationships=[], templates={})
        result = self.renderer.render(model)
        assert isinstance(result, dict)
    
    def test_render_empty_model_generates_init(self):
        """Test rendering empty model generates __init__.py."""
        model = ERModel(entities={}, relationships=[], templates={})
        result = self.renderer.render(model)
        assert '__init__.py' in result
    
    def test_render_single_entity_generates_four_files(self):
        """Test rendering single entity generates 4 files (3 + __init__)."""
        entity = Entity(
            name="User",
            columns=[Column(name="id", type="int", is_pk=True, nullable=False)]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        # Should have 4 files: __init__.py + 3 files for User
        assert len(result) == 4
        assert '__init__.py' in result
        assert 'user_queryset.py' in result
        assert 'user_manager.py' in result
        assert 'user.py' in result
    
    def test_render_multiple_entities_generates_correct_count(self):
        """Test rendering N entities generates 3N + 1 files."""
        user = Entity(
            name="User",
            columns=[Column(name="id", type="int", is_pk=True, nullable=False)]
        )
        post = Entity(
            name="Post",
            columns=[Column(name="id", type="int", is_pk=True, nullable=False)]
        )
        model = ERModel(
            entities={"User": user, "Post": post},
            relationships=[],
            templates={}
        )
        result = self.renderer.render(model)
        
        # Should have 7 files: __init__.py + 3 files per entity (2 entities)
        assert len(result) == 7
        assert '__init__.py' in result
        # User files
        assert 'user_queryset.py' in result
        assert 'user_manager.py' in result
        assert 'user.py' in result
        # Post files
        assert 'post_queryset.py' in result
        assert 'post_manager.py' in result
        assert 'post.py' in result
    
    def test_file_naming_convention(self):
        """Test that file names follow snake_case convention."""
        entity = Entity(
            name="UserProfile",
            columns=[Column(name="id", type="int", is_pk=True, nullable=False)]
        )
        model = ERModel(entities={"UserProfile": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        assert 'user_profile_queryset.py' in result
        assert 'user_profile_manager.py' in result
        assert 'user_profile.py' in result
    
    def test_queryset_file_content(self):
        """Test QuerySet file contains QuerySet class."""
        entity = Entity(
            name="User",
            columns=[Column(name="id", type="int", is_pk=True, nullable=False)]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        queryset_content = result['user_queryset.py']
        assert "class UserQuerySet" in queryset_content
        assert "models.QuerySet" in queryset_content
    
    def test_manager_file_content(self):
        """Test Manager file contains Manager class."""
        entity = Entity(
            name="User",
            columns=[Column(name="id", type="int", is_pk=True, nullable=False)]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        manager_content = result['user_manager.py']
        assert "class UserManager" in manager_content
        assert "models.Manager" in manager_content
    
    def test_model_file_content(self):
        """Test Model file contains Model class."""
        entity = Entity(
            name="User",
            columns=[Column(name="id", type="int", is_pk=True, nullable=False)]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        model_content = result['user.py']
        assert "class User" in model_content
        assert "models.Model" in model_content
    
    def test_manager_imports_queryset(self):
        """Test that Manager file imports QuerySet."""
        entity = Entity(
            name="User",
            columns=[Column(name="id", type="int", is_pk=True, nullable=False)]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        manager_content = result['user_manager.py']
        assert "from .user_queryset import UserQuerySet" in manager_content
    
    def test_model_imports_manager(self):
        """Test that Model file imports Manager."""
        entity = Entity(
            name="User",
            columns=[Column(name="id", type="int", is_pk=True, nullable=False)]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        model_content = result['user.py']
        assert "from .user_manager import UserManager" in model_content
    
    def test_init_imports_models(self):
        """Test that __init__.py imports Model classes."""
        entity = Entity(
            name="User",
            columns=[Column(name="id", type="int", is_pk=True, nullable=False)]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        init_content = result['__init__.py']
        assert "from .user import User" in init_content
    
    def test_init_has_all_export(self):
        """Test that __init__.py has __all__ list."""
        entity = Entity(
            name="User",
            columns=[Column(name="id", type="int", is_pk=True, nullable=False)]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        init_content = result['__init__.py']
        assert "__all__" in init_content
        assert "'User'" in init_content
    
    def test_all_generated_files_are_valid_python(self):
        """Test that all generated files are syntactically valid."""
        entity = Entity(
            name="User",
            columns=[
                Column(name="id", type="int", is_pk=True, nullable=False),
                Column(name="name", type="varchar", max_length=100, nullable=False)
            ]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        for filename, content in result.items():
            try:
                ast.parse(content)
            except SyntaxError as e:
                pytest.fail(f"File {filename} has syntax error: {e}\n{content}")
    
    def test_render_validates_model_type(self):
        """Test that render validates model type."""
        with pytest.raises(AssertionError, match="Model must be an ERModel instance"):
            self.renderer.render("not a model")
    
    def test_write_to_directory_validates_model_type(self):
        """Test that write_to_directory validates model type."""
        with pytest.raises(AssertionError, match="Model must be an ERModel instance"):
            self.renderer.write_to_directory("not a model", "/tmp/test")
    
    def test_write_to_directory_validates_output_dir_type(self):
        """Test that write_to_directory validates output_dir type."""
        model = ERModel(entities={}, relationships=[], templates={})
        with pytest.raises(AssertionError, match="output_dir must be a string"):
            self.renderer.write_to_directory(model, 123)
