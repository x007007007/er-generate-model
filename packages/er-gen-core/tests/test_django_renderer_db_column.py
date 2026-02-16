"""
Unit tests for Django renderer db_column generation - Task 4.2.

Tests that the Django renderer correctly generates db_column parameters
in field definitions only when db_column differs from the field name.
"""
import pytest
import ast
from x007007007.er.renderers.python.django import DjangoRenderer, DjangoPackageRenderer
from x007007007.er.models import ERModel, Entity, Column


class TestDjangoRendererDbColumnGeneration:
    """Test Django renderer db_column parameter generation - Task 4.2."""
    
    def test_db_column_different_from_name_includes_parameter(self):
        """Test that db_column parameter is included when different from name."""
        entity = Entity(
            name="User",
            table_name="auth_user",
            columns=[
                Column(name="id", type="int", db_column="id", is_pk=True, nullable=False),
                Column(name="username", type="varchar", db_column="user_name", max_length=100, nullable=False)
            ]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        renderer = DjangoRenderer()
        result = renderer.render(model)
        
        # Should include db_column for username field
        assert "db_column='user_name'" in result
        # Should not include db_column for id field (same as name)
        assert "id = models." in result
        # Count occurrences - should only have one db_column
        assert result.count("db_column=") == 1
    
    def test_db_column_same_as_name_excludes_parameter(self):
        """Test that db_column parameter is excluded when same as name."""
        entity = Entity(
            name="Post",
            table_name="blog_post",
            columns=[
                Column(name="id", type="int", db_column="id", is_pk=True, nullable=False),
                Column(name="title", type="varchar", db_column="title", max_length=200, nullable=False),
                Column(name="content", type="text", db_column="content", nullable=False)
            ]
        )
        model = ERModel(entities={"Post": entity}, relationships=[], templates={})
        renderer = DjangoRenderer()
        result = renderer.render(model)
        
        # Should not include db_column for any field (all same as name)
        assert "db_column=" not in result
    
    def test_mixed_db_column_scenarios(self):
        """Test entity with mixed db_column scenarios."""
        entity = Entity(
            name="Article",
            table_name="cms_article",
            columns=[
                Column(name="id", type="int", db_column="id", is_pk=True, nullable=False),
                Column(name="title", type="varchar", db_column="article_title", max_length=200, nullable=False),
                Column(name="content", type="text", db_column="content", nullable=False),
                Column(name="author", type="varchar", db_column="author_name", max_length=100, nullable=False)
            ]
        )
        model = ERModel(entities={"Article": entity}, relationships=[], templates={})
        renderer = DjangoRenderer()
        result = renderer.render(model)
        
        # Should include db_column for title and author (different from name)
        assert "db_column='article_title'" in result
        assert "db_column='author_name'" in result
        # Should not include db_column for id and content (same as name)
        assert result.count("db_column=") == 2
    
    def test_db_table_always_included_in_meta(self):
        """Test that db_table is always included in Meta class."""
        entity = Entity(
            name="Product",
            table_name="shop_product",
            columns=[
                Column(name="id", type="int", db_column="id", is_pk=True, nullable=False),
                Column(name="name", type="varchar", db_column="name", max_length=100, nullable=False)
            ]
        )
        model = ERModel(entities={"Product": entity}, relationships=[], templates={})
        renderer = DjangoRenderer()
        result = renderer.render(model)
        
        # Should always include db_table in Meta
        assert "class Meta:" in result
        assert "db_table = 'shop_product'" in result
    
    def test_generated_code_with_db_column_is_valid_python(self):
        """Test that generated code with db_column is syntactically valid."""
        entity = Entity(
            name="Customer",
            table_name="crm_customer",
            columns=[
                Column(name="id", type="int", db_column="customer_id", is_pk=True, nullable=False),
                Column(name="email", type="varchar", db_column="email_address", max_length=255, nullable=False),
                Column(name="phone", type="varchar", db_column="phone_number", max_length=20, nullable=True)
            ]
        )
        model = ERModel(entities={"Customer": entity}, relationships=[], templates={})
        renderer = DjangoRenderer()
        result = renderer.render(model)
        
        # Should be able to parse without syntax errors
        try:
            ast.parse(result)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{result}")


class TestDjangoPackageRendererDbColumnGeneration:
    """Test DjangoPackageRenderer db_column parameter generation - Task 4.2."""
    
    def test_package_renderer_db_column_different_from_name(self):
        """Test that package renderer includes db_column when different from name."""
        entity = Entity(
            name="User",
            table_name="auth_user",
            columns=[
                Column(name="id", type="int", db_column="id", is_pk=True, nullable=False),
                Column(name="username", type="varchar", db_column="user_name", max_length=100, nullable=False)
            ]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        renderer = DjangoPackageRenderer()
        result = renderer.render(model)
        
        # Check the model file
        model_content = result['user.py']
        assert "db_column='user_name'" in model_content
        # Should not include db_column for id field
        assert model_content.count("db_column=") == 1
    
    def test_package_renderer_db_column_same_as_name(self):
        """Test that package renderer excludes db_column when same as name."""
        entity = Entity(
            name="Post",
            table_name="blog_post",
            columns=[
                Column(name="id", type="int", db_column="id", is_pk=True, nullable=False),
                Column(name="title", type="varchar", db_column="title", max_length=200, nullable=False)
            ]
        )
        model = ERModel(entities={"Post": entity}, relationships=[], templates={})
        renderer = DjangoPackageRenderer()
        result = renderer.render(model)
        
        # Check the model file
        model_content = result['post.py']
        assert "db_column=" not in model_content
    
    def test_package_renderer_db_table_always_included(self):
        """Test that package renderer always includes db_table in Meta."""
        entity = Entity(
            name="Product",
            table_name="shop_product",
            columns=[
                Column(name="id", type="int", db_column="id", is_pk=True, nullable=False)
            ]
        )
        model = ERModel(entities={"Product": entity}, relationships=[], templates={})
        renderer = DjangoPackageRenderer()
        result = renderer.render(model)
        
        # Check the model file
        model_content = result['product.py']
        assert "class Meta:" in model_content
        assert "db_table = 'shop_product'" in model_content
    
    def test_package_renderer_all_files_valid_python_with_db_column(self):
        """Test that all package files with db_column are syntactically valid."""
        entity = Entity(
            name="Order",
            table_name="sales_order",
            columns=[
                Column(name="id", type="int", db_column="order_id", is_pk=True, nullable=False),
                Column(name="total", type="decimal", db_column="total_amount", precision=10, scale=2, nullable=False)
            ]
        )
        model = ERModel(entities={"Order": entity}, relationships=[], templates={})
        renderer = DjangoPackageRenderer()
        result = renderer.render(model)
        
        # All files should be valid Python
        for filename, content in result.items():
            try:
                ast.parse(content)
            except SyntaxError as e:
                pytest.fail(f"File {filename} has syntax error: {e}\n{content}")
