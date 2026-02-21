"""
Unit tests for Task 1.3: Ensure fields with max_length have complete parameter integrity.

This test verifies that fields with max_length (like String(255)) correctly include
all field attributes (nullable, unique, index) after the type parameter.

Validates Requirements: 3.1, 3.2, 6.4
"""
import ast
import pytest
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer
from x007007007.er.models import ERModel, Entity, Column


class TestMaxLengthFieldAttributes:
    """Tests for fields with max_length parameter integrity."""
    
    def test_max_length_field_with_nullable_false(self):
        """Test that fields with max_length include nullable=False.
        
        Validates: Requirement 3.1
        """
        entity = Entity(
            name="User",
            table_name="user",
            columns=[
                Column(name="id", db_column="id", type="int", is_pk=True, nullable=False),
                Column(
                    name="username",
                    db_column="username",
                    type="varchar",
                    max_length=50,
                    nullable=False
                )
            ]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Should include String(50) with nullable=False
        assert "String(50)" in result
        assert "nullable=False" in result
        
        # Find the username line
        lines = result.split('\n')
        username_line = [line for line in lines if 'username' in line and 'Column' in line][0]
        
        # Verify nullable=False appears after String(50)
        assert "String(50)" in username_line
        assert "nullable=False" in username_line
        
        # Should be valid Python
        ast.parse(result)
    
    def test_max_length_field_with_unique(self):
        """Test that fields with max_length include unique=True.
        
        Validates: Requirement 3.1, 6.4
        """
        entity = Entity(
            name="User",
            table_name="user",
            columns=[
                Column(name="id", db_column="id", type="int", is_pk=True, nullable=False),
                Column(
                    name="email",
                    db_column="email",
                    type="varchar",
                    max_length=255,
                    nullable=False,
                    unique=True
                )
            ]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Should include String(255) with both nullable=False and unique=True
        assert "String(255)" in result
        assert "nullable=False" in result
        assert "unique=True" in result
        
        # Find the email line
        lines = result.split('\n')
        email_line = [line for line in lines if 'email' in line and 'Column' in line][0]
        
        # Verify both attributes appear after String(255)
        assert "String(255)" in email_line
        assert "nullable=False" in email_line
        assert "unique=True" in email_line
        
        # Should be valid Python
        ast.parse(result)
    
    def test_max_length_field_with_index(self):
        """Test that fields with max_length include index=True.
        
        Validates: Requirement 3.1, 6.4
        """
        entity = Entity(
            name="Post",
            table_name="post",
            columns=[
                Column(name="id", db_column="id", type="int", is_pk=True, nullable=False),
                Column(
                    name="slug",
                    db_column="slug",
                    type="varchar",
                    max_length=200,
                    nullable=False,
                    indexed=True
                )
            ]
        )
        model = ERModel(entities={"Post": entity}, relationships=[], templates={})
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Should include String(200) with both nullable=False and index=True
        assert "String(200)" in result
        assert "nullable=False" in result
        assert "index=True" in result
        
        # Find the slug line
        lines = result.split('\n')
        slug_line = [line for line in lines if 'slug' in line and 'Column' in line][0]
        
        # Verify both attributes appear after String(200)
        assert "String(200)" in slug_line
        assert "nullable=False" in slug_line
        assert "index=True" in slug_line
        
        # Should be valid Python
        ast.parse(result)
    
    def test_max_length_field_with_all_attributes(self):
        """Test that fields with max_length include all attributes.
        
        Validates: Requirement 3.1, 3.2, 6.4
        """
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
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Should include String(50) with all attributes
        assert "String(50)" in result
        assert "nullable=False" in result
        assert "unique=True" in result
        assert "index=True" in result
        assert "default=" in result
        assert "SKU-000" in result
        assert "comment=" in result
        assert "Product SKU" in result
        
        # Find the sku line
        lines = result.split('\n')
        sku_line = [line for line in lines if 'sku' in line and 'Column' in line][0]
        
        # Verify all attributes appear after String(50)
        assert "String(50)" in sku_line
        assert "nullable=False" in sku_line
        assert "unique=True" in sku_line
        assert "index=True" in sku_line
        assert "default=" in sku_line
        assert "comment=" in sku_line
        
        # Should be valid Python
        ast.parse(result)
    
    def test_max_length_field_parameter_order(self):
        """Test that parameters are in correct order for fields with max_length.
        
        Validates: Requirement 6.4, 7.1
        """
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
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Find the column definition line
        lines = result.split('\n')
        code_line = [line for line in lines if 'code' in line and 'Column' in line][0]
        
        # Check parameter order
        string_pos = code_line.find('String(20)')
        nullable_pos = code_line.find('nullable=')
        unique_pos = code_line.find('unique=')
        index_pos = code_line.find('index=')
        default_pos = code_line.find('default=')
        comment_pos = code_line.find('comment=')
        
        # All should be present
        assert string_pos > 0
        assert nullable_pos > 0
        assert unique_pos > 0
        assert index_pos > 0
        assert default_pos > 0
        assert comment_pos > 0
        
        # Order should be: String(20) < nullable < unique < index < default < comment
        assert string_pos < nullable_pos
        assert nullable_pos < unique_pos
        assert unique_pos < index_pos
        assert index_pos < default_pos
        assert default_pos < comment_pos
    
    def test_max_length_field_without_nullable(self):
        """Test that fields with max_length and nullable=True don't include nullable parameter.
        
        Validates: Requirement 3.3
        """
        entity = Entity(
            name="User",
            table_name="user",
            columns=[
                Column(name="id", db_column="id", type="int", is_pk=True, nullable=False),
                Column(
                    name="nickname",
                    db_column="nickname",
                    type="varchar",
                    max_length=50,
                    nullable=True  # Default value, should not be included
                )
            ]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        # Find the nickname line
        lines = result.split('\n')
        nickname_line = [line for line in lines if 'nickname' in line and 'Column' in line][0]
        
        # Should include String(50) but not nullable parameter
        assert "String(50)" in nickname_line
        assert "nullable" not in nickname_line
        
        # Should be valid Python
        ast.parse(result)
    
    def test_multiple_max_length_fields_with_different_attributes(self):
        """Test multiple fields with max_length have correct attributes.
        
        Validates: Requirement 6.4
        """
        entity = Entity(
            name="User",
            table_name="user",
            columns=[
                Column(name="id", db_column="id", type="int", is_pk=True, nullable=False),
                Column(
                    name="username",
                    db_column="username",
                    type="varchar",
                    max_length=50,
                    nullable=False,
                    unique=True
                ),
                Column(
                    name="email",
                    db_column="email",
                    type="varchar",
                    max_length=255,
                    nullable=False,
                    unique=True,
                    indexed=True
                ),
                Column(
                    name="bio",
                    db_column="bio",
                    type="varchar",
                    max_length=500,
                    nullable=True
                )
            ]
        )
        model = ERModel(entities={"User": entity}, relationships=[], templates={})
        renderer = SQLAlchemyRenderer()
        result = renderer.render(model)
        
        lines = result.split('\n')
        
        # Check username: String(50), nullable=False, unique=True
        username_line = [line for line in lines if 'username' in line and 'Column' in line][0]
        assert "String(50)" in username_line
        assert "nullable=False" in username_line
        assert "unique=True" in username_line
        assert "index=" not in username_line
        
        # Check email: String(255), nullable=False, unique=True, index=True
        email_line = [line for line in lines if 'email' in line and 'Column' in line][0]
        assert "String(255)" in email_line
        assert "nullable=False" in email_line
        assert "unique=True" in email_line
        assert "index=True" in email_line
        
        # Check bio: String(500), no nullable parameter
        bio_line = [line for line in lines if 'bio' in line and 'Column' in line][0]
        assert "String(500)" in bio_line
        assert "nullable" not in bio_line
        assert "unique" not in bio_line
        assert "index" not in bio_line
        
        # Should be valid Python
        ast.parse(result)
