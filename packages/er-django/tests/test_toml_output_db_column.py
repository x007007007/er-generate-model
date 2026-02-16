"""
Unit tests for TOML output format - Task 3.3

Tests db_column and table_name output in TOMLRenderer.
Validates Requirement 1.4.
"""
import pytest
import toml
from x007007007.er.models import Entity, Column, ERModel
from x007007007.er_django.renderers import TOMLRenderer


class TestTOMLRendererDbColumn:
    """Test TOMLRenderer db_column field output - Task 3.3"""
    
    def test_db_column_output_when_different_from_name(self):
        """Test that db_column is output when different from name"""
        # Create entity with db_column different from name
        entity = Entity(
            name="User",
            table_name="auth_user",
            columns=[
                Column(name="username", type="CharField", db_column="user_name", max_length=50)
            ]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Parse TOML to verify
        data = toml.loads(toml_output)
        
        assert "entities" in data
        assert "User" in data["entities"]
        assert "columns" in data["entities"]["User"]
        assert len(data["entities"]["User"]["columns"]) == 1
        
        column = data["entities"]["User"]["columns"][0]
        assert column["name"] == "username"
        assert column["db_column"] == "user_name"
        assert column["type"] == "CharField"
    
    def test_db_column_not_output_when_same_as_name(self):
        """Test that db_column is NOT output when same as name"""
        # Create entity with db_column same as name
        entity = Entity(
            name="User",
            table_name="auth_user",
            columns=[
                Column(name="email", type="EmailField", db_column="email")
            ]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Parse TOML to verify
        data = toml.loads(toml_output)
        
        assert "entities" in data
        assert "User" in data["entities"]
        assert "columns" in data["entities"]["User"]
        assert len(data["entities"]["User"]["columns"]) == 1
        
        column = data["entities"]["User"]["columns"][0]
        assert column["name"] == "email"
        assert "db_column" not in column  # Should not be present
        assert column["type"] == "EmailField"
    
    def test_mixed_db_column_output(self):
        """Test mixed scenario with some columns having different db_column"""
        # Create entity with mixed db_column scenarios
        entity = Entity(
            name="Product",
            table_name="products",
            columns=[
                Column(name="product_name", type="CharField", db_column="name", max_length=100),
                Column(name="price", type="DecimalField", db_column="price", precision=10, scale=2),
                Column(name="created_at", type="DateTimeField", db_column="created_date")
            ]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Parse TOML to verify
        data = toml.loads(toml_output)
        
        assert "entities" in data
        assert "Product" in data["entities"]
        assert "columns" in data["entities"]["Product"]
        assert len(data["entities"]["Product"]["columns"]) == 3
        
        columns = {col["name"]: col for col in data["entities"]["Product"]["columns"]}
        
        # product_name has different db_column
        assert "db_column" in columns["product_name"]
        assert columns["product_name"]["db_column"] == "name"
        
        # price has same db_column
        assert "db_column" not in columns["price"]
        
        # created_at has different db_column
        assert "db_column" in columns["created_at"]
        assert columns["created_at"]["db_column"] == "created_date"


class TestTOMLRendererTableName:
    """Test TOMLRenderer table_name field output - Task 3.3"""
    
    def test_table_name_always_output(self):
        """Test that table_name is always output for Entity"""
        # Create entity with table_name
        entity = Entity(
            name="User",
            table_name="auth_user",
            columns=[
                Column(name="id", type="IntegerField", db_column="id", is_pk=True)
            ]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Parse TOML to verify
        data = toml.loads(toml_output)
        
        assert "entities" in data
        assert "User" in data["entities"]
        assert "table_name" in data["entities"]["User"]
        assert data["entities"]["User"]["table_name"] == "auth_user"
    
    def test_table_name_output_with_different_entity_name(self):
        """Test table_name output when different from entity name"""
        # Create entity where table_name differs from entity name
        entity = Entity(
            name="CustomUser",
            table_name="users",
            columns=[
                Column(name="username", type="CharField", db_column="username", max_length=50)
            ]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Parse TOML to verify
        data = toml.loads(toml_output)
        
        assert "entities" in data
        assert "CustomUser" in data["entities"]
        assert "table_name" in data["entities"]["CustomUser"]
        assert data["entities"]["CustomUser"]["table_name"] == "users"
    
    def test_table_name_output_multiple_entities(self):
        """Test that table_name is output for all entities"""
        # Create multiple entities
        entity1 = Entity(
            name="User",
            table_name="auth_user",
            columns=[Column(name="id", type="IntegerField", db_column="id", is_pk=True)]
        )
        
        entity2 = Entity(
            name="Post",
            table_name="blog_posts",
            columns=[Column(name="title", type="CharField", db_column="title", max_length=200)]
        )
        
        entity3 = Entity(
            name="Comment",
            table_name="comments",
            columns=[Column(name="text", type="TextField", db_column="text")]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity1)
        er_model.add_entity(entity2)
        er_model.add_entity(entity3)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Parse TOML to verify
        data = toml.loads(toml_output)
        
        assert "entities" in data
        assert len(data["entities"]) == 3
        
        # All entities should have table_name
        assert "table_name" in data["entities"]["User"]
        assert data["entities"]["User"]["table_name"] == "auth_user"
        
        assert "table_name" in data["entities"]["Post"]
        assert data["entities"]["Post"]["table_name"] == "blog_posts"
        
        assert "table_name" in data["entities"]["Comment"]
        assert data["entities"]["Comment"]["table_name"] == "comments"
    
    def test_table_name_with_db_column_combination(self):
        """Test table_name output combined with db_column scenarios"""
        # Create entity with both table_name and mixed db_column
        entity = Entity(
            name="Product",
            table_name="inventory_products",
            columns=[
                Column(name="product_id", type="IntegerField", db_column="id", is_pk=True),
                Column(name="name", type="CharField", db_column="name", max_length=100),
                Column(name="sku", type="CharField", db_column="product_sku", max_length=50)
            ]
        )
        
        er_model = ERModel()
        er_model.add_entity(entity)
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        
        # Parse TOML to verify
        data = toml.loads(toml_output)
        
        assert "entities" in data
        assert "Product" in data["entities"]
        
        # table_name should always be present
        assert "table_name" in data["entities"]["Product"]
        assert data["entities"]["Product"]["table_name"] == "inventory_products"
        
        # Check db_column output logic
        columns = {col["name"]: col for col in data["entities"]["Product"]["columns"]}
        
        # product_id has different db_column
        assert "db_column" in columns["product_id"]
        assert columns["product_id"]["db_column"] == "id"
        
        # name has same db_column
        assert "db_column" not in columns["name"]
        
        # sku has different db_column
        assert "db_column" in columns["sku"]
        assert columns["sku"]["db_column"] == "product_sku"
