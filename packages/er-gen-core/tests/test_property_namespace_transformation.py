"""
Property-based tests for namespace transformation.

These tests use hypothesis to verify universal properties across many generated inputs.
Each test runs a minimum of 100 iterations.
"""
import pytest
from hypothesis import given, settings, strategies as st, HealthCheck
from x007007007.er.namespace import NamespaceTransformer


# Custom strategies for generating valid package paths
import keyword

valid_identifier = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(
    lambda s: len(s) > 0 and len(s) < 30 and not s.startswith('_') and not keyword.iskeyword(s)
)

@st.composite
def valid_package_path(draw, min_components=1, max_components=5):
    """
    Generate a valid Python package path.
    
    Returns a package path like "kinkotech.common.models.base"
    """
    num_components = draw(st.integers(min_value=min_components, max_value=max_components))
    components = [draw(valid_identifier) for _ in range(num_components)]
    return '.'.join(components)


@st.composite
def package_without_suffix(draw):
    """
    Generate a package path that doesn't have _sqlalchemy suffix.
    """
    package = draw(valid_package_path())
    # Ensure it doesn't end with _sqlalchemy
    while package.endswith('_sqlalchemy'):
        package = draw(valid_package_path())
    return package


class TestProperty1NamespaceTransformationIdempotence:
    """
    Property 1: Namespace Transformation Idempotence
    
    **Validates: Requirements 1.2, 1.3**
    
    For any valid package path, transforming it twice should produce the same
    result as transforming it once. This ensures the transformation is idempotent.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(valid_package_path())
    def test_transformation_is_idempotent(self, package):
        """
        Test that transform(transform(x)) == transform(x) for all valid packages.
        
        This verifies Requirement 1.3: WHEN transformation is applied twice to
        the same package, THE Namespace_Transformer SHALL return the same result
        (idempotence).
        """
        transformer = NamespaceTransformer()
        
        # Apply transformation once
        first_transform = transformer.transform_package_to_export_path(package)
        
        # Apply transformation twice
        second_transform = transformer.transform_package_to_export_path(first_transform)
        
        # Property: Second transformation should equal first transformation
        assert first_transform == second_transform, (
            f"Transformation is not idempotent:\n"
            f"  Original: {package}\n"
            f"  First transform: {first_transform}\n"
            f"  Second transform: {second_transform}\n"
            f"Expected first_transform == second_transform"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(valid_package_path())
    def test_already_transformed_packages_unchanged(self, package):
        """
        Test that packages already ending with _sqlalchemy are returned unchanged.
        
        This verifies Requirement 1.2: WHEN a package path already has the
        _sqlalchemy suffix, THE Namespace_Transformer SHALL return it unchanged.
        """
        transformer = NamespaceTransformer()
        
        # First, transform the package to ensure it has the suffix
        transformed = transformer.transform_package_to_export_path(package)
        
        # Now transform the already-transformed package
        result = transformer.transform_package_to_export_path(transformed)
        
        # Property: Should return the same value
        assert result == transformed, (
            f"Already-transformed package was modified:\n"
            f"  Original: {package}\n"
            f"  Transformed: {transformed}\n"
            f"  Re-transformed: {result}\n"
            f"Expected result == transformed"
        )
        
        # Additional check: Should end with _sqlalchemy
        assert result.endswith('_sqlalchemy'), (
            f"Result should end with '_sqlalchemy': {result}"
        )


class TestProperty2NamespaceTransformationSuffixApplication:
    """
    Property 2: Namespace Transformation Suffix Application
    
    **Validates: Requirements 1.1, 1.4**
    
    For any valid package path without the _sqlalchemy suffix, transformation
    should append the suffix to the last component only.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(package_without_suffix())
    def test_suffix_appended_to_last_component(self, package):
        """
        Test that _sqlalchemy suffix is appended to the last component only.
        
        This verifies Requirement 1.1: WHEN a Django package path is provided,
        THE Namespace_Transformer SHALL append `_sqlalchemy` suffix to the last
        component.
        """
        transformer = NamespaceTransformer()
        
        # Transform the package
        result = transformer.transform_package_to_export_path(package)
        
        # Property: Result should end with _sqlalchemy
        assert result.endswith('_sqlalchemy'), (
            f"Transformed package should end with '_sqlalchemy':\n"
            f"  Original: {package}\n"
            f"  Result: {result}"
        )
        
        # Property: Only the last component should have the suffix
        original_components = package.split('.')
        result_components = result.split('.')
        
        # Should have the same number of components
        assert len(original_components) == len(result_components), (
            f"Number of components changed:\n"
            f"  Original: {package} ({len(original_components)} components)\n"
            f"  Result: {result} ({len(result_components)} components)"
        )
        
        # All components except the last should be unchanged
        for i in range(len(original_components) - 1):
            assert original_components[i] == result_components[i], (
                f"Component {i} was modified:\n"
                f"  Original: {original_components[i]}\n"
                f"  Result: {result_components[i]}"
            )
        
        # Last component should have suffix appended
        expected_last = original_components[-1] + '_sqlalchemy'
        assert result_components[-1] == expected_last, (
            f"Last component not correctly transformed:\n"
            f"  Original last: {original_components[-1]}\n"
            f"  Expected: {expected_last}\n"
            f"  Got: {result_components[-1]}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(package_without_suffix())
    def test_all_components_except_last_preserved(self, package):
        """
        Test that all package components except the last are preserved unchanged.
        
        This verifies Requirement 1.4: THE Namespace_Transformer SHALL preserve
        all package components except the last one.
        """
        transformer = NamespaceTransformer()
        
        # Transform the package
        result = transformer.transform_package_to_export_path(package)
        
        # Split into components
        original_components = package.split('.')
        result_components = result.split('.')
        
        # Property: All components except last should be identical
        if len(original_components) > 1:
            original_prefix = '.'.join(original_components[:-1])
            result_prefix = '.'.join(result_components[:-1])
            
            assert original_prefix == result_prefix, (
                f"Package prefix was modified:\n"
                f"  Original prefix: {original_prefix}\n"
                f"  Result prefix: {result_prefix}\n"
                f"  Full original: {package}\n"
                f"  Full result: {result}"
            )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(valid_package_path(min_components=1, max_components=1))
    def test_single_component_package_transformation(self, package):
        """
        Test that single-component packages are correctly transformed.
        
        This verifies that the transformation works correctly even for packages
        with only one component.
        """
        transformer = NamespaceTransformer()
        
        # Transform the package
        result = transformer.transform_package_to_export_path(package)
        
        # Property: Result should be original + _sqlalchemy
        expected = package + '_sqlalchemy'
        assert result == expected, (
            f"Single-component package not correctly transformed:\n"
            f"  Original: {package}\n"
            f"  Expected: {expected}\n"
            f"  Got: {result}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        package=package_without_suffix(),
        framework=st.sampled_from(['sqlalchemy', 'django'])
    )
    def test_framework_specific_suffix_application(self, package, framework):
        """
        Test that the correct suffix is applied based on the framework parameter.
        
        This verifies that the transformation correctly handles different
        framework suffixes.
        """
        transformer = NamespaceTransformer()
        
        # Transform with specified framework
        result = transformer.transform_package_to_export_path(package, framework)
        
        # Determine expected suffix
        expected_suffix = f'_{framework}'
        
        # Property: Result should end with the framework-specific suffix
        assert result.endswith(expected_suffix), (
            f"Result should end with '{expected_suffix}':\n"
            f"  Original: {package}\n"
            f"  Framework: {framework}\n"
            f"  Result: {result}"
        )
        
        # Property: Last component should have the suffix
        components = result.split('.')
        assert components[-1].endswith(expected_suffix), (
            f"Last component should end with '{expected_suffix}':\n"
            f"  Last component: {components[-1]}"
        )
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(valid_package_path())
    def test_transformation_produces_valid_package_path(self, package):
        """
        Test that the transformation always produces a valid Python package path.
        
        This verifies that the result is a valid package path with valid
        identifiers separated by dots.
        """
        transformer = NamespaceTransformer()
        
        # Transform the package
        result = transformer.transform_package_to_export_path(package)
        
        # Property: Result should be a non-empty string
        assert result, "Result should be non-empty"
        
        # Property: Result should contain dots (if original had multiple components)
        if '.' in package:
            assert '.' in result, "Result should contain dots for multi-component packages"
        
        # Property: All components should be valid identifiers
        components = result.split('.')
        for comp in components:
            assert comp.isidentifier(), (
                f"Component '{comp}' is not a valid Python identifier in result: {result}"
            )
        
        # Property: Should not have empty components
        assert all(comp for comp in components), (
            f"Result contains empty components: {result}"
        )
