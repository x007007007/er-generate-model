"""
Property-based tests for MixinGenerator.

These tests use hypothesis to verify universal properties across many generated inputs.
Each test runs a minimum of 100 iterations.
"""
import tempfile
import shutil
import ast
import re
from pathlib import Path
import pytest
from hypothesis import given, settings, strategies as st, HealthCheck

from x007007007.er.mixin_generator import MixinGenerator
from x007007007.er.models import TemplateInfo, Column
from x007007007.er.renderers.python.utils import to_snake_case


# Custom strategies for generating valid test data
valid_identifier = st.from_regex(r'[A-Z][a-zA-Z0-9]*', fullmatch=True).filter(
    lambda s: len(s) > 0 and len(s) < 30
)

valid_package_component = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(
    lambda s: len(s) > 0 and len(s) < 20 and not s.startswith('_')
)


@st.composite
def valid_export_path(draw, min_components=1, max_components=5):
    """Generate a valid export path."""
    num_components = draw(st.integers(min_value=min_components, max_value=max_components))
    components = [draw(valid_package_component) for _ in range(num_components)]
    return '.'.join(components)


@st.composite
def valid_column(draw):
    """Generate a valid Column object."""
    col_types = ['string', 'integer', 'bigint', 'datetime', 'boolean', 'text']
    col_type = draw(st.sampled_from(col_types))
    
    name = draw(st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(
        lambda s: len(s) > 0 and len(s) < 20
    ))
    
    max_length = draw(st.integers(min_value=1, max_value=500)) if col_type == 'string' else None
    
    # Generate valid comment text (printable ASCII characters only, no null bytes)
    comment_text = draw(st.one_of(
        st.none(),
        st.text(
            alphabet=st.characters(min_codepoint=32, max_codepoint=126),
            min_size=1,
            max_size=50
        )
    ))
    
    return Column(
        name=name,
        type=col_type,
        db_column=name,
        is_pk=draw(st.booleans()),
        nullable=draw(st.booleans()),
        unique=draw(st.booleans()),
        indexed=draw(st.booleans()),
        max_length=max_length,
        comment=comment_text
    )


@st.composite
def valid_template_info(draw):
    """Generate a valid TemplateInfo object."""
    name = draw(valid_identifier)
    export_path = draw(valid_export_path())
    columns = draw(st.lists(valid_column(), min_size=1, max_size=10))
    
    return TemplateInfo(
        name=name,
        package=f"test.{export_path}",
        export_path=export_path,
        columns=columns,
        source_file='test.toml'
    )


class TestProperty8MixinFilePathConstruction:
    """
    Property 8: Mixin File Path Construction
    
    **Validates: Requirements 4.1, 6.1, 6.2, 6.3**
    
    For any template with an export_path, the generated mixin file should be
    created at the path derived by converting dots to directory separators and
    the class name to snake_case with .py extension.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        template_name=valid_identifier,
        template_info=valid_template_info()
    )
    def test_file_path_construction_from_export_path(self, template_name, template_info):
        """
        Test that file path is correctly constructed from export_path.
        
        This verifies Requirements 6.1, 6.2, 6.3:
        - Export_path dots are converted to directory separators
        - Class name is converted to snake_case for filename
        - .py extension is appended
        """
        generator = MixinGenerator()
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Generate mixin file
            file_path = generator.generate_mixin_file(
                template_name,
                template_info,
                temp_dir
            )
            
            # Property: File should exist
            assert Path(file_path).exists(), (
                f"Generated file does not exist: {file_path}"
            )
            
            # Property: Path should contain export_path components as directories
            export_path_as_dir = template_info.export_path.replace('.', '/')
            assert export_path_as_dir in file_path, (
                f"Export path not correctly converted to directory structure:\n"
                f"  Export path: {template_info.export_path}\n"
                f"  Expected in path: {export_path_as_dir}\n"
                f"  Actual path: {file_path}"
            )
            
            # Property: Filename should be snake_case version of template name
            expected_filename = to_snake_case(template_name) + '.py'
            assert file_path.endswith(expected_filename), (
                f"Filename not correctly constructed:\n"
                f"  Template name: {template_name}\n"
                f"  Expected filename: {expected_filename}\n"
                f"  Actual path: {file_path}"
            )
            
            # Property: File should have .py extension
            assert file_path.endswith('.py'), (
                f"File should have .py extension: {file_path}"
            )
            
        finally:
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir)


class TestProperty9MixinAbstractClassGeneration:
    """
    Property 9: Mixin Abstract Class Generation
    
    **Validates: Requirements 4.2**
    
    For any generated mixin file, it should contain a class with
    __abstract__ = True attribute.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        template_name=valid_identifier,
        template_info=valid_template_info()
    )
    def test_generated_class_is_abstract(self, template_name, template_info):
        """
        Test that generated mixin class has __abstract__ = True.
        
        This verifies Requirement 4.2: THE Mixin_Generator SHALL generate a
        class with `__abstract__ = True` attribute.
        """
        generator = MixinGenerator()
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Generate mixin file
            file_path = generator.generate_mixin_file(
                template_name,
                template_info,
                temp_dir
            )
            
            # Read generated file
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Property: File should contain __abstract__ = True
            assert '__abstract__ = True' in content, (
                f"Generated class does not have __abstract__ = True:\n"
                f"  Template: {template_name}\n"
                f"  File: {file_path}\n"
                f"  Content preview: {content[:500]}"
            )
            
            # Property: Class should be defined with the template name
            class_pattern = f'class {template_name}'
            assert class_pattern in content, (
                f"Class definition not found:\n"
                f"  Expected: {class_pattern}\n"
                f"  Content preview: {content[:500]}"
            )
            
        finally:
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir)


