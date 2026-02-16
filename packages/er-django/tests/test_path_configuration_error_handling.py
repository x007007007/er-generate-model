"""
Unit tests for PathConfiguration error handling.

These tests verify specific error scenarios and validation behavior.

Feature: field-db-column-and-path-separation
Requirements: 3.8, 5.2, 5.3, 5.4, 5.5
"""
import pytest
from pathlib import Path
from x007007007.er_django.path_configuration import PathConfiguration


class TestScanPathValidation:
    """Test scan_path validation errors."""
    
    def test_scan_path_does_not_exist_error(self, tmp_path):
        """Test error when scan_path does not exist.
        
        Validates: Requirements 3.8, 5.2
        """
        # Create a path that doesn't exist
        non_existent_path = tmp_path / "does_not_exist"
        
        # Create configuration with non-existent scan_path
        config = PathConfiguration.from_options(
            scan_path=str(non_existent_path),
            working_dir=tmp_path
        )
        
        # Validate and check for error
        errors = config.validate()
        
        assert len(errors) == 1, f"Expected 1 error, got {len(errors)}"
        assert "Scan path does not exist" in errors[0], \
            f"Expected 'Scan path does not exist' in error, got: {errors[0]}"
        assert str(non_existent_path) in errors[0], \
            f"Expected path '{non_existent_path}' in error message"
    
    def test_scan_path_exists_no_error(self, tmp_path):
        """Test no error when scan_path exists.
        
        Validates: Requirements 3.8
        """
        # Create a directory that exists
        existing_path = tmp_path / "existing_dir"
        existing_path.mkdir()
        
        # Create configuration with existing scan_path
        config = PathConfiguration.from_options(
            scan_path=str(existing_path),
            working_dir=tmp_path
        )
        
        # Validate and check no errors
        errors = config.validate()
        
        assert len(errors) == 0, f"Expected no errors, got: {errors}"


class TestPackagePrefixValidation:
    """Test package prefix validation errors."""
    
    def test_invalid_package_prefix_error(self, tmp_path):
        """Test error when package prefix is not a valid Python identifier.
        
        Validates: Requirements 5.4
        """
        # Create scan_path that exists
        scan_path = tmp_path / "src"
        scan_path.mkdir()
        
        # Create configuration with invalid package prefix
        config = PathConfiguration.from_options(
            scan_path=str(scan_path),
            third_party_package_prefix="123-invalid",  # Invalid identifier
            working_dir=tmp_path
        )
        
        # Validate and check for error
        errors = config.validate()
        
        assert len(errors) == 1, f"Expected 1 error, got {len(errors)}"
        assert "Invalid package prefix" in errors[0], \
            f"Expected 'Invalid package prefix' in error, got: {errors[0]}"
        assert "123-invalid" in errors[0], \
            f"Expected '123-invalid' in error message"
        assert "valid Python identifier" in errors[0], \
            f"Expected 'valid Python identifier' in error message"
    
    def test_valid_package_prefix_no_error(self, tmp_path):
        """Test no error when package prefix is valid.
        
        Validates: Requirements 5.4
        """
        # Create scan_path that exists
        scan_path = tmp_path / "src"
        scan_path.mkdir()
        
        # Create configuration with valid package prefix
        config = PathConfiguration.from_options(
            scan_path=str(scan_path),
            third_party_package_prefix="valid_prefix",
            working_dir=tmp_path
        )
        
        # Validate and check no errors
        errors = config.validate()
        
        assert len(errors) == 0, f"Expected no errors, got: {errors}"
    
    def test_package_prefix_with_hyphen_error(self, tmp_path):
        """Test error when package prefix contains hyphen.
        
        Validates: Requirements 5.4
        """
        # Create scan_path that exists
        scan_path = tmp_path / "src"
        scan_path.mkdir()
        
        # Create configuration with hyphenated prefix
        config = PathConfiguration.from_options(
            scan_path=str(scan_path),
            third_party_package_prefix="my-prefix",
            working_dir=tmp_path
        )
        
        # Validate and check for error
        errors = config.validate()
        
        assert len(errors) == 1
        assert "Invalid package prefix" in errors[0]
        assert "my-prefix" in errors[0]
    
    def test_package_prefix_with_space_error(self, tmp_path):
        """Test error when package prefix contains space.
        
        Validates: Requirements 5.4
        """
        # Create scan_path that exists
        scan_path = tmp_path / "src"
        scan_path.mkdir()
        
        # Create configuration with space in prefix
        config = PathConfiguration.from_options(
            scan_path=str(scan_path),
            third_party_package_prefix="my prefix",
            working_dir=tmp_path
        )
        
        # Validate and check for error
        errors = config.validate()
        
        assert len(errors) == 1
        assert "Invalid package prefix" in errors[0]
    
    def test_package_prefix_starting_with_number_error(self, tmp_path):
        """Test error when package prefix starts with number.
        
        Validates: Requirements 5.4
        """
        # Create scan_path that exists
        scan_path = tmp_path / "src"
        scan_path.mkdir()
        
        # Create configuration with prefix starting with number
        config = PathConfiguration.from_options(
            scan_path=str(scan_path),
            third_party_package_prefix="3rdparty",
            working_dir=tmp_path
        )
        
        # Validate and check for error
        errors = config.validate()
        
        assert len(errors) == 1
        assert "Invalid package prefix" in errors[0]


