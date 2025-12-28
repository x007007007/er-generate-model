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
    max_length: Optional[int] = None  # For VARCHAR, CHAR, etc.
    precision: Optional[int] = None  # For DECIMAL, NUMERIC
    scale: Optional[int] = None  # For DECIMAL, NUMERIC
    unique: bool = False
    indexed: bool = False

@dataclass
class Relationship:
    left_entity: str
    right_entity: str
    relation_type: str  # one-to-one, one-to-many, many-to-many
    left_label: Optional[str] = None
    right_label: Optional[str] = None
    left_column: Optional[str] = None  # Foreign key column name in left entity
    right_column: Optional[str] = None  # Foreign key column name in right entity
    left_cardinality: Optional[str] = None  # "1", "0..1", "*", "0..*"
    right_cardinality: Optional[str] = None

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
        assert isinstance(entity, Entity), "entity must be an Entity instance"
        assert entity.name not in self.entities, f"Entity '{entity.name}' already exists"
        self.entities[entity.name] = entity

    def add_relationship(self, rel: Relationship):
        assert isinstance(rel, Relationship), "rel must be a Relationship instance"
        assert rel.left_entity in self.entities, f"Left entity '{rel.left_entity}' does not exist"
        assert rel.right_entity in self.entities, f"Right entity '{rel.right_entity}' does not exist"
        self.relationships.append(rel)
    
    def validate(self) -> List[str]:
        """Validate the model and return list of errors (empty if valid)."""
        errors = []
        for rel in self.relationships:
            if rel.left_entity not in self.entities:
                errors.append(f"Relationship references non-existent entity: {rel.left_entity}")
            if rel.right_entity not in self.entities:
                errors.append(f"Relationship references non-existent entity: {rel.right_entity}")
            if rel.left_column and rel.left_entity in self.entities:
                entity = self.entities[rel.left_entity]
                if not any(c.name == rel.left_column for c in entity.columns):
                    errors.append(f"Relationship references non-existent column '{rel.left_column}' in entity '{rel.left_entity}'")
            if rel.right_column and rel.right_entity in self.entities:
                entity = self.entities[rel.right_entity]
                if not any(c.name == rel.right_column for c in entity.columns):
                    errors.append(f"Relationship references non-existent column '{rel.right_column}' in entity '{rel.right_entity}'")
        return errors
