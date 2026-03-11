"""
Unit Tests for Entity Renderer Enhancements

These tests verify specific examples and edge cases for entity rendering
with mixin inheritance support in both reference and flatten modes.

**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 8.3**
"""
import pytest
from x007007007.er.models import ERModel, Entity, Column
from x007007007.er.renderers.python.sqlalchemy.renderer import SQLAlchemyRenderer


class TestReferenceModeImportGeneration:
    """Test reference mode import generation - Requirement 5.1"""
    
    def test_single_template_import(self):
        """Test import generation for a single template."""
        model = ERModel()
        model.templates = {
            'TimestampMixin': {
                'name': 'TimestampMixin',
                'package': 'common.models',
                'export_path': 'common.models_sqlalchemy',
                'columns': [
                    Column(name='created_at', type='datetime', db_column='created_at', nullable=False),
                    Column(name='updated_at', type='datetime', db_column='updated_at', nullable=True)
                ],
                'source_file': 'common.toml'
            }
        }
        
        entity = Entity(
            name='User',
            table_name='users',
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False),
                Column(name='username', type='string', db_column='username', max_length=100, nullable=False)
            ],
            extends=['TimestampMixin']
        )
        model.entities['User'] = entity
        
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        content = renderer.single_template.render(
            model=model, entity=entity, entity_relationships=[],
            table_prefix='', base_model_import=None, inheritance_mode='reference'
        )
        
        assert 'from common.models_sqlalchemy import TimestampMixin' in content


class TestReferenceModeInheritance:
    """Test reference mode inheritance - Requirement 5.2"""
    
    def test_single_template_inheritance(self):
        """Test class inheritance from a single template."""
        model = ERModel()
        model.templates = {
            'BaseMixin': {
                'name': 'BaseMixin',
                'package': 'common.models',
                'export_path': 'common.models_sqlalchemy',
                'columns': [Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False)],
                'source_file': 'common.toml'
            }
        }
        
        entity = Entity(
            name='Article',
            table_name='articles',
            columns=[Column(name='title', type='string', db_column='title', max_length=200, nullable=False)],
            extends=['BaseMixin']
        )
        model.entities['Article'] = entity
        
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        content = renderer.single_template.render(
            model=model, entity=entity, entity_relationships=[],
            table_prefix='', base_model_import=None, inheritance_mode='reference'
        )
        
        assert 'class Article(BaseMixin):' in content
    
    def test_inherited_columns_not_duplicated(self):
        """Test that inherited columns are not duplicated in reference mode."""
        model = ERModel()
        model.templates = {
            'IdMixin': {
                'name': 'IdMixin',
                'package': 'common.models',
                'export_path': 'common.models_sqlalchemy',
                'columns': [Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False)],
                'source_file': 'common.toml'
            }
        }
        
        entity = Entity(
            name='Product',
            table_name='products',
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False),
                Column(name='name', type='string', db_column='name', max_length=100, nullable=False)
            ],
            extends=['IdMixin']
        )
        model.entities['Product'] = entity
        
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        content = renderer.single_template.render(
            model=model, entity=entity, entity_relationships=[],
            table_prefix='', base_model_import=None, inheritance_mode='reference'
        )
        
        id_column_count = content.count('id = Column(')
        assert id_column_count == 0, "Inherited column 'id' should not be duplicated in entity"
        assert 'name = Column(' in content


class TestFlattenModeFieldExpansion:
    """Test flatten mode field expansion - Requirement 5.3"""
    
    def test_single_template_field_expansion(self):
        """Test that template fields are expanded inline in flatten mode."""
        model = ERModel()
        model.templates = {
            'TimestampMixin': {
                'name': 'TimestampMixin',
                'package': 'common.models',
                'export_path': 'common.models_sqlalchemy',
                'columns': [
                    Column(name='created_at', type='datetime', db_column='created_at', nullable=False),
                    Column(name='updated_at', type='datetime', db_column='updated_at', nullable=True)
                ],
                'source_file': 'common.toml'
            }
        }
        
        entity = Entity(
            name='Comment',
            table_name='comments',
            columns=[
                Column(name='created_at', type='datetime', db_column='created_at', nullable=False),
                Column(name='updated_at', type='datetime', db_column='updated_at', nullable=True),
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False),
                Column(name='text', type='text', db_column='text', nullable=False)
            ],
            extends=['TimestampMixin']
        )
        entity.columns[0]._source_template = 'TimestampMixin'
        entity.columns[1]._source_template = 'TimestampMixin'
        model.entities['Comment'] = entity
        
        renderer = SQLAlchemyRenderer(inheritance_mode='flatten')
        content = renderer.single_template.render(
            model=model, entity=entity, entity_relationships=[],
            table_prefix='', base_model_import=None, inheritance_mode='flatten'
        )
        
        assert 'created_at = Column(' in content
        assert 'updated_at = Column(' in content
        assert 'text = Column(' in content
        assert 'from common.models_sqlalchemy import TimestampMixin' not in content
        assert 'class Comment(Base):' in content


class TestCrossFileTemplateReferences:
    """Test cross-file template references - Requirement 8.3"""
    
    def test_template_from_different_file(self):
        """Test that templates from different files can be referenced correctly."""
        model = ERModel()
        model.templates = {
            'SharedMixin': {
                'name': 'SharedMixin',
                'package': 'shared.models',
                'export_path': 'shared.models_sqlalchemy',
                'columns': [Column(name='version', type='integer', db_column='version', nullable=False)],
                'source_file': 'shared/models.toml'
            }
        }
        
        entity = Entity(
            name='LocalEntity',
            table_name='local_entities',
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False),
                Column(name='data', type='text', db_column='data', nullable=False)
            ],
            extends=['SharedMixin']
        )
        model.entities['LocalEntity'] = entity
        
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        content = renderer.single_template.render(
            model=model, entity=entity, entity_relationships=[],
            table_prefix='', base_model_import=None, inheritance_mode='reference'
        )
        
        assert 'from shared.models_sqlalchemy import SharedMixin' in content
        assert 'class LocalEntity(SharedMixin):' in content


class TestMissingTemplateErrorHandling:
    """Test missing template error handling - Requirement 5.5"""
    
    def test_missing_template_reference(self):
        """Test that referencing a non-existent template is handled gracefully."""
        model = ERModel()
        model.templates = {}
        
        entity = Entity(
            name='Orphan',
            table_name='orphans',
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False),
                Column(name='data', type='text', db_column='data', nullable=False)
            ],
            extends=['NonExistentMixin']
        )
        model.entities['Orphan'] = entity
        
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        content = renderer.single_template.render(
            model=model, entity=entity, entity_relationships=[],
            table_prefix='', base_model_import=None, inheritance_mode='reference'
        )
        
        assert 'class Orphan' in content


class TestEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_no_extends_field(self):
        """Test entity without extends field."""
        model = ERModel()
        model.templates = {}
        
        entity = Entity(
            name='Standalone',
            table_name='standalone',
            columns=[
                Column(name='id', type='bigint', db_column='id', is_pk=True, nullable=False),
                Column(name='name', type='string', db_column='name', max_length=100, nullable=False)
            ]
        )
        model.entities['Standalone'] = entity
        
        renderer = SQLAlchemyRenderer(inheritance_mode='reference')
        content = renderer.single_template.render(
            model=model, entity=entity, entity_relationships=[],
            table_prefix='', base_model_import=None, inheritance_mode='reference'
        )
        
        assert 'class Standalone(Base):' in content
        assert 'name = Column(' in content
