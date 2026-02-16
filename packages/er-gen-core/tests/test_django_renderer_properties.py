"""
Property-based tests for Django renderers.

These tests use hypothesis to verify universal properties across many generated inputs.
Each test runs a minimum of 100 iterations.
"""
import ast
import re
import pytest
from hypothesis import given, settings, strategies as st, HealthCheck
from x007007007.er.renderers.python.django import DjangoRenderer, DjangoPackageRenderer
from x007007007.er.models import ERModel, Entity, Column


# Custom strategies for generating ER models
safe_text = st.text().filter(lambda s: '\x00' not in s and len(s) < 200 and '\r' not in s and '\n' not in s)
safe_identifier = st.from_regex(r'[A-Z][a-zA-Z0-9]*', fullmatch=True).filter(lambda s: len(s) < 50)
# For comments in docstrings, avoid triple quotes and problematic characters
safe_comment = st.text().filter(lambda s: '\x00' not in s and '"""' not in s and len(s) < 200 and '\r' not in s and '\n' not in s)


@st.composite
def column_with_values(draw):
    """Generate a column with default values and comments."""
    name = draw(st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(lambda s: len(s) < 30))
    col_type = draw(st.sampled_from(['int', 'varchar', 'text', 'boolean', 'float']))
    
    # Generate default value based on type
    if col_type == 'int':
        default = draw(st.one_of(st.none(), st.integers()))
    elif col_type == 'boolean':
        default = draw(st.one_of(st.none(), st.booleans()))
    elif col_type == 'float':
        default = draw(st.one_of(st.none(), st.floats(allow_nan=False, allow_infinity=False)))
    else:
        default = draw(st.one_of(st.none(), safe_text))
    
    comment = draw(st.one_of(st.none(), safe_text))
    
    return Column(
        name=name,
        type=col_type,
        db_column=name,  # Use name as db_column by default
        max_length=100 if col_type == 'varchar' else None,
        is_pk=(name == 'id'),
        nullable=True,
        default=default,
        comment=comment
    )


@st.composite
def simple_entity(draw):
    """Generate a simple entity with columns."""
    name = draw(safe_identifier)
    num_columns = draw(st.integers(min_value=1, max_value=5))
    
    # Always include an id column
    columns = [Column(name='id', type='int', db_column='id', is_pk=True, nullable=False)]
    
    # Add additional columns
    for _ in range(num_columns - 1):
        columns.append(draw(column_with_values()))
    
    return Entity(
        name=name,
        columns=columns,
        comment=draw(st.one_of(st.none(), safe_comment)),
        table_name=name.lower()  # Add table_name based on entity name
    )


@st.composite
def er_model_with_values(draw):
    """Generate an ERModel with entities containing default values and comments."""
    num_entities = draw(st.integers(min_value=1, max_value=3))
    entities = {}
    
    for _ in range(num_entities):
        entity = draw(simple_entity())
        entities[entity.name] = entity
    
    return ERModel(entities=entities, relationships=[], templates={})


