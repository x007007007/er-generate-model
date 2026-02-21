"""
Unit tests for SQLAlchemyRenderer.
"""
import pytest
import ast
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer
from x007007007.er.models import ERModel, Entity, Column


class TestSQLAlchemyRenderer:
    """Tests for SQLAlchemyRenderer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.renderer = SQLAlchemyRenderer(table_prefix='test')
    
    def test_initialization(self):
        """Test SQLAlchemyRenderer initialization."""
        renderer = SQLAlchemyRenderer(table_prefix='prefix')
        assert renderer.table_prefix == 'prefix'
    
    def test_default_initialization(self):
        """Test SQLAlchemyRenderer with default parameters."""
        renderer = SQLAlchemyRenderer()
        assert renderer.table_prefix == ''
    
    def test_has_jinja_environment(self):
        """Test that renderer has Jinja2 environment."""
        assert hasattr(self.renderer, 'env')
        assert self.renderer.env is not None
    
    def test_has_code_value_filter(self):
        """Test that code_value filter is registered."""
        assert 'code_value' in self.renderer.env.filters
        assert callable(self.renderer.env.filters['code_value'])
    
    def test_has_sqlalchemy_column_type_filter(self):
        """Test that sqlalchemy_column_type filter is registered."""
        assert 'sqlalchemy_column_type' in self.renderer.env.filters
        assert callable(self.renderer.env.filters['sqlalchemy_column_type'])
    
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
            table_name="user",
            columns=[
                Column(name="id", db_column="id", type="int", is_pk=True, nullable=False),
                Column(name="name", db_column="name", type="varchar", max_length=100, nullable=False)
            ],
            comment="User model"
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        # Verify generated code contains expected elements
        assert "class User" in result
        assert "Base" in result
        assert "id = Column" in result or "id=Column" in result
        assert "name = Column" in result or "name=Column" in result
    
    def test_render_entity_with_default_values(self):
        """Test rendering entity with default values."""
        entity = Entity(
            name="Post",
            table_name="post",
            columns=[
                Column(name="id", db_column="id", type="int", is_pk=True, nullable=False),
                Column(name="title", db_column="title", type="varchar", max_length=200, nullable=False, default="Untitled"),
                Column(name="published", db_column="published", type="boolean", nullable=False, default=False)
            ]
        )
        model = ERModel(entities={"Post": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        # Verify default values are serialized
        assert "default=" in result
        assert '"Untitled"' in result or "'Untitled'" in result
        assert "False" in result
    
    def test_render_entity_with_comments(self):
        """Test rendering entity with comments."""
        entity = Entity(
            name="Article",
            table_name="article",
            columns=[
                Column(name="id", db_column="id", type="int", is_pk=True, nullable=False),
                Column(name="content", db_column="content", type="text", nullable=False, comment="Article content")
            ]
        )
        model = ERModel(entities={"Article": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        # Verify comments are serialized
        assert "comment=" in result
        assert "Article content" in result
    
    def test_render_entity_with_quotes_in_comment(self):
        """Test rendering entity with quotes in comments."""
        entity = Entity(
            name="Product",
            table_name="product",
            columns=[
                Column(name="id", db_column="id", type="int", is_pk=True, nullable=False),
                Column(name="name", db_column="name", type="varchar", max_length=100, nullable=False, comment='Product "name"')
            ]
        )
        model = ERModel(entities={"Product": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        # Verify generated code is valid Python
        # Should not have syntax errors from unescaped quotes
        assert "comment=" in result
        # The serializer should handle quotes properly
        assert 'Product "name"' in result or 'Product \\"name\\"' in result
    
    def test_render_multiple_entities(self):
        """Test rendering multiple entities."""
        user = Entity(
            name="User",
            table_name="user",
            columns=[Column(name="id", db_column="id", type="int", is_pk=True, nullable=False)]
        )
        post = Entity(
            name="Post",
            table_name="post",
            columns=[Column(name="id", db_column="id", type="int", is_pk=True, nullable=False)]
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
        renderer = SQLAlchemyRenderer(table_prefix='myapp')
        entity = Entity(
            name="User",
            table_name="user",
            columns=[Column(name="id", db_column="id", type="int", is_pk=True, nullable=False)]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        result = renderer.render(model)
        
        assert "__tablename__" in result
        assert "myapp" in result
    
    def test_render_validates_model_type(self):
        """Test that render validates model type."""
        with pytest.raises(AssertionError, match="Model must be an ERModel instance"):
            self.renderer.render("not a model")
    
    def test_generated_code_is_valid_python(self):
        """Test that generated code is syntactically valid."""
        entity = Entity(
            name="User",
            table_name="user",
            columns=[
                Column(name="id", db_column="id", type="int", is_pk=True, nullable=False),
                Column(name="name", db_column="name", type="varchar", max_length=100, nullable=False),
                Column(name="email", db_column="email", type="varchar", max_length=255, nullable=False)
            ]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        # Should be able to parse without syntax errors
        try:
            ast.parse(result)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{result}")
    
    def test_render_with_zero_default_value(self):
        """Test rendering with default value of 0."""
        entity = Entity(
            name="Counter",
            table_name="counter",
            columns=[
                Column(name="id", db_column="id", type="int", is_pk=True, nullable=False),
                Column(name="count", db_column="count", type="int", nullable=False, default=0)
            ]
        )
        model = ERModel(entities={"Counter": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        # Should include default=0
        assert "default=0" in result
        # Should be valid Python
        ast.parse(result)
    
    def test_render_with_false_default_value(self):
        """Test rendering with default value of False."""
        entity = Entity(
            name="Flag",
            table_name="flag",
            columns=[
                Column(name="id", db_column="id", type="int", is_pk=True, nullable=False),
                Column(name="active", db_column="active", type="boolean", nullable=False, default=False)
            ]
        )
        model = ERModel(entities={"Flag": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        # Should include default=False
        assert "default=False" in result
        # Should be valid Python
        ast.parse(result)
    
    def test_render_with_empty_string_default_value(self):
        """Test rendering with default value of empty string."""
        entity = Entity(
            name="Text",
            table_name="text",
            columns=[
                Column(name="id", db_column="id", type="int", is_pk=True, nullable=False),
                Column(name="content", db_column="content", type="varchar", max_length=100, nullable=False, default="")
            ]
        )
        model = ERModel(entities={"Text": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        # Should include default=""
        assert 'default=""' in result
        # Should be valid Python
        ast.parse(result)

    def test_render_with_unique_attribute(self):
        """Test rendering with unique=True attribute."""
        entity = Entity(
            name="User",
            table_name="user",
            columns=[
                Column(name="id", db_column="id", type="int", is_pk=True, nullable=False),
                Column(name="email", db_column="email", type="varchar", max_length=255, nullable=False, unique=True)
            ]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        # Should include unique=True
        assert "unique=True" in result
        # Should be valid Python
        ast.parse(result)
    
    def test_render_with_index_attribute(self):
        """Test rendering with indexed=True attribute."""
        entity = Entity(
            name="Post",
            table_name="post",
            columns=[
                Column(name="id", db_column="id", type="int", is_pk=True, nullable=False),
                Column(name="slug", db_column="slug", type="varchar", max_length=200, nullable=False, indexed=True)
            ]
        )
        model = ERModel(entities={"Post": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        # Should include index=True
        assert "index=True" in result
        # Should be valid Python
        ast.parse(result)
    
    def test_render_with_multiple_attributes(self):
        """Test rendering with multiple attributes (unique, indexed, nullable, default, comment)."""
        entity = Entity(
            name="Product",
            table_name="product",
            columns=[
                Column(name="id", db_column="id", type="int", is_pk=True, nullable=False),
                Column(
                    name="sku",
                    db_column="sku",
                    type="varchar",
                    max_length=50,
                    nullable=False,
                    unique=True,
                    indexed=True,
                    default="SKU-000",
                    comment="Product SKU"
                )
            ]
        )
        model = ERModel(entities={"Product": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        # Should include all attributes
        assert "nullable=False" in result
        assert "unique=True" in result
        assert "index=True" in result
        assert "default=" in result
        assert "SKU-000" in result
        assert "comment=" in result
        assert "Product SKU" in result
        # Should be valid Python
        ast.parse(result)
    
    def test_parameter_order(self):
        """Test that parameters are in correct order: primary_key, nullable, unique, index, default, comment."""
        entity = Entity(
            name="Item",
            table_name="item",
            columns=[
                Column(
                    name="code",
                    db_column="code",
                    type="varchar",
                    max_length=20,
                    nullable=False,
                    unique=True,
                    indexed=True,
                    default="CODE",
                    comment="Item code"
                )
            ]
        )
        model = ERModel(entities={"Item": entity}, relationships=[], templates={})
        result = self.renderer.render(model)
        
        # Find the column definition line
        lines = result.split('\n')
        code_line = [line for line in lines if 'code = Column' in line or 'code=Column' in line][0]
        
        # Check parameter order
        nullable_pos = code_line.find('nullable=')
        unique_pos = code_line.find('unique=')
        index_pos = code_line.find('index=')
        default_pos = code_line.find('default=')
        comment_pos = code_line.find('comment=')
        
        # All should be present
        assert nullable_pos > 0
        assert unique_pos > 0
        assert index_pos > 0
        assert default_pos > 0
        assert comment_pos > 0
        
        # Order should be: nullable < unique < index < default < comment
        assert nullable_pos < unique_pos
        assert unique_pos < index_pos
        assert index_pos < default_pos
        assert default_pos < comment_pos
