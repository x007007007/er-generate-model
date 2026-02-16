"""Unit tests for PathConfiguration class."""

import pytest
from pathlib import Path
from x007007007.er_django.path_configuration import PathConfiguration


class TestPathConfigurationBasics:
    """Test basic PathConfiguration functionality."""
    
    def test_from_options_with_defaults(self, tmp_path):
        """Test PathConfiguration with all default values."""
        # Create a src directory for validation
        src_dir = tmp_path / 'src'
        src_dir.mkdir()
        
        config = PathConfiguration.from_options(working_dir=tmp_path)
        
        assert config.scan_path == tmp_path / 'src'
        assert config.output_path == tmp_path / 'src'
        assert config.third_party_output_path == tmp_path / 'src' / 'third'
        assert config.third_party_package_prefix == 'third'
    
    def test_from_options_with_scan_path_only(self, tmp_path):
        """Test PathConfiguration with only scan_path specified."""
        # Create a custom directory for validation
        custom_dir = tmp_path / 'custom'
        custom_dir.mkdir()
        
        config = PathConfiguration.from_options(
            scan_path='custom',
            working_dir=tmp_path
        )
        
        assert config.scan_path == tmp_path / 'custom'
        assert config.output_path == tmp_path / 'custom'
        assert config.third_party_output_path == tmp_path / 'custom' / 'third'
        assert config.third_party_package_prefix == 'third'
    
    def test_from_options_with_scan_and_output_path(self, tmp_path):
        """Test PathConfiguration with scan_path and output_path specified."""
        # Create directories for validation
        scan_dir = tmp_path / 'scan'
        output_dir = tmp_path / 'output'
        scan_dir.mkdir()
        output_dir.mkdir()
        
        config = PathConfiguration.from_options(
            scan_path='scan',
            output_path='output',
            working_dir=tmp_path
        )
        
        assert config.scan_path == tmp_path / 'scan'
        assert config.output_path == tmp_path / 'output'
        assert config.third_party_output_path == tmp_path / 'output' / 'third'
        assert config.third_party_package_prefix == 'third'
    
    def test_from_options_with_all_paths(self, tmp_path):
        """Test PathConfiguration with all paths specified."""
        # Create directories for validation
        scan_dir = tmp_path / 'scan'
        output_dir = tmp_path / 'output'
        third_dir = tmp_path / 'third_party'
        scan_dir.mkdir()
        output_dir.mkdir()
        third_dir.mkdir()
        
        config = PathConfiguration.from_options(
            scan_path='scan',
            output_path='output',
            third_party_output_path=str(third_dir),
            working_dir=tmp_path
        )
        
        assert config.scan_path == tmp_path / 'scan'
        assert config.output_path == tmp_path / 'output'
        assert config.third_party_output_path == third_dir
        assert config.third_party_package_prefix == 'third_party'
    
    def test_from_options_with_custom_prefix(self, tmp_path):
        """Test PathConfiguration with custom package prefix."""
        # Create a src directory for validation
        src_dir = tmp_path / 'src'
        src_dir.mkdir()
        
        config = PathConfiguration.from_options(
            third_party_package_prefix='external',
            working_dir=tmp_path
        )
        
        assert config.third_party_package_prefix == 'external'
    
    def test_from_options_relative_third_party_path(self, tmp_path):
        """Test that relative third_party_output_path is resolved relative to output_path."""
        # Create directories for validation
        src_dir = tmp_path / 'src'
        src_dir.mkdir()
        
        config = PathConfiguration.from_options(
            third_party_output_path='external',
            working_dir=tmp_path
        )
        
        # Relative path should be resolved relative to output_path (which defaults to src)
        assert config.third_party_output_path == tmp_path / 'src' / 'external'
        assert config.third_party_package_prefix == 'external'
    
    def test_from_options_absolute_paths(self, tmp_path):
        """Test PathConfiguration with absolute paths."""
        # Create directories for validation
        scan_dir = tmp_path / 'scan'
        output_dir = tmp_path / 'output'
        scan_dir.mkdir()
        output_dir.mkdir()
        
        config = PathConfiguration.from_options(
            scan_path=str(scan_dir),
            output_path=str(output_dir),
            working_dir=tmp_path
        )
        
        assert config.scan_path == scan_dir
        assert config.output_path == output_dir


class TestPathConfigurationValidation:
    """Test PathConfiguration validation."""
    
    def test_validate_success(self, tmp_path):
        """Test validation passes with valid configuration."""
        # Create a src directory for validation
        src_dir = tmp_path / 'src'
        src_dir.mkdir()
        
        config = PathConfiguration.from_options(working_dir=tmp_path)
        errors = config.validate()
        
        assert errors == []
    
    def test_validate_scan_path_not_exists(self, tmp_path):
        """Test validation fails when scan_path does not exist."""
        config = PathConfiguration.from_options(
            scan_path='nonexistent',
            working_dir=tmp_path
        )
        errors = config.validate()
        
        assert len(errors) == 1
        assert 'Scan path does not exist' in errors[0]
        assert 'nonexistent' in errors[0]
    
    def test_validate_invalid_package_prefix(self, tmp_path):
        """Test validation fails with invalid package prefix."""
        # Create a src directory for validation
        src_dir = tmp_path / 'src'
        src_dir.mkdir()
        
        config = PathConfiguration.from_options(
            third_party_package_prefix='invalid-prefix',
            working_dir=tmp_path
        )
        errors = config.validate()
        
        assert len(errors) == 1
        assert 'Invalid package prefix' in errors[0]
        assert 'invalid-prefix' in errors[0]
    
    def test_validate_multiple_errors(self, tmp_path):
        """Test validation returns multiple errors."""
        config = PathConfiguration.from_options(
            scan_path='nonexistent',
            third_party_package_prefix='123invalid',
            working_dir=tmp_path
        )
        errors = config.validate()
        
        assert len(errors) == 2
        assert any('Scan path does not exist' in e for e in errors)
        assert any('Invalid package prefix' in e for e in errors)
