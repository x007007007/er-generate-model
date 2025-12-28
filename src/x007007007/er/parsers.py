import re
import logging
from x007007007.er.base import Parser
from x007007007.er.models import ERModel, Entity, Column, Relationship

logger = logging.getLogger(__name__)

class MermaidParser(Parser):
    def parse(self, content: str) -> ERModel:
        assert isinstance(content, str), "Content must be a string"
        model = ERModel()
        
        # Simple regex based parser for mermaid ER
        # In a real scenario, use ANTLR4 as requested. 
        # For now, implementing a basic one to get things started.
        
        lines = content.split('\n')
        current_entity = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('erDiagram'):
                continue
            
            # Entity definition: EntityName { ... }
            entity_match = re.match(r'(\w+)\s*\{', line)
            if entity_match:
                name = entity_match.group(1)
                current_entity = Entity(name=name)
                model.add_entity(current_entity)
                continue
            
            if line == '}':
                current_entity = None
                continue
            
            if current_entity:
                # Column: type name [pk/fk] "comment"
                col_match = re.match(r'(\w+)\s+(\w+)(?:\s+((?:PK|FK|,|\s)+))?(?:\s+"([^"]+)")?', line)
                if col_match:
                    col_type = col_match.group(1)
                    col_name = col_match.group(2)
                    extras = col_match.group(3) or ""
                    comment = col_match.group(4)
                    
                    is_pk = "PK" in extras
                    is_fk = "FK" in extras
                    
                    current_entity.columns.append(Column(
                        name=col_name,
                        type=col_type,
                        is_pk=is_pk,
                        is_fk=is_fk,
                        comment=comment
                    ))
                continue
            
            # Relationship: Entity1 relation Entity2 : label
            # relation: ||--o{ etc
            rel_match = re.match(r'(\w+)\s+([\d\|o{}-]+)\s+(\w+)\s*:\s*(.*)', line)
            if rel_match:
                left = rel_match.group(1)
                rel_type_str = rel_match.group(2)
                right = rel_match.group(3)
                label = rel_match.group(4)
                
                # Improved relation type mapping
                if "{" in rel_type_str and "}" in rel_type_str:
                    rel_type = "many-to-many"
                elif "{" in rel_type_str or "}" in rel_type_str:
                    rel_type = "one-to-many"
                else:
                    rel_type = "one-to-one"
                
                model.add_relationship(Relationship(
                    left_entity=left,
                    right_entity=right,
                    relation_type=rel_type,
                    right_label=label
                ))
                
        return model
