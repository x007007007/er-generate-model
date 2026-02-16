"""
Tests for TOMLRenderer - Task 7.1

Tests the extends field output functionality in TOMLRenderer.
"""
import pytest
import toml
from x007007007.er.models import Entity, Column, ERModel
from x007007007.er_django.renderers import TOMLRenderer


class TestTOMLRendererExtends:
    """Test TOMLRenderer extends field output - Task 7.1"""
    
    def test_render_with_extends_field(self):
        """Test that extends field is output when present"""
        # Create entity with extends
        entity = Entity(
            name="User",
            extends=["django.contrib.auth.models.AbstractUser"],
            columns=[
                Column(name="phone", type="CharField", max_length=20, nullable=True, unique=True)
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
        assert "extends" in data["entities"]["User"]
        assert data["entities"]["User"]["extends"] == ["django.contrib.auth.models.AbstractUser"]
    
    def test_render_with_multiple_extends(self):
        """Test that multiple inheritance is correctly output"""
        # Create entity with multiple extends
        entity = Entity(
            name="Profile",
            extends=[
                "kinkotech.common.base.TimeStampedModel",
                "kinkotech.common.base.SoftDeleteModel"
            ],
            columns=[
                Column(name="bio", type="TextField", nullable=True)
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
        assert "Profile" in data["entities"]
        assert "extends" in data["entities"]["Profile"]
        assert len(data["entities"]["Profile"]["extends"]) == 2
        assert "kinkotech.common.base.TimeStampedModel" in data["entities"]["Profile"]["extends"]
        assert "kinkotech.common.base.SoftDeleteModel" in data["entities"]["Profile"]["extends"]
    
    def test_render_without_extends_field(self):
        """Test that extends field is not output when empty"""
        # Create entity without extends
        entity = Entity(
            name="SimpleModel",
            extends=[],  # Empty list
            columns=[
                Column(name="name", type="CharField", max_length=100)
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
        assert "SimpleModel" in data["entities"]
        # extends field should not be present when empty
        assert "extends" not in data["entities"]["SimpleModel"]
    
    def test_render_with_extends_default_value(self):
        """Test that extends field is not output when using default value (empty list)"""
        # Create entity with default extends (not explicitly set)
        entity = Entity(
            name="DefaultModel",
            columns=[
                Column(name="id", type="IntegerField", is_pk=True)
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
        assert "DefaultModel" in data["entities"]
        # extends field should not be present when using default empty list
        assert "extends" not in data["entities"]["DefaultModel"]
    
    def test_render_multiple_entities_mixed_extends(self):
        """Test rendering multiple entities with mixed extends configurations"""
        # Entity with extends
        entity1 = Entity(
            name="User",
            extends=["django.contrib.auth.models.AbstractUser"],
            columns=[Column(name="phone", type="CharField", max_length=20)]
        )
        
        # Entity without extends
        entity2 = Entity(
            name="Tag",
            extends=[],
            columns=[Column(name="name", type="CharField", max_length=50)]
        )
        
        # Entity with multiple extends
        entity3 = Entity(
            name="Post",
            extends=["kinkotech.common.base.TimeStampedModel"],
            columns=[Column(name="title", type="CharField", max_length=200)]
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
        
        # User should have extends
        assert "extends" in data["entities"]["User"]
        assert data["entities"]["User"]["extends"] == ["django.contrib.auth.models.AbstractUser"]
        
        # Tag should not have extends
        assert "extends" not in data["entities"]["Tag"]
        
        # Post should have extends
        assert "extends" in data["entities"]["Post"]
        assert data["entities"]["Post"]["extends"] == ["kinkotech.common.base.TimeStampedModel"]
    
    def test_render_extends_with_columns(self):
        """Test that extends field is output correctly along with columns"""
        # Create entity with both extends and columns
        entity = Entity(
            name="CustomUser",
            extends=["django.contrib.auth.models.AbstractUser"],
            columns=[
                Column(name="phone", type="CharField", max_length=20, nullable=True),
                Column(name="avatar", type="ImageField", nullable=True),
                Column(name="bio", type="TextField", nullable=True)
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
        
        # Check extends field
        assert "extends" in data["entities"]["CustomUser"]
        assert data["entities"]["CustomUser"]["extends"] == ["django.contrib.auth.models.AbstractUser"]
        
        # Check columns are also present
        assert "columns" in data["entities"]["CustomUser"]
        assert len(data["entities"]["CustomUser"]["columns"]) == 3
        
        column_names = [col["name"] for col in data["entities"]["CustomUser"]["columns"]]
        assert "phone" in column_names
        assert "avatar" in column_names
        assert "bio" in column_names


class TestTOMLRendererExportPath:
    """Test TOMLRenderer export_path field output - Task 7.3"""
    
    def test_render_with_export_path_field(self):
        """Test that export_path field is NOT output even when present (per requirement 2.4)"""
        # Create entity with export_path
        entity = Entity(
            name="User",
            export_path="src/kinkotech/common/domains/account/models.toml",
            columns=[
                Column(name="phone", type="CharField", max_length=20, nullable=True)
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
        # Per requirement 2.4: export_path should NOT be in output
        assert "export_path" not in data["entities"]["User"]
    
    def test_render_without_export_path_field(self):
        """Test that export_path field is not output when None"""
        # Create entity without export_path (None)
        entity = Entity(
            name="SimpleModel",
            export_path=None,
            columns=[
                Column(name="name", type="CharField", max_length=100)
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
        assert "SimpleModel" in data["entities"]
        # export_path field should not be present when None
        assert "export_path" not in data["entities"]["SimpleModel"]
    
    def test_render_with_export_path_default_value(self):
        """Test that export_path field is not output when using default value (None)"""
        # Create entity with default export_path (not explicitly set)
        entity = Entity(
            name="DefaultModel",
            columns=[
                Column(name="id", type="IntegerField", is_pk=True)
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
        assert "DefaultModel" in data["entities"]
        # export_path field should not be present when using default None
        assert "export_path" not in data["entities"]["DefaultModel"]
    
    def test_render_multiple_entities_mixed_export_path(self):
        """Test rendering multiple entities - export_path should NOT be output (per requirement 2.4)"""
        # Entity with export_path
        entity1 = Entity(
            name="User",
            export_path="src/app1/models.toml",
            columns=[Column(name="phone", type="CharField", max_length=20)]
        )
        
        # Entity without export_path
        entity2 = Entity(
            name="Tag",
            export_path=None,
            columns=[Column(name="name", type="CharField", max_length=50)]
        )
        
        # Entity with different export_path
        entity3 = Entity(
            name="Post",
            export_path="src/app2/models.toml",
            columns=[Column(name="title", type="CharField", max_length=200)]
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
        
        # Per requirement 2.4: export_path should NOT be in output for any entity
        assert "export_path" not in data["entities"]["User"]
        assert "export_path" not in data["entities"]["Tag"]
        assert "export_path" not in data["entities"]["Post"]
    
    def test_render_export_path_with_extends_and_package(self):
        """Test that export_path is NOT output even with extends and package (per requirement 2.4)"""
        # Create entity with export_path, extends, and package
        entity = Entity(
            name="CustomUser",
            extends=["django.contrib.auth.models.AbstractUser"],
            package="kinkotech.common.domains.account.models",
            export_path="src/kinkotech/common/domains/account/models.toml",
            columns=[
                Column(name="phone", type="CharField", max_length=20, nullable=True),
                Column(name="avatar", type="ImageField", nullable=True)
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
        
        # Check extends and package are present
        assert "extends" in data["entities"]["CustomUser"]
        assert data["entities"]["CustomUser"]["extends"] == ["django.contrib.auth.models.AbstractUser"]
        
        assert "package" in data["entities"]["CustomUser"]
        assert data["entities"]["CustomUser"]["package"] == "kinkotech.common.domains.account.models"
        
        # Per requirement 2.4: export_path should NOT be in output
        assert "export_path" not in data["entities"]["CustomUser"]
        
        # Check columns are also present
        assert "columns" in data["entities"]["CustomUser"]
        assert len(data["entities"]["CustomUser"]["columns"]) == 2
    
    def test_render_export_path_with_pathlib_path(self):
        """Test that export_path is converted to string when it's a Path object"""
        from pathlib import Path
        
        # Create entity with Path object as export_path
        entity = Entity(
            name="User",
            export_path=Path("src/kinkotech/common/domains/account/models.toml"),
            columns=[
                Column(name="phone", type="CharField", max_length=20)
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
        # Per requirement 2.4: export_path should NOT be in output
        assert "export_path" not in data["entities"]["User"]
    
    def test_render_export_path_with_absolute_path(self):
        """Test that export_path works with absolute paths"""
        # Create entity with absolute path
        entity = Entity(
            name="User",
            export_path="/absolute/path/to/models.toml",
            columns=[
                Column(name="id", type="IntegerField", is_pk=True)
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
        # Per requirement 2.4: export_path should NOT be in output
        assert "export_path" not in data["entities"]["User"]
