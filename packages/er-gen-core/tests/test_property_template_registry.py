"""
Property-based tests for template registry.

These tests use hypothesis to verify universal properties across many generated inputs.
Each test runs a minimum of 100 iterations.
"""
import pytest
import tempfile
import os
from pathlib import Path
from hypothesis import given, settings, strategies as st, HealthCheck, assume
from x007007007.er.template_registry import (
    TemplateRegistry,
    ConflictError,
    ValidationError
)


# Custom strategies for generating valid package paths and template data
# Python keywords that should be excluded from identifiers
PYTHON_KEYWORDS = {
    'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break',
    'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally',
    'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal',
    'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield'
}

valid_identifier = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(
    lambda s: len(s) > 0 and len(s) < 30 and not s.startswith('_') and s not in PYTHON_KEYWORDS
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
def valid_template_name(draw):
    """Generate a valid Python identifier for template name."""
    # Start with letter, can contain letters, numbers, underscores
    first_char = draw(st.sampled_from('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
    rest = draw(st.text(
        alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_',
        min_size=0,
        max_size=20
    ))
    return first_char + rest


@st.composite
def valid_column_data(draw):
    """Generate valid column data for a template."""
    name = draw(valid_identifier)
    col_type = draw(st.sampled_from(['string', 'integer', 'bigint', 'datetime', 'boolean', 'text']))
    
    column = {
        'name': name,
        'type': col_type
    }
    
    # Optionally add other fields
    if draw(st.booleans()):
        column['primary_key'] = draw(st.booleans())
    if draw(st.booleans()):
        column['nullable'] = draw(st.booleans())
    
    return column


@st.composite
def template_with_package(draw):
    """Generate a template definition with package field."""
    template_name = draw(valid_template_name())
    package = draw(valid_package_path())
    num_columns = draw(st.integers(min_value=1, max_value=5))
    columns = [draw(valid_column_data()) for _ in range(num_columns)]
    
    return {
        'name': template_name,
        'package': package,
        'columns': columns
    }


@st.composite
def template_with_export_path(draw):
    """Generate a template definition with explicit export_path."""
    template_name = draw(valid_template_name())
    package = draw(valid_package_path())
    export_path = draw(valid_package_path())
    num_columns = draw(st.integers(min_value=1, max_value=5))
    columns = [draw(valid_column_data()) for _ in range(num_columns)]
    
    return {
        'name': template_name,
        'package': package,
        'export_path': export_path,
        'columns': columns
    }


def create_toml_file(templates_data):
    """
    Create a temporary TOML file with the given templates data.
    
    Args:
        templates_data: List of template dictionaries
        
    Returns:
        Path to the created temporary file
    """
    content = ""
    for template in templates_data:
        content += f"\n[templates.{template['name']}]\n"
        if 'package' in template:
            content += f'package = "{template["package"]}"\n'
        if 'export_path' in template:
            content += f'export_path = "{template["export_path"]}"\n'
        
        for column in template['columns']:
            content += f"\n[[templates.{template['name']}.columns]]\n"
            content += f'name = "{column["name"]}"\n'
            content += f'type = "{column["type"]}"\n'
            if 'primary_key' in column:
                content += f'primary_key = {str(column["primary_key"]).lower()}\n'
            if 'nullable' in column:
                content += f'nullable = {str(column["nullable"]).lower()}\n'
    
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False)
    f.write(content)
    f.flush()
    f.close()
    return f.name


class TestProperty3TemplateDiscoveryCompleteness:
    """
    Property 3: Template Discovery Completeness
    
    **Validates: Requirements 2.1**
    
    For any set of TOML files with templates, all templates from all files
    should be discovered and registered.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        st.lists(
            st.lists(template_with_package(), min_size=1, max_size=3),
            min_size=1,
            max_size=3
        )
    )
    def test_all_templates_discovered_from_multiple_files(self, files_templates):
        """
        Test that all templates from all TOML files are discovered.
        
        This verifies Requirement 2.1: WHEN multiple TOML files are provided,
        THE Template_Registry SHALL discover all templates from all files.
        """
        # Ensure unique template names across all files
        all_names = []
        for file_templates in files_templates:
            for template in file_templates:
                all_names.append(template['name'])
        
        # Skip if there are duplicates (that's tested separately)
        if len(all_names) != len(set(all_names)):
            assume(False)
        
        # Create temporary TOML files
        temp_files = []
        try:
            for file_templates in files_templates:
                temp_file = create_toml_file(file_templates)
                temp_files.append(temp_file)
            
            # Discover templates
            registry = TemplateRegistry()
            discovered = registry.discover_templates(temp_files)
            
            # Property: All templates should be discovered
            expected_count = sum(len(file_templates) for file_templates in files_templates)
            assert len(discovered) == expected_count, (
                f"Not all templates were discovered:\n"
                f"  Expected: {expected_count} templates\n"
                f"  Got: {len(discovered)} templates\n"
                f"  Discovered names: {list(discovered.keys())}"
            )
            
            # Property: Each template should be in the registry
            for file_templates in files_templates:
                for template in file_templates:
                    assert template['name'] in discovered, (
                        f"Template '{template['name']}' was not discovered"
                    )
                    
                    # Verify template data
                    discovered_template = discovered[template['name']]
                    assert discovered_template.name == template['name']
                    assert len(discovered_template.columns) == len(template['columns'])
        
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(st.lists(template_with_package(), min_size=1, max_size=5, unique_by=lambda t: t['name']))
    def test_single_file_template_count_matches(self, templates):
        """
        Test that the number of discovered templates matches the number in the file.
        
        This verifies that template discovery is complete for a single file.
        """
        temp_file = None
        try:
            temp_file = create_toml_file(templates)
            
            registry = TemplateRegistry()
            discovered = registry.discover_templates([temp_file])
            
            # Property: Count should match
            assert len(discovered) == len(templates), (
                f"Template count mismatch:\n"
                f"  Expected: {len(templates)}\n"
                f"  Got: {len(discovered)}"
            )
        
        finally:
            if temp_file:
                try:
                    os.unlink(temp_file)
                except:
                    pass


class TestProperty4ExportPathAutoDerivation:
    """
    Property 4: Export Path Auto-Derivation
    
    **Validates: Requirements 2.2**
    
    For any template with a package field but no export_path field, the export_path
    should be auto-derived by applying namespace transformation to the package.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(template_with_package())
    def test_export_path_auto_derived_from_package(self, template):
        """
        Test that export_path is auto-derived when only package is specified.
        
        This verifies Requirement 2.2: WHEN a template has a package but no
        export_path, THE Template_Registry SHALL auto-derive the export_path
        using namespace transformation.
        """
        temp_file = None
        try:
            temp_file = create_toml_file([template])
            
            registry = TemplateRegistry()
            discovered = registry.discover_templates([temp_file])
            
            template_info = discovered[template['name']]
            
            # Property: export_path should be set
            assert template_info.export_path is not None, (
                f"export_path was not auto-derived for template '{template['name']}'"
            )
            
            # Property: export_path should end with _sqlalchemy
            assert template_info.export_path.endswith('_sqlalchemy'), (
                f"Auto-derived export_path should end with '_sqlalchemy':\n"
                f"  Package: {template['package']}\n"
                f"  Export path: {template_info.export_path}"
            )
            
            # Property: export_path should be based on package
            expected_export_path = template['package'] + '_sqlalchemy'
            assert template_info.export_path == expected_export_path, (
                f"Auto-derived export_path doesn't match expected:\n"
                f"  Package: {template['package']}\n"
                f"  Expected: {expected_export_path}\n"
                f"  Got: {template_info.export_path}"
            )
        
        finally:
            if temp_file:
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(template_with_package())
    def test_auto_derived_export_path_is_valid_package_path(self, template):
        """
        Test that auto-derived export_path is a valid Python package path.
        
        This verifies that the auto-derivation produces valid package paths.
        """
        temp_file = None
        try:
            temp_file = create_toml_file([template])
            
            registry = TemplateRegistry()
            discovered = registry.discover_templates([temp_file])
            
            template_info = discovered[template['name']]
            export_path = template_info.export_path
            
            # Property: export_path should be non-empty
            assert export_path, "Auto-derived export_path should be non-empty"
            
            # Property: All components should be valid identifiers
            components = export_path.split('.')
            for comp in components:
                assert comp.isidentifier(), (
                    f"Component '{comp}' in auto-derived export_path is not a valid identifier:\n"
                    f"  Export path: {export_path}"
                )
        
        finally:
            if temp_file:
                try:
                    os.unlink(temp_file)
                except:
                    pass


class TestProperty5ExportPathPrecedence:
    """
    Property 5: Export Path Precedence
    
    **Validates: Requirements 2.3**
    
    For any template with both package and export_path fields, the explicit
    export_path should be used unchanged.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(template_with_export_path())
    def test_explicit_export_path_takes_precedence(self, template):
        """
        Test that explicit export_path is used when both package and export_path are specified.
        
        This verifies Requirement 2.3: WHEN a template has both package and
        export_path, THE Template_Registry SHALL use the explicit export_path.
        """
        temp_file = None
        try:
            temp_file = create_toml_file([template])
            
            registry = TemplateRegistry()
            discovered = registry.discover_templates([temp_file])
            
            template_info = discovered[template['name']]
            
            # Property: export_path should match the explicit value
            assert template_info.export_path == template['export_path'], (
                f"Explicit export_path was not used:\n"
                f"  Expected: {template['export_path']}\n"
                f"  Got: {template_info.export_path}\n"
                f"  Package: {template['package']}"
            )
            
            # Property: export_path should NOT be auto-derived from package
            auto_derived = template['package'] + '_sqlalchemy'
            if template['export_path'] != auto_derived:
                assert template_info.export_path != auto_derived, (
                    f"export_path was auto-derived instead of using explicit value:\n"
                    f"  Explicit: {template['export_path']}\n"
                    f"  Auto-derived: {auto_derived}\n"
                    f"  Got: {template_info.export_path}"
                )
        
        finally:
            if temp_file:
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(template_with_export_path())
    def test_explicit_export_path_unchanged(self, template):
        """
        Test that explicit export_path is stored exactly as specified.
        
        This verifies that no transformation is applied to explicit export_path.
        """
        temp_file = None
        try:
            temp_file = create_toml_file([template])
            
            registry = TemplateRegistry()
            discovered = registry.discover_templates([temp_file])
            
            template_info = discovered[template['name']]
            
            # Property: export_path should be exactly as specified
            assert template_info.export_path == template['export_path'], (
                f"Explicit export_path was modified:\n"
                f"  Original: {template['export_path']}\n"
                f"  Stored: {template_info.export_path}"
            )
        
        finally:
            if temp_file:
                try:
                    os.unlink(temp_file)
                except:
                    pass


class TestProperty6TemplateResolutionAcrossFiles:
    """
    Property 6: Template Resolution Across Files
    
    **Validates: Requirements 3.1, 8.1**
    
    For any template name in the registry, it should be resolvable regardless
    of which TOML file defined it.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        st.lists(
            st.lists(template_with_package(), min_size=1, max_size=2),
            min_size=2,
            max_size=3
        )
    )
    def test_templates_resolvable_across_files(self, files_templates):
        """
        Test that templates can be resolved regardless of which file defined them.
        
        This verifies Requirement 3.1: WHEN an entity references a template by name,
        THE Template_Registry SHALL resolve it from any loaded TOML file.
        
        Also verifies Requirement 8.1: WHEN an entity in file A references a
        template defined in file B, THE Template_Registry SHALL resolve the
        template successfully.
        """
        # Ensure unique template names across all files
        all_names = []
        for file_templates in files_templates:
            for template in file_templates:
                all_names.append(template['name'])
        
        # Skip if there are duplicates
        if len(all_names) != len(set(all_names)):
            assume(False)
        
        temp_files = []
        try:
            # Create temporary TOML files
            for file_templates in files_templates:
                temp_file = create_toml_file(file_templates)
                temp_files.append(temp_file)
            
            # Discover templates
            registry = TemplateRegistry()
            registry.discover_templates(temp_files)
            
            # Property: All templates should be resolvable
            for file_templates in files_templates:
                for template in file_templates:
                    resolved = registry.resolve_template(template['name'])
                    
                    assert resolved is not None, (
                        f"Template '{template['name']}' could not be resolved"
                    )
                    
                    assert resolved.name == template['name'], (
                        f"Resolved template has wrong name:\n"
                        f"  Expected: {template['name']}\n"
                        f"  Got: {resolved.name}"
                    )
        
        finally:
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(st.lists(template_with_package(), min_size=1, max_size=5, unique_by=lambda t: t['name']))
    def test_all_discovered_templates_are_resolvable(self, templates):
        """
        Test that every discovered template can be resolved by name.
        
        This verifies that the resolution mechanism works for all templates.
        """
        temp_file = None
        try:
            temp_file = create_toml_file(templates)
            
            registry = TemplateRegistry()
            discovered = registry.discover_templates([temp_file])
            
            # Property: Every discovered template should be resolvable
            for template_name in discovered.keys():
                resolved = registry.resolve_template(template_name)
                
                assert resolved is not None, (
                    f"Discovered template '{template_name}' could not be resolved"
                )
                
                assert resolved.name == template_name, (
                    f"Resolved template name mismatch:\n"
                    f"  Expected: {template_name}\n"
                    f"  Got: {resolved.name}"
                )
        
        finally:
            if temp_file:
                try:
                    os.unlink(temp_file)
                except:
                    pass


class TestProperty7RegistryCompletenessInvariant:
    """
    Property 7: Registry Completeness Invariant
    
    **Validates: Requirements 3.3, 3.4**
    
    For any completed template discovery, all templates in the registry should
    have valid, non-null export paths.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(st.lists(template_with_package(), min_size=1, max_size=5, unique_by=lambda t: t['name']))
    def test_all_templates_have_export_path(self, templates):
        """
        Test that all discovered templates have non-null export_path.
        
        This verifies Requirement 3.3: THE Template_Registry SHALL maintain a
        unified registry of all templates across files.
        
        Also verifies Requirement 3.4: WHEN templates are discovered, THE
        Template_Registry SHALL validate that all have valid export paths.
        """
        temp_file = None
        try:
            temp_file = create_toml_file(templates)
            
            registry = TemplateRegistry()
            discovered = registry.discover_templates([temp_file])
            
            # Property: All templates should have export_path
            for template_name, template_info in discovered.items():
                assert template_info.export_path is not None, (
                    f"Template '{template_name}' has null export_path"
                )
                
                assert template_info.export_path, (
                    f"Template '{template_name}' has empty export_path"
                )
        
        finally:
            if temp_file:
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(st.lists(template_with_package(), min_size=1, max_size=5, unique_by=lambda t: t['name']))
    def test_all_export_paths_are_valid_package_paths(self, templates):
        """
        Test that all export_path values are valid Python package paths.
        
        This verifies that the registry maintains valid export paths for all templates.
        """
        temp_file = None
        try:
            temp_file = create_toml_file(templates)
            
            registry = TemplateRegistry()
            discovered = registry.discover_templates([temp_file])
            
            # Property: All export_path values should be valid package paths
            for template_name, template_info in discovered.items():
                export_path = template_info.export_path
                
                # Should be non-empty
                assert export_path, (
                    f"Template '{template_name}' has empty export_path"
                )
                
                # All components should be valid identifiers
                components = export_path.split('.')
                for comp in components:
                    assert comp.isidentifier(), (
                        f"Template '{template_name}' has invalid export_path component '{comp}':\n"
                        f"  Export path: {export_path}"
                    )
                
                # Should not have empty components
                assert all(comp for comp in components), (
                    f"Template '{template_name}' has empty components in export_path: {export_path}"
                )
        
        finally:
            if temp_file:
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        st.lists(
            st.lists(template_with_package(), min_size=1, max_size=2),
            min_size=1,
            max_size=3
        )
    )
    def test_registry_completeness_across_multiple_files(self, files_templates):
        """
        Test that registry completeness holds across multiple files.
        
        This verifies that the invariant holds even when templates come from
        multiple TOML files.
        """
        # Ensure unique template names
        all_names = []
        for file_templates in files_templates:
            for template in file_templates:
                all_names.append(template['name'])
        
        if len(all_names) != len(set(all_names)):
            assume(False)
        
        temp_files = []
        try:
            for file_templates in files_templates:
                temp_file = create_toml_file(file_templates)
                temp_files.append(temp_file)
            
            registry = TemplateRegistry()
            discovered = registry.discover_templates(temp_files)
            
            # Property: All templates should have valid export_path
            for template_name, template_info in discovered.items():
                assert template_info.export_path is not None, (
                    f"Template '{template_name}' has null export_path"
                )
                
                assert template_info.export_path, (
                    f"Template '{template_name}' has empty export_path"
                )
                
                # Validate it's a valid package path
                components = template_info.export_path.split('.')
                for comp in components:
                    assert comp.isidentifier(), (
                        f"Template '{template_name}' has invalid export_path: {template_info.export_path}"
                    )
        
        finally:
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