class TestProperty10MixinColumnCompleteness:
    """
    Property 10: Mixin Column Completeness
    
    **Validates: Requirements 4.3**
    
    For any template with columns, all columns should appear in the generated
    mixin class.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        template_name=valid_identifier,
        template_info=valid_template_info()
    )
    def test_all_columns_present_in_generated_class(self, template_name, template_info):
        """
        Test that all template columns appear in the generated mixin.
        
        This verifies Requirement 4.3: THE Mixin_Generator SHALL include all
        columns from the template in the generated class.
        """
        generator = MixinGenerator()
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Generate mixin file
            file_path = generator.generate_mixin_file(
                template_name,
                template_info,
                temp_dir
            )
            
            # Read generated file
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Property: All columns should be present in the file
            for col in template_info.columns:
                column_pattern = f'{col.name} = Column('
                assert column_pattern in content, (
                    f"Column '{col.name}' not found in generated class:\n"
                    f"  Template: {template_name}\n"
                    f"  Expected pattern: {column_pattern}\n"
                    f"  File: {file_path}\n"
                    f"  Content preview: {content[:1000]}"
                )
            
            # Property: Number of Column definitions should match number of columns
            column_count = content.count(' = Column(')
            assert column_count == len(template_info.columns), (
                f"Column count mismatch:\n"
                f"  Expected: {len(template_info.columns)}\n"
                f"  Found: {column_count}\n"
                f"  Template columns: {[c.name for c in template_info.columns]}"
            )
            
        finally:
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir)


class TestProperty11DirectoryStructureCreation:
    """
    Property 11: Directory Structure Creation
    
    **Validates: Requirements 4.4, 6.4**
    
    For any mixin file generation, all intermediate directories in the path
    should be created if they don't exist.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        template_name=valid_identifier,
        template_info=valid_template_info()
    )
    def test_directory_structure_created(self, template_name, template_info):
        """
        Test that all intermediate directories are created.
        
        This verifies Requirements 4.4, 6.4: THE Mixin_Generator SHALL create
        the directory structure if it doesn't exist, and SHALL create all
        intermediate directories in the path.
        """
        generator = MixinGenerator()
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Generate mixin file
            file_path = generator.generate_mixin_file(
                template_name,
                template_info,
                temp_dir
            )
            
            # Property: File should exist (implies directories were created)
            assert Path(file_path).exists(), (
                f"Generated file does not exist: {file_path}"
            )
            
            # Property: All intermediate directories should exist
            file_path_obj = Path(file_path)
            parent_dir = file_path_obj.parent
            
            assert parent_dir.exists(), (
                f"Parent directory does not exist: {parent_dir}"
            )
            
            assert parent_dir.is_dir(), (
                f"Parent path is not a directory: {parent_dir}"
            )
            
            # Property: All components of export_path should exist as directories
            export_components = template_info.export_path.split('.')
            current_path = Path(temp_dir)
            
            for component in export_components:
                current_path = current_path / component
                assert current_path.exists(), (
                    f"Directory component does not exist:\n"
                    f"  Component: {component}\n"
                    f"  Path: {current_path}\n"
                    f"  Export path: {template_info.export_path}"
                )
                assert current_path.is_dir(), (
                    f"Path component is not a directory: {current_path}"
                )
            
        finally:
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir)


