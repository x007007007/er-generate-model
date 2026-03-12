"""
Bug Condition Exploration Test for Third-Party Library Inheritance Import Fix

**Property 1: Fault Condition - Third-Party Library Inheritance Import and File Generation**

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5**

This test MUST FAIL on unfixed code - failure confirms the bug exists.
DO NOT attempt to fix the test or the code when it fails.

The test encodes the expected behavior - it will validate the fix when it passes after implementation.

GOAL: Surface counterexamples that demonstrate the bug exists - third-party library imports
are missing the `third.` prefix and corresponding files are not generated in the `third/` directory.

Scoped PBT Approach: For deterministic bugs, scope the property to the concrete failing case(s) to ensure reproducibility.
"""
import re
import pytest
import toml
from hypothesis import given, settings, strategies as st, HealthCheck
from x007007007.er.parser.toml_parser import TomlERParser
from x007007007.er.renderers.python.sqlalchemy import SQLAlchemyRenderer


# Custom strategies for generating valid identifiers
safe_identifier = st.from_regex(r'[A-Z][a-zA-Z0-9]*', fullmatch=True).filter(lambda s: len(s) < 50)
safe_column_name = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(lambda s: len(s) < 30)
safe_type = st.sampled_from(['string', 'text', 'bigint', 'int', 'datetime', 'boolean'])


@st.composite
def toml_with_third_party_inheritance(draw):
    """
    Generate TOML data with third-party library inheritance (3+ namespace parts).
    
    This strategy creates:
    - An entity that extends third-party library classes (3+ namespace parts)
    - The entity has its own columns
    
    Returns a tuple of (toml_dict, entity_name, third_party_classes, entity_columns)
    """
    # Generate entity name and columns
    entity_name = draw(safe_identifier)
    num_entity_cols = draw(st.integers(min_value=1, max_value=3))
    
    entity_columns = []
    for i in range(num_entity_cols):
        col_name = draw(safe_column_name.filter(lambda x: x not in [c['name'] for c in entity_columns]))
        col_type = draw(safe_type)
        entity_columns.append({
            'name': col_name,
            'type': col_type,
            'primary_key': i == 0  # First column is PK
        })
    
    # Generate third-party class references (3+ namespace parts)
    num_third_party = draw(st.integers(min_value=1, max_value=2))
    third_party_classes = []
    for i in range(num_third_party):
        class_name = draw(safe_identifier.filter(lambda x: x not in third_party_classes and x != entity_name))
        # Create fully qualified third-party class name (3+ parts)
        # Examples: oauth2_provider.models.AbstractAccessToken, django.contrib.auth.models.AbstractUser
        num_parts = draw(st.integers(min_value=3, max_value=4))
        if num_parts == 3:
            third_party_class = f"package.module.{class_name}"
        else:
            third_party_class = f"package.subpackage.module.{class_name}"
        third_party_classes.append(third_party_class)
    
    # Build TOML structure
    toml_dict = {
        # NO templates section - third-party classes are not defined here
        'entities': {
            entity_name: {
                'extends': third_party_classes,
                'table_name': entity_name.lower(),
                'columns': entity_columns
            }
        }
    }
    
    return toml_dict, entity_name, third_party_classes, entity_columns


