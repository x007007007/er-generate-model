"""
Tests for ImportPathGenerator namespace transformation functionality.

This module tests the framework-specific namespace transformation feature,
particularly for SQLAlchemy import generation from Django namespaces.
"""

import pytest
from x007007007.er.import_path_generator import ImportPathGenerator, ImportSpec


class TestNamespaceTransformation:
    """Test namespace transformation for different frameworks"""
    
    def test_no_transformation_when_no_framework(self):
        """When no target_framework is specified, namespace should not be transformed"""
        generator = ImportPathGenerator()
        
        result = generator.generate(
            "kinkotech.common.models.base",
            "project",
            "BaseModel"
        )
        
        assert result == "from kinkotech.common.models.base import BaseModel"
    
    def test_sqlalchemy_transformation_project_model(self):
        """SQLAlchemy framework should append _sqlalchemy to module path"""
        generator = ImportPathGenerator(target_framework="sqlalchemy")
        
        result = generator.generate(
            "kinkotech.common.models.base",
            "project",
            "BaseModel"
        )
        
        assert result == "from kinkotech.common.models.base_sqlalchemy import BaseModel"
    
    def test_sqlalchemy_transformation_third_party_model(self):
        """SQLAlchemy transformation should work with third-party models"""
        generator = ImportPathGenerator(
            third_party_dir="third",
            target_framework="sqlalchemy"
        )
        
        result = generator.generate(
            "django.contrib.auth.models",
            "third-party",
            "AbstractUser"
        )
        
        assert result == "from third.django.contrib.auth.models_sqlalchemy import AbstractUser"
    
    def test_sqlalchemy_transformation_with_class_in_namespace(self):
        """When namespace includes class name, only transform module path"""
        generator = ImportPathGenerator(target_framework="sqlalchemy")
        
        # Namespace with class name at the end
        result = generator.generate(
            "kinkotech.common.models.base.BaseModel",
            "project",
            "BaseModel"
        )
        
        # Should transform only the module part, not the class name
        assert result == "from kinkotech.common.models.base_sqlalchemy import BaseModel"
    
    def test_sqlalchemy_transformation_deep_namespace(self):
        """Transformation should work with deeply nested namespaces"""
        generator = ImportPathGenerator(target_framework="sqlalchemy")
        
        result = generator.generate(
            "kinkotech.rfc_backend.domains.route_plan.models.route",
            "project",
            "Route"
        )
        
        assert result == "from kinkotech.rfc_backend.domains.route_plan.models.route_sqlalchemy import Route"
    
    def test_batch_generation_with_transformation(self):
        """Batch generation should apply transformation to all imports"""
        generator = ImportPathGenerator(target_framework="sqlalchemy")
        
        imports = [
            ImportSpec(
                namespace="kinkotech.common.models.base",
                model_name="BaseModel",
                location_type="project"
            ),
            ImportSpec(
                namespace="kinkotech.common.models.base",
                model_name="CreateModifyMixin",
                location_type="project"
            ),
        ]
        
        results = generator.generate_batch(imports)
        
        assert len(results) == 2
        assert results[0] == "from kinkotech.common.models.base_sqlalchemy import BaseModel"
        assert results[1] == "from kinkotech.common.models.base_sqlalchemy import CreateModifyMixin"
    
    def test_custom_third_party_dir_with_transformation(self):
        """Custom third-party directory should work with transformation"""
        generator = ImportPathGenerator(
            third_party_dir="external",
            target_framework="sqlalchemy"
        )
        
        result = generator.generate(
            "django.db.models",
            "third-party",
            "Model"
        )
        
        assert result == "from external.django.db.models_sqlalchemy import Model"


class TestTransformNamespaceMethod:
    """Test the _transform_namespace method directly"""
    
    def test_transform_simple_namespace(self):
        """Transform a simple namespace"""
        generator = ImportPathGenerator(target_framework="sqlalchemy")
        
        result = generator._transform_namespace("myapp.models")
        assert result == "myapp.models_sqlalchemy"
    
    def test_transform_namespace_with_class(self):
        """Transform namespace that includes a class name"""
        generator = ImportPathGenerator(target_framework="sqlalchemy")
        
        # Class name (PascalCase) should not be transformed
        result = generator._transform_namespace("myapp.models.MyModel")
        assert result == "myapp.models_sqlalchemy"
    
    def test_no_transform_without_framework(self):
        """Without target_framework, namespace should remain unchanged"""
        generator = ImportPathGenerator()
        
        result = generator._transform_namespace("myapp.models.base")
        assert result == "myapp.models.base"
    
    def test_transform_single_component(self):
        """Transform namespace with single component"""
        generator = ImportPathGenerator(target_framework="sqlalchemy")
        
        result = generator._transform_namespace("models")
        assert result == "models_sqlalchemy"


class TestRealWorldScenarios:
    """Test real-world usage scenarios"""
    
    def test_kinkotech_base_models(self):
        """Test with actual kinkotech base models"""
        generator = ImportPathGenerator(target_framework="sqlalchemy")
        
        # KinkoTechModelBase
        result1 = generator.generate(
            "kinkotech.common.infrastructure.models.base",
            "project",
            "KinkoTechModelBase"
        )
        assert result1 == "from kinkotech.common.infrastructure.models.base_sqlalchemy import KinkoTechModelBase"
        
        # CreateModifyMixinModel
        result2 = generator.generate(
            "kinkotech.common.infrastructure.models.base",
            "project",
            "CreateModifyMixinModel"
        )
        assert result2 == "from kinkotech.common.infrastructure.models.base_sqlalchemy import CreateModifyMixinModel"
    
    def test_route_plan_models(self):
        """Test with route plan domain models"""
        generator = ImportPathGenerator(target_framework="sqlalchemy")
        
        result = generator.generate(
            "kinkotech.rfc_backend.domains.route_plan.models.route",
            "project",
            "Route"
        )
        
        assert result == "from kinkotech.rfc_backend.domains.route_plan.models.route_sqlalchemy import Route"
    
    def test_mixed_project_and_third_party(self):
        """Test generating imports for both project and third-party models"""
        generator = ImportPathGenerator(
            third_party_dir="third",
            target_framework="sqlalchemy"
        )
        
        # Project model
        project_import = generator.generate(
            "kinkotech.common.models.base",
            "project",
            "BaseModel"
        )
        
        # Third-party model
        third_party_import = generator.generate(
            "django.contrib.auth.models",
            "third-party",
            "AbstractUser"
        )
        
        assert project_import == "from kinkotech.common.models.base_sqlalchemy import BaseModel"
        assert third_party_import == "from third.django.contrib.auth.models_sqlalchemy import AbstractUser"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