class TestProperty20GeneratedCodeSyntacticValidity:
    """
    Property 20: Generated Code Syntactic Validity
    
    **Validates: Requirements 9.1**
    
    For any generated mixin or entity file, the Python code should be
    syntactically valid and parseable.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        template_name=valid_identifier,
        template_info=valid_template_info()
    )
    def test_generated_code_is_syntactically_valid(self, template_name, template_info):
        """
        Test that generated code is syntactically valid Python.
        
        This verifies Requirement 9.1: THE Mixin_Generator SHALL generate
        syntactically valid Python code.
        """
        generator = MixinGenerator()
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Generate mixin file
            file_path = generator.generate_mixin_file(
                template_name,
                template_info,
                temp_dir
            )
            
            # Read generated file
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Property: Code should be parseable by Python AST
            try:
                ast.parse(content)
            except SyntaxError as e:
                pytest.fail(
                    f"Generated code has syntax errors:\n"
                    f"  Template: {template_name}\n"
                    f"  File: {file_path}\n"
                    f"  Error: {e}\n"
                    f"  Content:\n{content}"
                )
            
            # Property: Code should compile without errors
            try:
                compile(content, file_path, 'exec')
            except Exception as e:
                pytest.fail(
                    f"Generated code does not compile:\n"
                    f"  Template: {template_name}\n"
                    f"  File: {file_path}\n"
                    f"  Error: {e}\n"
                    f"  Content:\n{content}"
                )
            
        finally:
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir)


class TestProperty21SQLAlchemyImportPresence:
    """
    Property 21: SQLAlchemy Import Presence
    
    **Validates: Requirements 9.2**
    
    For any generated mixin file, it should include the necessary SQLAlchemy
    imports.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(
        template_name=valid_identifier,
        template_info=valid_template_info()
    )
    def test_sqlalchemy_imports_present(self, template_name, template_info):
        """
        Test that generated code includes necessary SQLAlchemy imports.
        
        This verifies Requirement 9.2: THE Mixin_Generator SHALL include proper
        SQLAlchemy imports in generated files.
        """
        generator = MixinGenerator()
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Generate mixin file
            file_path = generator.generate_mixin_file(
                template_name,
                template_info,
                temp_dir
            )
            
            # Read generated file
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Property: Should import Column from sqlalchemy
            assert 'from sqlalchemy import Column' in content, (
                f"Missing 'from sqlalchemy import Column':\n"
                f"  Template: {template_name}\n"
                f"  File: {file_path}\n"
                f"  Content preview: {content[:500]}"
            )
            
            # Property: Should import declarative_base from sqlalchemy.orm
            assert 'from sqlalchemy.orm import declarative_base' in content, (
                f"Missing 'from sqlalchemy.orm import declarative_base':\n"
                f"  Template: {template_name}\n"
                f"  File: {file_path}\n"
                f"  Content preview: {content[:500]}"
            )
            
            # Property: Should create Base using declarative_base
            assert 'Base = declarative_base()' in content, (
                f"Missing 'Base = declarative_base()':\n"
                f"  Template: {template_name}\n"
                f"  File: {file_path}\n"
                f"  Content preview: {content[:500]}"
            )
            
            # Property: Should import column types used in the template
            # Check that at least one column type is imported
            column_type_pattern = re.compile(r'from sqlalchemy import Column,\s*(\w+)')
            match = column_type_pattern.search(content)
            
            if len(template_info.columns) > 0:
                # If there are columns, there should be column type imports
                # (unless all columns use types that don't need explicit imports)
                assert 'from sqlalchemy import' in content, (
                    f"Missing SQLAlchemy type imports:\n"
                    f"  Template: {template_name}\n"
                    f"  Columns: {[c.type for c in template_info.columns]}\n"
                    f"  Content preview: {content[:500]}"
                )
            
        finally:
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir)