class TestProperty5DjangoTemplateIntegration:
    """
    Property 5: Django Template Integration
    
    **Validates: Requirements 7.1, 7.2**
    
    For any ERModel with entities containing columns with default values or comments,
    rendering the model with Django renderer should produce code where all default
    values and help_text are properly serialized using the code_value filter.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(er_model_with_values())
    def test_django_renderer_serializes_default_values(self, model):
        """Test that Django renderer properly serializes default values."""
        renderer = DjangoRenderer()
        result = renderer.render(model)
        
        # Check that columns with non-None default values have them serialized
        has_default = any(
            col.default is not None 
            for entity in model.entities.values() 
            for col in entity.columns
        )
        
        if has_default:
            # The default should appear in the output
            assert 'default=' in result
        
        # The generated code should be valid Python
        try:
            ast.parse(result)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{result}")
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(er_model_with_values())
    def test_django_renderer_serializes_help_text(self, model):
        """Test that Django renderer properly serializes help_text."""
        renderer = DjangoRenderer()
        result = renderer.render(model)
        
        # Check that all columns with comments have them serialized
        for entity in model.entities.values():
            for col in entity.columns:
                if col.comment is not None and col.comment != '':
                    # The help_text should appear in the output
                    assert 'help_text=' in result
                    # The generated code should be valid Python
                    try:
                        ast.parse(result)
                    except SyntaxError as e:
                        pytest.fail(f"Generated code has syntax error: {e}\nColumn: {col.name}, Comment: {col.comment}")
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(er_model_with_values())
    def test_django_renderer_handles_quotes_in_values(self, model):
        """Test that Django renderer handles quotes in default values and comments."""
        renderer = DjangoRenderer()
        
        # Add some columns with quotes in values
        for entity in model.entities.values():
            if len(entity.columns) > 1:
                # Add a column with quotes in default
                entity.columns.append(Column(
                    name='quoted_field',
                    type='varchar',
                    max_length=100,
                    nullable=True,
                    default='say "hello"',
                    comment='Field with "quotes"'
                ))
        
        result = renderer.render(model)
        
        # The generated code should be valid Python despite quotes
        try:
            ast.parse(result)
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error with quotes: {e}\n{result}")


class TestProperty7GeneratedCodeValidityDjango:
    """
    Property 7: Generated Code Validity (Django)
    
    **Validates: Requirements 7.4**
    
    For any ERModel rendered to Django code, the generated code should be
    syntactically valid Python that can be parsed without errors.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(er_model_with_values())
    def test_django_generated_code_is_valid_python(self, model):
        """Test that all Django generated code is syntactically valid."""
        renderer = DjangoRenderer()
        result = renderer.render(model)
        
        # Should be able to parse without syntax errors
        try:
            ast.parse(result)
        except SyntaxError as e:
            pytest.fail(f"Generated Django code has syntax error: {e}\n{result}")
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(er_model_with_values())
    def test_django_generated_code_has_no_unescaped_quotes(self, model):
        """Test that generated code doesn't have unescaped quotes causing errors."""
        renderer = DjangoRenderer()
        result = renderer.render(model)
        
        # Parse to ensure no syntax errors from unescaped quotes
        try:
            ast.parse(result)
        except SyntaxError as e:
            # Check if error is related to quotes
            if 'unterminated string' in str(e).lower() or 'invalid syntax' in str(e).lower():
                pytest.fail(f"Generated code has quote escaping issue: {e}\n{result}")
            raise


class TestProperty9ThreeFileStructureGeneration:
    """
    Property 9: Three-File Structure Generation
    
    **Validates: Requirements 11.1**
    
    For any ERModel with N entities, rendering with DjangoPackageRenderer
    should produce exactly 3N + 1 files (3 files per entity plus __init__.py).
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(er_model_with_values())
    def test_three_file_structure_count(self, model):
        """Test that DjangoPackageRenderer generates exactly 3N + 1 files."""
        renderer = DjangoPackageRenderer()
        result = renderer.render(model)
        
        num_entities = len(model.entities)
        expected_files = 3 * num_entities + 1  # 3 files per entity + __init__.py
        
        assert len(result) == expected_files, \
            f"Expected {expected_files} files for {num_entities} entities, got {len(result)}"
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(er_model_with_values())
    def test_three_file_structure_has_init(self, model):
        """Test that generated package always has __init__.py."""
        renderer = DjangoPackageRenderer()
        result = renderer.render(model)
        
        assert '__init__.py' in result, "Missing __init__.py in generated package"
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(er_model_with_values())
    def test_three_file_structure_has_all_components(self, model):
        """Test that each entity has queryset, manager, and model files."""
        renderer = DjangoPackageRenderer()
        result = renderer.render(model)
        
        for entity_name in model.entities.keys():
            # Convert to snake_case for filename
            from x007007007.er.renderers.python.django import to_snake_case
            base_name = to_snake_case(entity_name)
            
            assert f'{base_name}_queryset.py' in result, \
                f"Missing queryset file for {entity_name}"
            assert f'{base_name}_manager.py' in result, \
                f"Missing manager file for {entity_name}"
            assert f'{base_name}.py' in result, \
                f"Missing model file for {entity_name}"


class TestProperty10FileNamingConvention:
    """
    Property 10: File Naming Convention
    
    **Validates: Requirements 11.2, 11.3, 11.4, 11.8**
    
    For any entity with name EntityName, the generated files should be named:
    - entity_name_queryset.py (QuerySet file)
    - entity_name_manager.py (Manager file)
    - entity_name.py (Model file)
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(er_model_with_values())
    def test_file_naming_follows_snake_case(self, model):
        """Test that all file names follow snake_case convention."""
        renderer = DjangoPackageRenderer()
        result = renderer.render(model)
        
        for filename in result.keys():
            if filename == '__init__.py':
                continue
            
            # Check that filename is in snake_case (lowercase with underscores)
            assert filename.islower() or '_' in filename, \
                f"Filename {filename} is not in snake_case"
            assert not re.search(r'[A-Z]', filename), \
                f"Filename {filename} contains uppercase letters"
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(er_model_with_values())
    def test_file_naming_pattern(self, model):
        """Test that file names match expected pattern."""
        renderer = DjangoPackageRenderer()
        result = renderer.render(model)
        
        for filename in result.keys():
            if filename == '__init__.py':
                continue
            
            # Should match pattern: <name>_{queryset|manager}.py or <name>.py
            assert filename.endswith('_queryset.py') or \
                   filename.endswith('_manager.py') or \
                   (filename.endswith('.py') and not filename.startswith('_')), \
                f"Filename {filename} doesn't match expected pattern"


