"""
Django template-based renderers for ER diagrams
"""
from django.template.loader import get_template
from django.template import Context
from x007007007.er.models import ERModel
import toml


class DjangoTemplateRenderer:
    """Render ER diagrams using Django templates"""
    
    def __init__(self, template_name: str):
        self.template_name = template_name
    
    def render(self, er_model: ERModel) -> str:
        """
        Render ER model using Django template
        
        Args:
            er_model: ERModel instance
            
        Returns:
            Rendered diagram as string
        """
        # Load template
        template = get_template(f'er_django/{self.template_name}')
        
        # Prepare context
        context = {
            'entities': list(er_model.entities.values()),
            'relationships': er_model.relationships,
        }
        
        # Render template
        return template.render(context)


class MermaidRenderer(DjangoTemplateRenderer):
    """Render Mermaid ER diagrams using Django templates"""
    
    def __init__(self):
        super().__init__('mermaid_er.html')


class PlantUMLRenderer(DjangoTemplateRenderer):
    """Render PlantUML ER diagrams using Django templates"""
    
    def __init__(self):
        super().__init__('plantuml_er.html')


class TOMLRenderer:
    """Render ER model as TOML format"""
    
    def render(self, er_model: ERModel) -> str:
        """
        Render ER model as TOML format
        
        Args:
            er_model: ERModel instance
            
        Returns:
            TOML formatted string
        """
        data = {}
        
        # Add entities
        entities_data = {}
        for entity_name, entity in er_model.entities.items():
            entity_dict = {
                'columns': []
            }
            
            # Add columns
            for col in entity.columns:
                col_dict = {
                    'name': col.name,
                    'type': col.type,
                }
                
                # Add optional fields
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
        
        if entities_data:
            data['entities'] = entities_data
        
        # Add relationships
        if er_model.relationships:
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
            
            data['relationships'] = relationships_data
        
        # Convert to TOML string
        return toml.dumps(data)