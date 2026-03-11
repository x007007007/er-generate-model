"""
Unit Tests for NamespaceTransformer

These tests verify specific examples and edge cases for namespace transformation:
- Simple package transformation
- Already-transformed packages (idempotence)
- Single-component packages
- Invalid package paths

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
"""
import pytest
from x007007007.er.namespace import NamespaceTransformer


class TestSimplePackageTransformation:
    """Test simple package transformation with multiple components."""
    
    def test_multi_component_package_transformation(self):
        """
        Test transformation of a typical multi-component package path.
        
        This verifies that a Django package path like "kinkotech.common.models.base"
        is correctly transformed to "kinkotech.common.models.base_sqlalchemy".
        
        Requirements: 1.1, 1.4
        """
        transformer = NamespaceTransformer()
        package = "kinkotech.common.models.base"
        
        result = transformer.transform_package_to_export_path(package)
        
        assert result == "kinkotech.common.models.base_sqlalchemy", \
            f"Expected 'kinkotech.common.models.base_sqlalchemy', got '{result}'"
    
    def test_two_component_package_transformation(self):
        """
        Test transformation of a two-component package path.
        
        Requirements: 1.1, 1.4
        """
        transformer = NamespaceTransformer()
        package = "myapp.models"
        
        result = transformer.transform_package_to_export_path(package)
        
        assert result == "myapp.models_sqlalchemy", \
            f"Expected 'myapp.models_sqlalchemy', got '{result}'"
    
    def test_deep_nested_package_transformation(self):
        """
        Test transformation of a deeply nested package path.
        
        Requirements: 1.1, 1.4
        """
        transformer = NamespaceTransformer()
        package = "company.division.team.project.module.submodule.models"
        
        result = transformer.transform_package_to_export_path(package)
        
        assert result == "company.division.team.project.module.submodule.models_sqlalchemy", \
            f"Expected suffix appended to last component only"
        
        # Verify all components except last are preserved
        original_components = package.split('.')
        result_components = result.split('.')
        
        assert len(original_components) == len(result_components), \
            "Number of components should remain the same"
        
        for i in range(len(original_components) - 1):
            assert original_components[i] == result_components[i], \
                f"Component {i} should be unchanged: {original_components[i]} != {result_components[i]}"
    
    def test_package_with_underscores(self):
        """
        Test transformation of package with underscores in component names.
        
        Requirements: 1.1, 1.4
        """
        transformer = NamespaceTransformer()
        package = "my_company.common_utils.base_models"
        
        result = transformer.transform_package_to_export_path(package)
        
        assert result == "my_company.common_utils.base_models_sqlalchemy", \
            f"Expected 'my_company.common_utils.base_models_sqlalchemy', got '{result}'"
    
    def test_django_framework_suffix(self):
        """
        Test transformation with django framework suffix.
        
        Requirements: 1.1
        """
        transformer = NamespaceTransformer()
        package = "myapp.models"
        
        result = transformer.transform_package_to_export_path(package, output_framework='django')
        
        assert result == "myapp.models_django", \
            f"Expected 'myapp.models_django', got '{result}'"


class TestAlreadyTransformedPackages:
    """Test that already-transformed packages are returned unchanged (idempotence)."""
    
    def test_sqlalchemy_suffix_already_present(self):
        """
        Test that a package already ending with _sqlalchemy is returned unchanged.
        
        This verifies idempotence: transforming an already-transformed package
        should return the same value.
        
        Requirements: 1.2, 1.3
        """
        transformer = NamespaceTransformer()
        package = "kinkotech.common.models.base_sqlalchemy"
        
        result = transformer.transform_package_to_export_path(package)
        
        assert result == package, \
            f"Already-transformed package should be unchanged: expected '{package}', got '{result}'"
    
    def test_double_transformation_idempotence(self):
        """
        Test that transforming twice produces the same result as transforming once.
        
        Requirements: 1.3
        """
        transformer = NamespaceTransformer()
        package = "myapp.models"
        
        first_transform = transformer.transform_package_to_export_path(package)
        second_transform = transformer.transform_package_to_export_path(first_transform)
        
        assert first_transform == second_transform, \
            f"Double transformation should be idempotent: '{first_transform}' != '{second_transform}'"
        
        assert second_transform == "myapp.models_sqlalchemy", \
            f"Expected 'myapp.models_sqlalchemy', got '{second_transform}'"
    
    def test_django_suffix_already_present(self):
        """
        Test that a package already ending with _django is returned unchanged.
        
        Requirements: 1.2, 1.3
        """
        transformer = NamespaceTransformer()
        package = "myapp.models_django"
        
        result = transformer.transform_package_to_export_path(package, output_framework='django')
        
        assert result == package, \
            f"Already-transformed package should be unchanged: expected '{package}', got '{result}'"


class TestSingleComponentPackages:
    """Test transformation of single-component package paths."""
    
    def test_single_component_transformation(self):
        """
        Test transformation of a package with only one component.
        
        Requirements: 1.1, 1.4
        """
        transformer = NamespaceTransformer()
        package = "models"
        
        result = transformer.transform_package_to_export_path(package)
        
        assert result == "models_sqlalchemy", \
            f"Expected 'models_sqlalchemy', got '{result}'"
    
    def test_single_component_with_underscore(self):
        """
        Test transformation of a single-component package with underscores.
        
        Requirements: 1.1, 1.4
        """
        transformer = NamespaceTransformer()
        package = "base_models"
        
        result = transformer.transform_package_to_export_path(package)
        
        assert result == "base_models_sqlalchemy", \
            f"Expected 'base_models_sqlalchemy', got '{result}'"
    
    def test_single_component_already_transformed(self):
        """
        Test that a single-component package already transformed is unchanged.
        
        Requirements: 1.2, 1.3
        """
        transformer = NamespaceTransformer()
        package = "models_sqlalchemy"
        
        result = transformer.transform_package_to_export_path(package)
        
        assert result == package, \
            f"Already-transformed single-component package should be unchanged"