class TestMultipleValidationErrors:
    """Test multiple validation errors at once."""
    
    def test_multiple_errors_reported(self, tmp_path):
        """Test that multiple validation errors are all reported.
        
        Validates: Requirements 3.8, 5.4
        """
        # Create configuration with multiple errors
        config = PathConfiguration.from_options(
            scan_path=str(tmp_path / "does_not_exist"),  # Non-existent path
            third_party_package_prefix="invalid-prefix",  # Invalid prefix
            working_dir=tmp_path
        )
        
        # Validate and check for multiple errors
        errors = config.validate()
        
        assert len(errors) == 2, f"Expected 2 errors, got {len(errors)}: {errors}"
        
        # Check both error types are present
        error_text = " ".join(errors)
        assert "Scan path does not exist" in error_text
        assert "Invalid package prefix" in error_text


class TestConfigurationTypeErrors:
    """Test configuration parameter type errors.
    
    Note: Type errors are typically caught by Python's type system at runtime,
    but we test the behavior when incorrect types are passed.
    """
    
    def test_none_package_prefix_is_valid(self, tmp_path):
        """Test that None package prefix is valid (uses default).
        
        Validates: Requirements 5.5
        """
        # Create scan_path that exists
        scan_path = tmp_path / "src"
        scan_path.mkdir()
        
        # Create configuration with None prefix (should use default)
        config = PathConfiguration.from_options(
            scan_path=str(scan_path),
            third_party_package_prefix=None,
            working_dir=tmp_path
        )
        
        # Validate and check no errors
        errors = config.validate()
        
        assert len(errors) == 0, f"Expected no errors, got: {errors}"
        # Verify default prefix is used
        assert config.third_party_package_prefix == "third"
    
    def test_empty_string_package_prefix_is_valid(self, tmp_path):
        """Test that empty string package prefix is treated as no prefix.
        
        Empty string is falsy, so validation skips it (treated as None).
        This is acceptable behavior since empty string means "no prefix".
        
        Validates: Requirements 5.5
        """
        # Create scan_path that exists
        scan_path = tmp_path / "src"
        scan_path.mkdir()
        
        # Create configuration with empty string prefix
        config = PathConfiguration.from_options(
            scan_path=str(scan_path),
            third_party_package_prefix="",
            working_dir=tmp_path
        )
        
        # Validate - empty string is treated as falsy, so no validation error
        errors = config.validate()
        
        assert len(errors) == 0, f"Expected no errors for empty string prefix, got: {errors}"
        # Empty string is preserved (not replaced with default)
        assert config.third_party_package_prefix == ""


class TestPathResolutionEdgeCases:
    """Test edge cases in path resolution."""
    
    def test_relative_scan_path_validation(self, tmp_path):
        """Test validation with relative scan_path.
        
        Validates: Requirements 3.8
        """
        # Create a relative path directory
        relative_dir = tmp_path / "relative_src"
        relative_dir.mkdir()
        
        # Create configuration with relative path
        config = PathConfiguration.from_options(
            scan_path="relative_src",
            working_dir=tmp_path
        )
        
        # Validate - should pass since directory exists
        errors = config.validate()
        
        assert len(errors) == 0, f"Expected no errors, got: {errors}"
    
    def test_absolute_scan_path_validation(self, tmp_path):
        """Test validation with absolute scan_path.
        
        Validates: Requirements 3.8
        """
        # Create an absolute path directory
        absolute_dir = tmp_path / "absolute_src"
        absolute_dir.mkdir()
        
        # Create configuration with absolute path
        config = PathConfiguration.from_options(
            scan_path=str(absolute_dir),
            working_dir=tmp_path
        )
        
        # Validate - should pass since directory exists
        errors = config.validate()
        
        assert len(errors) == 0, f"Expected no errors, got: {errors}"
