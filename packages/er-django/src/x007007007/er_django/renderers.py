"""
Django template-based renderers for ER diagrams
"""
from django.template.loader import get_template
from django.template import Context
from x007007007.er.models import ERModel
from x007007007.er.toml_writer import _serialize_toml_new_format, _toml_escape_string


class DjangoTemplateRenderer:
    """Render ER diagrams using Django templates"""
    
    def __init__(self, template_name: str):
        self.template_name = template_name
    
    def render(self, er_model: ERModel) -> str:
        template = get_template(f'er_django/{self.template_name}')
        context = {
            'entities': list(er_model.entities.values()),
            'relationships': er_model.relationships,
        }
        return template.render(context)


class MermaidRenderer(DjangoTemplateRenderer):
    def __init__(self):
        super().__init__('mermaid_er.html')


class PlantUMLRenderer(DjangoTemplateRenderer):
    def __init__(self):
        super().__init__('plantuml_er.html')


class TOMLRenderer:
    """Render ER model as TOML format (new spec)"""
    
    def render(self, er_model: ERModel) -> str:
        config = {}
        if er_model.namespace:
            config['namespace'] = er_model.namespace
        if er_model.base_package:
            config['base_package'] = er_model.base_package
        if er_model.extends_aliases:
            config['extends_aliases'] = er_model.extends_aliases
        
        entities_data = {}
        for entity_name, entity in er_model.entities.items():
            entity_dict = {}
            
            if entity.extends:
                entity_dict['extends'] = entity.extends
            
            entity_dict['table_name'] = entity.table_name
            
            if hasattr(entity, 'package') and entity.package:
                entity_dict['package'] = entity.package
            
            if entity.comment:
                entity_dict['comment'] = entity.comment
            
            entity_dict['columns'] = []
            for col in entity.columns:
                col_dict = {
                    'name': col.name,
                    'type': col.type,
                }
                
                if col.db_column != col.name:
                    col_dict['db_column'] = col.db_column
                
                if col.is_pk:
                    col_dict['primary_key'] = True
                if not col.nullable:
                    col_dict['nullable'] = False
                if col.unique:
                    col_dict['unique'] = True
                if col.default is not None:
                    col_dict['default'] = col.default
                if col.max_length is not None:
                    col_dict['max_length'] = col.max_length
                if col.precision is not None:
                    col_dict['precision'] = col.precision
                if col.scale is not None:
                    col_dict['scale'] = col.scale
                if col.comment:
                    col_dict['comment'] = col.comment
                
                entity_dict['columns'].append(col_dict)
            
            entities_data[entity_name] = entity_dict
        
        relationships_data = []
        for rel in er_model.relationships:
            rel_dict = {
                'left': rel.left_entity,
                'right': rel.right_entity,
                'type': rel.relation_type,
            }
            if rel.left_column:
                rel_dict['left_column'] = rel.left_column
            if rel.right_column:
                rel_dict['right_column'] = rel.right_column
            relationships_data.append(rel_dict)
        
        output_data = {
            'entities': entities_data,
            'relationships': relationships_data,
        }
        
        return _serialize_toml_new_format(output_data, config if config else None)