class TestInvalidPackagePaths:
    """Test error handling for invalid package paths."""
    
    def test_empty_string_raises_error(self):
        """
        Test that an empty string raises ValueError.
        
        Requirements: 1.5
        """
        transformer = NamespaceTransformer()
        
        with pytest.raises(ValueError, match="Package path cannot be empty or None"):
            transformer.transform_package_to_export_path("")
    
    def test_none_raises_error(self):
        """
        Test that None raises ValueError.
        
        Requirements: 1.5
        """
        transformer = NamespaceTransformer()
        
        with pytest.raises(ValueError, match="Package path cannot be empty or None"):
            transformer.transform_package_to_export_path(None)
    
    def test_non_string_raises_error(self):
        """
        Test that non-string input raises ValueError.
        
        Requirements: 1.5
        """
        transformer = NamespaceTransformer()
        
        with pytest.raises(ValueError, match="Package must be a string"):
            transformer.transform_package_to_export_path(123)
    
    def test_package_with_empty_component_raises_error(self):
        """
        Test that a package with empty components raises ValueError.
        
        Requirements: 1.5
        """
        transformer = NamespaceTransformer()
        
        with pytest.raises(ValueError, match="Package path contains empty components"):
            transformer.transform_package_to_export_path("myapp..models")
    
    def test_package_starting_with_dot_raises_error(self):
        """
        Test that a package starting with a dot raises ValueError.
        
        Requirements: 1.5
        """
        transformer = NamespaceTransformer()
        
        with pytest.raises(ValueError, match="Package path contains empty components"):
            transformer.transform_package_to_export_path(".myapp.models")
    
    def test_package_ending_with_dot_raises_error(self):
        """
        Test that a package ending with a dot raises ValueError.
        
        Requirements: 1.5
        """
        transformer = NamespaceTransformer()
        
        with pytest.raises(ValueError, match="Package path contains empty components"):
            transformer.transform_package_to_export_path("myapp.models.")
    
    def test_invalid_identifier_with_hyphen_raises_error(self):
        """
        Test that a package with hyphens raises ValueError.
        
        Requirements: 1.5
        """
        transformer = NamespaceTransformer()
        
        with pytest.raises(ValueError, match="Invalid Python identifier"):
            transformer.transform_package_to_export_path("my-app.models")
    
    def test_invalid_identifier_starting_with_digit_raises_error(self):
        """
        Test that a package component starting with a digit raises ValueError.
        
        Requirements: 1.5
        """
        transformer = NamespaceTransformer()
        
        with pytest.raises(ValueError, match="Invalid Python identifier"):
            transformer.transform_package_to_export_path("myapp.123models")
    
    def test_invalid_identifier_with_spaces_raises_error(self):
        """
        Test that a package with spaces raises ValueError.
        
        Requirements: 1.5
        """
        transformer = NamespaceTransformer()
        
        with pytest.raises(ValueError, match="Invalid Python identifier"):
            transformer.transform_package_to_export_path("my app.models")
    
    def test_python_keyword_as_component_raises_error(self):
        """
        Test that a Python keyword as a component raises ValueError.
        
        Requirements: 1.5
        """
        transformer = NamespaceTransformer()
        
        with pytest.raises(ValueError, match="Invalid Python identifier"):
            transformer.transform_package_to_export_path("myapp.class.models")
    
    def test_unsupported_framework_raises_error(self):
        """
        Test that an unsupported framework raises ValueError.
        
        Requirements: 1.5
        """
        transformer = NamespaceTransformer()
        
        with pytest.raises(ValueError, match="Unsupported framework"):
            transformer.transform_package_to_export_path("myapp.models", output_framework='react')


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_package_with_numbers_in_middle(self):
        """
        Test transformation of package with numbers in component names.
        
        Requirements: 1.1, 1.4
        """
        transformer = NamespaceTransformer()
        package = "myapp.v2.models"
        
        result = transformer.transform_package_to_export_path(package)
        
        assert result == "myapp.v2.models_sqlalchemy", \
            f"Expected 'myapp.v2.models_sqlalchemy', got '{result}'"
    
    def test_package_with_multiple_underscores(self):
        """
        Test transformation of package with multiple consecutive underscores.
        
        Requirements: 1.1, 1.4
        """
        transformer = NamespaceTransformer()
        package = "my__app.models"
        
        result = transformer.transform_package_to_export_path(package)
        
        assert result == "my__app.models_sqlalchemy", \
            f"Expected 'my__app.models_sqlalchemy', got '{result}'"
    
    def test_very_long_package_path(self):
        """
        Test transformation of a very long package path.
        
        Requirements: 1.1, 1.4
        """
        transformer = NamespaceTransformer()
        components = ['component' + str(i) for i in range(20)]
        package = '.'.join(components)
        
        result = transformer.transform_package_to_export_path(package)
        
        expected = package + '_sqlalchemy'
        assert result == expected, \
            f"Long package path not correctly transformed"
        
        # Verify all components except last are preserved
        assert result.count('.') == package.count('.'), \
            "Number of dots should remain the same"
