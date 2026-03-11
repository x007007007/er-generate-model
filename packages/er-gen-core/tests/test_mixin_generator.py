"""Unit tests for MixinGenerator."""
import tempfile
import shutil
from pathlib import Path
import pytest

from x007007007.er.mixin_generator import MixinGenerator
from x007007007.er.models import TemplateInfo, Column


class TestMixinGenerator:
    """Test suite for MixinGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = MixinGenerator()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_generate_simple_mixin(self):
        """Test generating a simple mixin file."""
        # Create template info
        columns = [
            Column(
                name='id',
                type='bigint',
                db_column='id',
                is_pk=True,
                nullable=False
            ),
            Column(
                name='created_at',
                type='datetime',
                db_column='created_at',
                nullable=False
            )
        ]
        
        template_info = TemplateInfo(
            name='TestMixin',
            package='test.models.base',
            export_path='test.models.base_sqlalchemy',
            columns=columns,
            source_file='test.toml'
        )
        
        # Generate mixin file
        file_path = self.generator.generate_mixin_file(
            'TestMixin',
            template_info,
            self.temp_dir
        )
        
        # Verify file was created
        assert Path(file_path).exists()
        
        # Verify file path structure
        expected_path = Path(self.temp_dir) / 'test' / 'models' / 'base_sqlalchemy' / 'test_mixin.py'
        assert Path(file_path) == expected_path
        
        # Verify file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for key elements
        assert 'class TestMixin(Base):' in content
        assert '__abstract__ = True' in content
        assert 'id = Column(' in content
        assert 'created_at = Column(' in content
        assert 'from sqlalchemy import Column' in content
    
    def test_generate_mixin_with_complex_name(self):
        """Test generating mixin with CamelCase name converted to snake_case."""
        columns = [
            Column(
                name='name',
                type='string',
                db_column='name',
                max_length=255
            )
        ]
        
        template_info = TemplateInfo(
            name='KinkoTechModelBase',
            package='kinkotech.common.models.base',
            export_path='kinkotech.common.models.base_sqlalchemy',
            columns=columns,
            source_file='test.toml'
        )
        
        # Generate mixin file
        file_path = self.generator.generate_mixin_file(
            'KinkoTechModelBase',
            template_info,
            self.temp_dir
        )
        
        # Verify filename is snake_case
        assert file_path.endswith('kinko_tech_model_base.py')
        
        # Verify class name is preserved
        with open(file_path, 'r') as f:
            content = f.read()
        assert 'class KinkoTechModelBase(Base):' in content
    
    def test_generate_mixin_creates_directories(self):
        """Test that directory structure is created if it doesn't exist."""
        columns = [
            Column(
                name='id',
                type='bigint',
                db_column='id',
                is_pk=True
            )
        ]
        
        template_info = TemplateInfo(
            name='DeepMixin',
            package='a.b.c.d.e',
            export_path='a.b.c.d.e_sqlalchemy',
            columns=columns,
            source_file='test.toml'
        )
        
        # Generate mixin file
        file_path = self.generator.generate_mixin_file(
            'DeepMixin',
            template_info,
            self.temp_dir
        )
        
        # Verify all directories were created
        expected_dir = Path(self.temp_dir) / 'a' / 'b' / 'c' / 'd' / 'e_sqlalchemy'
        assert expected_dir.exists()
        assert expected_dir.is_dir()
    
    def test_generate_mixin_without_export_path_raises_error(self):
        """Test that missing export_path raises ValueError."""
        columns = [
            Column(
                name='id',
                type='bigint',
                db_column='id',
                is_pk=True
            )
        ]
        
        template_info = TemplateInfo(
            name='BadMixin',
            package='test.models',
            export_path=None,  # Missing export_path
            columns=columns,
            source_file='test.toml'
        )
        
        with pytest.raises(ValueError, match="must have export_path set"):
            self.generator.generate_mixin_file(
                'BadMixin',
                template_info,
                self.temp_dir
            )
    
    def test_generate_mixin_with_empty_columns_raises_error(self):
        """Test that empty columns list raises ValueError."""
        template_info = TemplateInfo(
            name='EmptyMixin',
            package='test.models',
            export_path='test.models_sqlalchemy',
            columns=[],  # Empty columns
            source_file='test.toml'
        )
        
        with pytest.raises(ValueError, match="empty columns list"):
            self.generator.generate_mixin_file(
                'EmptyMixin',
                template_info,
                self.temp_dir
            )
    
    def test_generate_mixin_with_empty_template_name_raises_error(self):
        """Test that empty template name raises ValueError."""
        columns = [
            Column(
                name='id',
                type='bigint',
                db_column='id',
                is_pk=True
            )
        ]
        
        template_info = TemplateInfo(
            name='TestMixin',
            package='test.models',
            export_path='test.models_sqlalchemy',
            columns=columns,
            source_file='test.toml'
        )
        
        with pytest.raises(ValueError, match="template_name cannot be empty"):
            self.generator.generate_mixin_file(
                '',  # Empty name
                template_info,
                self.temp_dir
            )
    
    def test_generate_mixin_with_various_column_types(self):
        """Test generating mixin with various column types and attributes."""
        columns = [
            Column(
                name='id',
                type='bigint',
                db_column='id',
                is_pk=True,
                nullable=False
            ),
            Column(
                name='name',
                type='string',
                db_column='name',
                max_length=255,
                nullable=False,
                unique=True
            ),
            Column(
                name='email',
                type='string',
                db_column='email',
                max_length=255,
                indexed=True
            ),
            Column(
                name='age',
                type='integer',
                db_column='age',
                nullable=True
            ),
            Column(
                name='created_at',
                type='datetime',
                db_column='created_at',
                nullable=False,
                comment='Creation timestamp'
            )
        ]
        
        template_info = TemplateInfo(
            name='ComplexMixin',
            package='test.models',
            export_path='test.models_sqlalchemy',
            columns=columns,
            source_file='test.toml'
        )
        
        # Generate mixin file
        file_path = self.generator.generate_mixin_file(
            'ComplexMixin',
            template_info,
            self.temp_dir
        )
        
        # Verify file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for all columns
        assert 'id = Column(' in content
        assert 'name = Column(' in content
        assert 'email = Column(' in content
        assert 'age = Column(' in content
        assert 'created_at = Column(' in content
        
        # Check for attributes
        assert 'primary_key=True' in content
        assert 'unique=True' in content
        assert 'index=True' in content
        assert 'comment=' in content
    
    def test_file_path_construction_accuracy(self):
        """Test that file path is constructed correctly from export_path."""
        columns = [
            Column(
                name='id',
                type='bigint',
                db_column='id',
                is_pk=True
            )
        ]
        
        template_info = TemplateInfo(
            name='PathTestMixin',
            package='a.b.c',
            export_path='a.b.c_sqlalchemy',
            columns=columns,
            source_file='test.toml'
        )
        
        # Generate mixin file
        file_path = self.generator.generate_mixin_file(
            'PathTestMixin',
            template_info,
            self.temp_dir
        )
        
        # Verify path structure
        expected_path = Path(self.temp_dir) / 'a' / 'b' / 'c_sqlalchemy' / 'path_test_mixin.py'
        assert Path(file_path) == expected_path
        
        # Verify dots are converted to slashes
        assert 'a/b/c_sqlalchemy' in file_path or 'a\\b\\c_sqlalchemy' in file_path
    
    def test_mixin_file_has_py_extension(self):
        """Test that generated mixin file has .py extension."""
        columns = [
            Column(
                name='id',
                type='bigint',
                db_column='id',
                is_pk=True
            )
        ]
        
        template_info = TemplateInfo(
            name='ExtensionTest',
            package='test.models',
            export_path='test.models_sqlalchemy',
            columns=columns,
            source_file='test.toml'
        )
        
        # Generate mixin file
        file_path = self.generator.generate_mixin_file(
            'ExtensionTest',
            template_info,
            self.temp_dir
        )
        
        # Verify .py extension
        assert file_path.endswith('.py')
        assert Path(file_path).suffix == '.py'
    
    def test_mixin_with_single_column(self):
        """Test generating mixin with just one column."""
        columns = [
            Column(
                name='timestamp',
                type='datetime',
                db_column='timestamp',
                nullable=False
            )
        ]
        
        template_info = TemplateInfo(
            name='SingleColumnMixin',
            package='test.models',
            export_path='test.models_sqlalchemy',
            columns=columns,
            source_file='test.toml'
        )
        
        # Generate mixin file
        file_path = self.generator.generate_mixin_file(
            'SingleColumnMixin',
            template_info,
            self.temp_dir
        )
        
        # Verify file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for the single column
        assert 'timestamp = Column(' in content
        assert '__abstract__ = True' in content
    
    def test_mixin_with_special_characters_in_comment(self):
        """Test generating mixin with special characters in column comments."""
        columns = [
            Column(
                name='description',
                type='text',
                db_column='description',
                comment="User's description with 'quotes' and \"double quotes\""
            )
        ]
        
        template_info = TemplateInfo(
            name='CommentMixin',
            package='test.models',
            export_path='test.models_sqlalchemy',
            columns=columns,
            source_file='test.toml'
        )
        
        # Generate mixin file
        file_path = self.generator.generate_mixin_file(
            'CommentMixin',
            template_info,
            self.temp_dir
        )
        
        # Verify file exists and is valid Python
        assert Path(file_path).exists()
        
        # Verify file content is syntactically valid
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Should be able to compile the generated code
        import ast
        try:
            ast.parse(content)
        except SyntaxError:
            pytest.fail(f"Generated code has syntax errors:\n{content}")
    
    def test_directory_creation_with_existing_parent(self):
        """Test that mixin generation works when parent directory already exists."""
        # Create parent directory first
        parent_dir = Path(self.temp_dir) / 'existing' / 'path'
        parent_dir.mkdir(parents=True, exist_ok=True)
        
        columns = [
            Column(
                name='id',
                type='bigint',
                db_column='id',
                is_pk=True
            )
        ]
        
        template_info = TemplateInfo(
            name='ExistingDirMixin',
            package='existing.path.models',
            export_path='existing.path.models_sqlalchemy',
            columns=columns,
            source_file='test.toml'
        )
        
        # Generate mixin file
        file_path = self.generator.generate_mixin_file(
            'ExistingDirMixin',
            template_info,
            self.temp_dir
        )
        
        # Verify file was created
        assert Path(file_path).exists()
    
    def test_column_order_preserved(self):
        """Test that column order is preserved in generated mixin."""
        columns = [
            Column(name='first', type='string', db_column='first', max_length=50),
            Column(name='second', type='integer', db_column='second'),
            Column(name='third', type='datetime', db_column='third'),
            Column(name='fourth', type='boolean', db_column='fourth'),
        ]
        
        template_info = TemplateInfo(
            name='OrderMixin',
            package='test.models',
            export_path='test.models_sqlalchemy',
            columns=columns,
            source_file='test.toml'
        )
        
        # Generate mixin file
        file_path = self.generator.generate_mixin_file(
            'OrderMixin',
            template_info,
            self.temp_dir
        )
        
        # Verify column order in file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find positions of each column definition
        first_pos = content.find('first = Column(')
        second_pos = content.find('second = Column(')
        third_pos = content.find('third = Column(')
        fourth_pos = content.find('fourth = Column(')
        
        # Verify order is preserved
        assert first_pos < second_pos < third_pos < fourth_pos, (
            "Column order not preserved in generated file"
        )