class TestProperty1ThirdPartyLibraryInheritanceImportAndFileGeneration:
    """
    Property 1: Fault Condition - Third-Party Library Inheritance Import and File Generation
    
    **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5**
    
    For any entity with third-party library classes (3+ namespace parts) in extends list
    when using reference mode and SQLAlchemy target framework, the generated code SHALL:
    1. Include `third.` prefix in import statements
    2. Generate corresponding files in `third/` directory with class definitions
    
    **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists.
    """
    
    def test_concrete_oauth2_provider_inheritance(self):
        """
        Concrete test case 1: OAuth2 Provider inheritance
        
        Entity extends `oauth2_provider.models.AbstractAccessToken`
        
        Expected behavior:
        - Import statement: `from third.oauth2_provider.models_sqlalchemy import AbstractAccessToken`
        - File generated: `third/oauth2_provider/models_sqlalchemy.py` with `AbstractAccessToken` class
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test FAILS
        - Import statement will be: `from oauth2_provider.models_sqlalchemy import AbstractAccessToken` (missing `third.` prefix)
        - File will NOT be generated in `third/` directory
        """
        toml_dict = {
            'entities': {
                'AccessToken': {
                    'extends': ['oauth2_provider.models.AbstractAccessToken'],
                    'table_name': 'access_token',
                    'columns': [
                        {'name': 'id', 'type': 'bigint', 'primary_key': True},
                        {'name': 'token', 'type': 'string'}
                    ]
                }
            }
        }
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code with reference mode (multi-file)
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        files = renderer.render_multi_file(er_model)
        
        # Get the entity file
        entity_file = files.get('access_token.py', '')
        
        # Property 1: Import statement should contain `third.` prefix
        expected_import = 'from third.oauth2_provider.models_sqlalchemy import AbstractAccessToken'
        assert expected_import in entity_file, (
            f"COUNTEREXAMPLE FOUND (Req 2.1, 2.2): Generated import statement is MISSING `third.` prefix.\n"
            f"Expected: {expected_import}\n"
            f"This confirms the bug: third-party library imports lack `third.` prefix.\n"
            f"Generated entity file:\n{entity_file}"
        )
        
        # Property 2: File should be generated in `third/` directory
        expected_file_path = 'third/oauth2_provider/models_sqlalchemy.py'
        assert expected_file_path in files, (
            f"COUNTEREXAMPLE FOUND (Req 2.3): Third-party library file NOT generated.\n"
            f"Expected file: {expected_file_path}\n"
            f"Generated files: {list(files.keys())}\n"
            f"This confirms the bug: system doesn't generate files in `third/` directory."
        )
        
        # Property 3: Generated file should contain class definition
        third_party_file = files.get(expected_file_path, '')
        assert 'class AbstractAccessToken' in third_party_file, (
            f"COUNTEREXAMPLE FOUND (Req 2.4): Third-party file missing class definition.\n"
            f"Expected: class AbstractAccessToken\n"
            f"Generated file content:\n{third_party_file}"
        )
    
    def test_concrete_django_auth_inheritance(self):
        """
        Concrete test case 2: Django Auth inheritance
        
        Entity extends `django.contrib.auth.models.AbstractUser`
        
        Expected behavior:
        - Import statement: `from third.django.contrib.auth.models_sqlalchemy import AbstractUser`
        - File generated: `third/django/contrib/auth/models_sqlalchemy.py` with `AbstractUser` class
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test FAILS
        """
        toml_dict = {
            'entities': {
                'CustomUser': {
                    'extends': ['django.contrib.auth.models.AbstractUser'],
                    'table_name': 'custom_user',
                    'columns': [
                        {'name': 'id', 'type': 'bigint', 'primary_key': True},
                        {'name': 'bio', 'type': 'text'}
                    ]
                }
            }
        }
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code with reference mode (multi-file)
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        files = renderer.render_multi_file(er_model)
        
        # Get the entity file
        entity_file = files.get('custom_user.py', '')
        
        # Property 1: Import statement should contain `third.` prefix
        expected_import = 'from third.django.contrib.auth.models_sqlalchemy import AbstractUser'
        assert expected_import in entity_file, (
            f"COUNTEREXAMPLE FOUND (Req 2.1, 2.2): Generated import statement is MISSING `third.` prefix.\n"
            f"Expected: {expected_import}\n"
            f"Generated entity file:\n{entity_file}"
        )
        
        # Property 2: File should be generated in `third/` directory
        expected_file_path = 'third/django/contrib/auth/models_sqlalchemy.py'
        assert expected_file_path in files, (
            f"COUNTEREXAMPLE FOUND (Req 2.3): Third-party library file NOT generated.\n"
            f"Expected file: {expected_file_path}\n"
            f"Generated files: {list(files.keys())}\n"
        )
        
        # Property 3: Generated file should contain class definition
        third_party_file = files.get(expected_file_path, '')
        assert 'class AbstractUser' in third_party_file, (
            f"COUNTEREXAMPLE FOUND (Req 2.4): Third-party file missing class definition.\n"
            f"Expected: class AbstractUser\n"
            f"Generated file content:\n{third_party_file}"
        )
    
    def test_concrete_multiple_inheritance_mix(self):
        """
        Concrete test case 3: Multiple inheritance mix
        
        Entity extends both third-party library and internal mixin:
        - `oauth2_provider.models.AbstractAccessToken` (third-party, 3 parts)
        - `TimestampMixin` (internal, 1 part)
        
        Expected behavior:
        - Third-party import: `from third.oauth2_provider.models_sqlalchemy import AbstractAccessToken`
        - Internal mixin import: `from mixins.timestamp_mixin import TimestampMixin`
        - Both files generated correctly
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test FAILS
        """
        toml_dict = {
            'templates': {
                'TimestampMixin': {
                    'columns': [
                        {'name': 'created_at', 'type': 'datetime'}
                    ]
                }
            },
            'entities': {
                'Token': {
                    'extends': ['oauth2_provider.models.AbstractAccessToken', 'TimestampMixin'],
                    'table_name': 'token',
                    'columns': [
                        {'name': 'id', 'type': 'bigint', 'primary_key': True},
                        {'name': 'value', 'type': 'string'}
                    ]
                }
            }
        }
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code with reference mode (multi-file)
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        files = renderer.render_multi_file(er_model)
        
        # Get the entity file
        entity_file = files.get('token.py', '')
        
        # Property 1: Third-party import should have `third.` prefix
        expected_third_party_import = 'from third.oauth2_provider.models_sqlalchemy import AbstractAccessToken'
        assert expected_third_party_import in entity_file, (
            f"COUNTEREXAMPLE FOUND (Req 2.1, 2.2): Third-party import MISSING `third.` prefix.\n"
            f"Expected: {expected_third_party_import}\n"
            f"Generated entity file:\n{entity_file}"
        )
        
        # Property 2: Internal mixin import should NOT have `third.` prefix
        # Note: System converts template names to lowercase without underscores (existing behavior)
        expected_mixin_import = 'from mixins.timestampmixin import TimestampMixin'
        assert expected_mixin_import in entity_file, (
            f"Internal mixin import should be: {expected_mixin_import}\n"
            f"Generated entity file:\n{entity_file}"
        )
        
        # Property 3: Third-party file should be generated
        expected_third_party_file = 'third/oauth2_provider/models_sqlalchemy.py'
        assert expected_third_party_file in files, (
            f"COUNTEREXAMPLE FOUND (Req 2.3): Third-party file NOT generated.\n"
            f"Expected file: {expected_third_party_file}\n"
            f"Generated files: {list(files.keys())}"
        )
        
        # Property 4: Internal mixin file should be generated
        # Note: System converts template names to lowercase without underscores (existing behavior)
        expected_mixin_file = 'mixins/timestampmixin.py'
        assert expected_mixin_file in files, (
            f"Internal mixin file should be generated: {expected_mixin_file}\n"
            f"Generated files: {list(files.keys())}"
        )
    
    def test_concrete_edge_case_exactly_three_parts(self):
        """
        Concrete test case 4: Edge case - namespace with exactly 3 parts
        
        Entity extends `package.module.Class` (exactly 3 parts)
        
        Expected behavior:
        - Should be detected as third-party library (3+ parts)
        - Import statement: `from third.package.module_sqlalchemy import Class`
        - File generated: `third/package/module_sqlalchemy.py`
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test FAILS
        """
        toml_dict = {
            'entities': {
                'MyEntity': {
                    'extends': ['package.module.BaseClass'],
                    'table_name': 'my_entity',
                    'columns': [
                        {'name': 'id', 'type': 'bigint', 'primary_key': True},
                        {'name': 'name', 'type': 'string'}
                    ]
                }
            }
        }
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code with reference mode (multi-file)
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        files = renderer.render_multi_file(er_model)
        
        # Get the entity file
        entity_file = files.get('my_entity.py', '')
        
        # Property 1: Import statement should contain `third.` prefix
        expected_import = 'from third.package.module_sqlalchemy import BaseClass'
        assert expected_import in entity_file, (
            f"COUNTEREXAMPLE FOUND (Req 2.2): Edge case with 3 parts NOT detected as third-party.\n"
            f"Expected: {expected_import}\n"
            f"Generated entity file:\n{entity_file}"
        )
        
        # Property 2: File should be generated in `third/` directory
        expected_file_path = 'third/package/module_sqlalchemy.py'
        assert expected_file_path in files, (
            f"COUNTEREXAMPLE FOUND (Req 2.3): Third-party file NOT generated for 3-part namespace.\n"
            f"Expected file: {expected_file_path}\n"
            f"Generated files: {list(files.keys())}"
        )
    
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(toml_with_third_party_inheritance())
    def test_property_third_party_import_has_prefix(self, test_data):
        """
        Property-based test: Third-party imports should have `third.` prefix
        
        This verifies Requirements 2.1, 2.2:
        - When entity extends third-party library (3+ namespace parts)
        - Then import statement should contain `third.` prefix
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test FAILS
        - Generated imports will be missing `third.` prefix
        - Counterexamples will show which imports are incorrect
        
        **EXPECTED OUTCOME ON FIXED CODE**: This test PASSES
        - All third-party imports will have `third.` prefix
        """
        toml_dict, entity_name, third_party_classes, entity_columns = test_data
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code with reference mode (multi-file)
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        files = renderer.render_multi_file(er_model)
        
        # Get the entity file
        entity_filename = entity_name.lower() + '.py'
        # Handle snake_case conversion for multi-word names
        import re
        entity_filename = re.sub(r'(?<!^)(?=[A-Z])', '_', entity_name).lower() + '.py'
        entity_file = files.get(entity_filename, '')
        
        # If entity file is empty, check if it exists with a different name
        if not entity_file:
            # Try to find the entity file by looking for files that are not mixin or third-party files
            entity_files = [f for f in files.keys() if not f.startswith('mixins/') and not f.startswith('third/')]
            assert entity_files, (
                f"No entity file generated.\n"
                f"Expected entity file: {entity_filename}\n"
                f"Generated files: {list(files.keys())}\n"
                f"Entity name: {entity_name}\n"
                f"TOML content:\n{toml_content}"
            )
            # Use the first entity file found
            entity_filename = entity_files[0]
            entity_file = files[entity_filename]
        
        # Property: All third-party imports should have `third.` prefix
        for third_party_class in third_party_classes:
            # Extract module path and class name
            parts = third_party_class.rsplit('.', 1)
            if len(parts) == 2:
                module_path = parts[0]
                class_name = parts[1]
                
                # Expected import with `third.` prefix and `_sqlalchemy` suffix
                expected_import_pattern = rf'from\s+third\.{re.escape(module_path)}_sqlalchemy\s+import\s+.*{re.escape(class_name)}'
                
                assert re.search(expected_import_pattern, entity_file), (
                    f"COUNTEREXAMPLE FOUND: Generated import for '{class_name}' is MISSING `third.` prefix.\n"
                    f"Third-party class: {third_party_class}\n"
                    f"Expected pattern: from third.{module_path}_sqlalchemy import {class_name}\n"
                    f"Entity: {entity_name}\n"
                    f"This confirms the bug: third-party library imports lack `third.` prefix.\n"
                    f"Generated entity file:\n{entity_file}"
                )
    
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(toml_with_third_party_inheritance())
    def test_property_third_party_files_generated(self, test_data):
        """
        Property-based test: Third-party files should be generated in `third/` directory
        
        This verifies Requirements 2.3, 2.4:
        - When entity extends third-party library (3+ namespace parts)
        - Then system should generate corresponding file in `third/` directory
        - File should contain class definition
        
        **EXPECTED OUTCOME ON UNFIXED CODE**: This test FAILS
        - Files will NOT be generated in `third/` directory
        - Counterexamples will show which files are missing
        
        **EXPECTED OUTCOME ON FIXED CODE**: This test PASSES
        - All third-party files will be generated with class definitions
        """
        toml_dict, entity_name, third_party_classes, entity_columns = test_data
        
        # Convert dict to TOML string
        toml_content = toml.dumps(toml_dict)
        
        # Parse TOML
        parser = TomlERParser()
        er_model = parser.parse(toml_content)
        
        # Generate SQLAlchemy code with reference mode (multi-file)
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        files = renderer.render_multi_file(er_model)
        
        # Property: All third-party classes should have corresponding files in `third/` directory
        for third_party_class in third_party_classes:
            # Extract module path and class name
            parts = third_party_class.rsplit('.', 1)
            if len(parts) == 2:
                module_path = parts[0]
                class_name = parts[1]
                
                # Expected file path: third/{module_path}_sqlalchemy.py
                expected_file_path = f"third/{module_path.replace('.', '/')}_sqlalchemy.py"
                
                assert expected_file_path in files, (
                    f"COUNTEREXAMPLE FOUND: Third-party file NOT generated.\n"
                    f"Third-party class: {third_party_class}\n"
                    f"Expected file: {expected_file_path}\n"
                    f"Generated files: {list(files.keys())}\n"
                    f"This confirms the bug: system doesn't generate files in `third/` directory."
                )
                
                # Verify file contains class definition
                third_party_file = files.get(expected_file_path, '')
                assert f'class {class_name}' in third_party_file, (
                    f"COUNTEREXAMPLE FOUND: Third-party file missing class definition.\n"
                    f"Expected: class {class_name}\n"
                    f"File: {expected_file_path}\n"
                    f"Generated file content:\n{third_party_file}"
                )
