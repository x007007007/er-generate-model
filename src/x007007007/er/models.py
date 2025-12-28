from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class Column:
    name: str
    type: str
    is_pk: bool = False
    is_fk: bool = False
    nullable: bool = True
    comment: Optional[str] = None
    default: Optional[str] = None

@dataclass
class Relationship:
    left_entity: str
    right_entity: str
    relation_type: str  # one-to-one, one-to-many, many-to-many
    left_label: Optional[str] = None
    right_label: Optional[str] = None

@dataclass
class Entity:
    name: str
    columns: List[Column] = field(default_factory=list)
    comment: Optional[str] = None

@dataclass
class ERModel:
    entities: Dict[str, Entity] = field(default_factory=dict)
    relationships: List[Relationship] = field(default_factory=list)

    def add_entity(self, entity: Entity):
        self.entities[entity.name] = entity

    def add_relationship(self, rel: Relationship):
        self.relationships.append(rel)
