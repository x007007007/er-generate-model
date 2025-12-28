import re
import logging
from x007007007.er.base import Parser
from x007007007.er.models import ERModel, Entity, Column, Relationship

logger = logging.getLogger(__name__)

class PlantUMLParser(Parser):
    def parse(self, content: str) -> ERModel:
        assert isinstance(content, str), "Content must be a string"
        model = ERModel()
        
        lines = content.split('\n')
        current_entity = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('@startuml') or line.startswith('@enduml'):
                continue
            
            # Entity definition: entity EntityName { ... } or class EntityName { ... }
            entity_match = re.match(r'(?:entity|class)\s+(\w+)(?:\s+as\s+"([^"]+)")?\s*\{', line)
            if entity_match:
                name = entity_match.group(1)
                comment = entity_match.group(2)
                current_entity = Entity(name=name, comment=comment)
                model.add_entity(current_entity)
                continue
            
            if line == '}':
                current_entity = None
                continue
            
            if current_entity:
                # Column: [+][*]name : type [<<markers>>]
                col_match = re.match(r'([+*]*)\s*(\w+)\s*:\s*(\w+)(?:\s+<<([^>]+)>>)?', line)
                if col_match:
                    markers = col_match.group(1)
                    col_name = col_match.group(2)
                    col_type = col_match.group(3)
                    extra_markers = col_match.group(4) or ""
                    
                    is_pk = "*" in markers
                    is_fk = "FK" in extra_markers
                    comment = None
                    if "enum:" in extra_markers:
                        comment = extra_markers # Keep enum info in comment for now
                    
                    current_entity.columns.append(Column(
                        name=col_name,
                        type=col_type,
                        is_pk=is_pk,
                        is_fk=is_fk,
                        comment=comment
                    ))
                continue
            
            # Relationship: Entity1 [card] relation [card] Entity2 : label
            # e.g. User "1" -- "0..*" Post : writes
            rel_match = re.match(r'(\w+)\s*(?:"[^"]*")?\s+([<|o*.-]+)\s+(?:"[^"]*")?\s+(\w+)\s*:\s*(.*)', line)
            if rel_match:
                left = rel_match.group(1)
                rel_type_str = rel_match.group(2)
                right = rel_match.group(3)
                label = rel_match.group(4)
                
                # Simple logic for cardinality in puml
                rel_type = "one-to-many"
                if line.count("*") >= 2 or ("*" in line and "many" in line.lower()):
                     rel_type = "many-to-many"
                elif "--" in rel_type_str and "*" not in line:
                    rel_type = "one-to-one"
                
                model.add_relationship(Relationship(
                    left_entity=left,
                    right_entity=right,
                    relation_type=rel_type,
                    right_label=label
                ))
                
        return model