class TestProperty11ImportCorrectness:
    """
    Property 11: Import Correctness
    
    **Validates: Requirements 11.5, 11.6, 11.7**
    
    For any generated model file, the imports should be correct such that:
    - Model file imports Manager from manager file
    - Manager file imports QuerySet from queryset file
    - __init__.py imports only Model classes
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(er_model_with_values())
    def test_model_imports_manager(self, model):
        """Test that Model files import Manager from manager file."""
        renderer = DjangoPackageRenderer()
        result = renderer.render(model)
        
        for entity_name in model.entities.keys():
            from x007007007.er.renderers.python.django import to_snake_case
            base_name = to_snake_case(entity_name)
            model_file = f'{base_name}.py'
            
            if model_file in result:
                content = result[model_file]
                # Should import Manager
                assert f'from .{base_name}_manager import {entity_name}Manager' in content, \
                    f"Model file {model_file} doesn't import Manager correctly"
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(er_model_with_values())
    def test_manager_imports_queryset(self, model):
        """Test that Manager files import QuerySet from queryset file."""
        renderer = DjangoPackageRenderer()
        result = renderer.render(model)
        
        for entity_name in model.entities.keys():
            from x007007007.er.renderers.python.django import to_snake_case
            base_name = to_snake_case(entity_name)
            manager_file = f'{base_name}_manager.py'
            
            if manager_file in result:
                content = result[manager_file]
                # Should import QuerySet
                assert f'from .{base_name}_queryset import {entity_name}QuerySet' in content, \
                    f"Manager file {manager_file} doesn't import QuerySet correctly"
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(er_model_with_values())
    def test_init_imports_only_models(self, model):
        """Test that __init__.py imports only Model classes."""
        renderer = DjangoPackageRenderer()
        result = renderer.render(model)
        
        init_content = result['__init__.py']
        
        for entity_name in model.entities.keys():
            from x007007007.er.renderers.python.django import to_snake_case
            base_name = to_snake_case(entity_name)
            
            # Should import Model from model file
            assert f'from .{base_name} import {entity_name}' in init_content, \
                f"__init__.py doesn't import {entity_name} correctly"
            
            # Should NOT import Manager or QuerySet
            assert f'{entity_name}Manager' not in init_content or \
                   f'import {entity_name}Manager' not in init_content, \
                f"__init__.py should not import {entity_name}Manager"
            assert f'{entity_name}QuerySet' not in init_content or \
                   f'import {entity_name}QuerySet' not in init_content, \
                f"__init__.py should not import {entity_name}QuerySet"


class TestProperty12GeneratedPackageValidity:
    """
    Property 12: Generated Package Validity
    
    **Validates: Requirements 11.7, 12.1**
    
    For any ERModel rendered as a Django package, the generated package should
    be importable without errors and all Model classes should be accessible
    from the package root.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(er_model_with_values())
    def test_all_generated_files_are_valid_python(self, model):
        """Test that all generated files are syntactically valid Python."""
        renderer = DjangoPackageRenderer()
        result = renderer.render(model)
        
        for filename, content in result.items():
            try:
                ast.parse(content)
            except SyntaxError as e:
                pytest.fail(f"File {filename} has syntax error: {e}\n{content}")
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(er_model_with_values())
    def test_init_exports_all_models(self, model):
        """Test that __init__.py exports all Model classes in __all__."""
        renderer = DjangoPackageRenderer()
        result = renderer.render(model)
        
        init_content = result['__init__.py']
        
        # Should have __all__ list
        assert '__all__' in init_content, "__init__.py missing __all__ list"
        
        # All entity names should be in __all__
        for entity_name in model.entities.keys():
            assert f"'{entity_name}'" in init_content, \
                f"{entity_name} not in __all__ list"
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(er_model_with_values())
    def test_model_files_use_manager(self, model):
        """Test that Model files properly use the Manager class."""
        renderer = DjangoPackageRenderer()
        result = renderer.render(model)
        
        for entity_name in model.entities.keys():
            from x007007007.er.renderers.python.django import to_snake_case
            base_name = to_snake_case(entity_name)
            model_file = f'{base_name}.py'
            
            if model_file in result:
                content = result[model_file]
                # Should have objects = <Entity>Manager()
                assert f'objects = {entity_name}Manager()' in content, \
                    f"Model file {model_file} doesn't use Manager correctly"
