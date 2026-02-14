import logging
import re
from contextlib import contextmanager
from sqlalchemy import create_engine, inspect
from x007007007.er.base import Parser
from x007007007.er.models import ERModel, Entity, Column as ERColumn, Relationship

logger = logging.getLogger(__name__)


class DBParser(Parser):
    def __init__(self):
        self._engine = None
    
    @contextmanager
    def _get_inspector(self, db_url: str):
        """Context manager for database connection."""
        assert isinstance(db_url, str), "DB URL must be a string"
        assert len(db_url) > 0, "DB URL cannot be empty"
        
        engine = create_engine(db_url)
        self._engine = engine
        inspector = inspect(engine)
        yield inspector
        engine.dispose()
        self._engine = None
    
    def parse(self, db_url: str) -> ERModel:
        assert isinstance(db_url, str), "DB URL must be a string"
        assert len(db_url) > 0, "DB URL cannot be empty"
        
        model = ERModel()
        
        with self._get_inspector(db_url) as inspector:
            # Get all table names
            table_names = inspector.get_table_names()
            # Allow empty database for testing purposes
            
            # First pass: create entities and columns
            for table_name in table_names:
                entity = Entity(name=table_name)
                pk_constraint = inspector.get_pk_constraint(table_name)
                pk_cols = pk_constraint.get('constrained_columns', []) if pk_constraint else []
                
                # Get table comment if available (may not be supported by all databases)
                try:
                    table_info = inspector.get_table_comment(table_name)
                    if table_info and table_info.get('text'):
                        entity.comment = table_info['text']
                except NotImplementedError:
                    # Some databases don't support table comments
                    pass
                
                # Process columns
                for col in inspector.get_columns(table_name):
                    col_type = str(col['type'])
                    
                    # Extract max_length from type string if available
                    max_length = None
                    if 'VARCHAR' in col_type.upper() or 'CHAR' in col_type.upper():
                        match = re.search(r'\((\d+)\)', col_type)
                        if match:
                            max_length = int(match.group(1))
                    
                    # Extract precision and scale for decimal types
                    precision = None
                    scale = None
                    if 'DECIMAL' in col_type.upper() or 'NUMERIC' in col_type.upper():
                        match = re.search(r'\((\d+)\s*,\s*(\d+)\)', col_type)
                        if match:
                            precision = int(match.group(1))
                            scale = int(match.group(2))
                    
                    # Check if column is a foreign key
                    is_fk = False
                    for fk in inspector.get_foreign_keys(table_name):
                        if col['name'] in fk.get('constrained_columns', []):
                            is_fk = True
                            break
                    
                    entity.columns.append(ERColumn(
                        name=col['name'],
                        type=col_type,
                        is_pk=col['name'] in pk_cols,
                        is_fk=is_fk,
                        nullable=col['nullable'],
                        default=str(col['default']) if col['default'] is not None else None,
                        comment=col.get('comment'),
                        max_length=max_length,
                        precision=precision,
                        scale=scale
                    ))
                
                model.add_entity(entity)
            
            # Second pass: create relationships from foreign keys
            for table_name in table_names:
                for fk in inspector.get_foreign_keys(table_name):
                    # fk structure: {
                    #   'constrained_columns': ['local_col'],
                    #   'referred_table': 'referred_table',
                    #   'referred_columns': ['referred_col']
                    # }
                    local_cols = fk.get('constrained_columns', [])
                    referred_table = fk.get('referred_table')
                    referred_cols = fk.get('referred_columns', [])
                    
                    if not local_cols or not referred_table or not referred_cols:
                        logger.warning(f"Incomplete foreign key definition in table '{table_name}', skipping")
                        continue
                    
                    # Determine relationship type
                    # Check if referred table has a unique constraint on the referred column
                    referred_pk = inspector.get_pk_constraint(referred_table)
                    referred_pk_cols = referred_pk.get('constrained_columns', []) if referred_pk else []
                    
                    # If referred column is PK, it's likely one-to-many or one-to-one
                    # If local column is also unique, it's one-to-one
                    local_entity = model.entities.get(table_name)
                    if local_entity:
                        local_col = next((c for c in local_entity.columns if c.name == local_cols[0]), None)
                        if local_col and local_col.is_pk:
                            # Local PK -> Referred PK: one-to-one
                            relation_type = "one-to-one"
                        elif referred_cols[0] in referred_pk_cols:
                            # Local FK -> Referred PK: many-to-one (reverse: one-to-many)
                            relation_type = "one-to-many"
                        else:
                            # Default to one-to-many
                            relation_type = "one-to-many"
                    else:
                        relation_type = "one-to-many"
                    
                    # Create relationship (from referred table to local table for one-to-many)
                    if relation_type == "one-to-many":
                        # Referred table (one) -> Local table (many)
                        rel = Relationship(
                            left_entity=referred_table,
                            right_entity=table_name,
                            relation_type=relation_type,
                            left_column=referred_cols[0] if referred_cols else None,
                            right_column=local_cols[0] if local_cols else None
                        )
                    else:
                        # One-to-one: can be either direction
                        rel = Relationship(
                            left_entity=table_name,
                            right_entity=referred_table,
                            relation_type=relation_type,
                            left_column=local_cols[0] if local_cols else None,
                            right_column=referred_cols[0] if referred_cols else None
                        )
                    
                    model.add_relationship(rel)
        
        return model
