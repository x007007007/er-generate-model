"""
ANTLR-based Mermaid ER Diagram Parser
This parser uses ANTLR-generated code to parse Mermaid ER diagrams.
"""
import logging
import sys
from pathlib import Path

# Import ANTLR generated code
# Add generated directory to path if it exists
generated_path = Path(__file__).parent / "generated"
if generated_path.exists():
    sys.path.insert(0, str(generated_path))

from MermaidERLexer import MermaidERLexer
from MermaidERParser import MermaidERParser
from MermaidERVisitor import MermaidERVisitor

from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener as BaseErrorListener
from x007007007.er.base import Parser
from x007007007.er.models import ERModel, Entity, Column, Relationship

logger = logging.getLogger(__name__)


class ErrorListener(BaseErrorListener):
    """Error listener that logs errors but doesn't stop parsing."""
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        logger.warning(f"Parse error at line {line}:{column} - {msg}")
        # Don't raise exception, allow parsing to continue


class MermaidERModelVisitor(MermaidERVisitor):
    """Visitor to build ERModel from ANTLR parse tree."""
    
    def __init__(self):
        super().__init__()
        self.model = ERModel()
        self.current_entity = None
    
    def visitDiagram(self, ctx):
        """Visit diagram root."""
        # Collect all children
        children = list(ctx.getChildren())
        
        # First pass: collect all entities
        for child in children:
            # Check if this is an entityDef by trying to visit it
            try:
                if hasattr(child, 'entityName') and hasattr(child, 'columnDef'):
                    self.visitEntityDef(child)
            except:
                pass  # Not an entityDef
        
        # Second pass: process relationships (entities must exist first)
        for child in children:
            # Check if this is a relationship
            try:
                if hasattr(child, 'relationSymbol'):
                    self.visitRelationship(child)
            except:
                pass  # Not a relationship
        
        return self.model
    
    def visitEntityDef(self, ctx):
        """Visit entity definition."""
        entity_name_ctx = ctx.entityName()
        if entity_name_ctx:
            entity_name = entity_name_ctx.getText()
            self.current_entity = Entity(name=entity_name)
            self.model.add_entity(self.current_entity)
            
            # Visit column definitions
            for col_ctx in ctx.columnDef():
                self.visitColumnDef(col_ctx)
            
            self.current_entity = None
        return self.model
    
    def visitColumnDef(self, ctx):
        """Visit column definition."""
        if not self.current_entity:
            return
        
        column_type = ctx.columnType().getText() if ctx.columnType() else None
        column_name = ctx.columnName().getText() if ctx.columnName() else None
        
        if not column_type or not column_name:
            return
        
        # Check for modifiers
        is_pk = False
        is_fk = False
        is_unique = False
        if ctx.columnModifiers():
            modifiers_text = ctx.columnModifiers().getText()
            is_pk = 'PK' in modifiers_text
            is_fk = 'FK' in modifiers_text
            is_unique = 'UK' in modifiers_text
        
        # Get comment
        comment = None
        if ctx.columnComment():
            comment_text = ctx.columnComment().getText()
            # Remove quotes
            comment = comment_text.strip('"')
        
        column = Column(
            name=column_name,
            type=column_type,
            is_pk=is_pk,
            is_fk=is_fk,
            unique=is_unique,
            comment=comment
        )
        self.current_entity.columns.append(column)
    
    def visitRelationship(self, ctx):
        """Visit relationship definition."""
        entity_names = ctx.entityName()
        if len(entity_names) < 2:
            return
        
        left_entity = entity_names[0].getText()
        right_entity = entity_names[1].getText()
        
        # Determine relationship type from symbol
        rel_type = "one-to-many"  # default
        if ctx.relationSymbol():
            symbol_ctx = ctx.relationSymbol()
            # Check which type of relation symbol it is
            if symbol_ctx.ONE_TO_ONE():
                rel_type = "one-to-one"
            elif symbol_ctx.ONE_TO_MANY():
                rel_type = "one-to-many"
            elif symbol_ctx.MANY_TO_MANY():
                rel_type = "many-to-many"
            elif symbol_ctx.MANY_TO_ONE():
                rel_type = "many-to-one"
        
        # Get label
        label = None
        if ctx.relationshipLabel():
            label_text = ctx.relationshipLabel().getText()
            label = label_text.strip('"') if label_text.startswith('"') else label_text
        
        # Try to find foreign key column
        # For one-to-many: FK is in right_entity, referencing left_entity
        # For many-to-one: FK is in left_entity, referencing right_entity
        # For one-to-one: FK can be in either entity, prefer right_entity
        left_column = None
        right_column = None
        
        if rel_type == "one-to-many":
            # FK is in right_entity
            if right_entity in self.model.entities:
                right_entity_obj = self.model.entities[right_entity]
                # Look for a column that matches the left entity name
                left_entity_lower = left_entity.lower()
                
                # Try multiple matching strategies, preferring more specific matches
                best_match = None
                best_score = 0
                
                for col in right_entity_obj.columns:
                    if not col.is_fk:
                        continue
                    
                    col_name_lower = col.name.lower()
                    score = 0
                    
                    # Strategy 1: Exact match with entity name (highest score)
                    if left_entity_lower == col_name_lower.replace('_id', '').replace('_', ''):
                        score = 100
                    # Strategy 2: Entity name is substring of column name
                    elif left_entity_lower in col_name_lower:
                        score = 50
                    else:
                        # Strategy 3: Match with partial entity name (e.g., "session" in "ConversationSessionModel")
                        # Split entity name by capital letters and count matching parts
                        import re
                        entity_parts = re.findall('[A-Z][a-z]*', left_entity)
                        for part in entity_parts:
                            part_lower = part.lower()
                            if part_lower in col_name_lower:
                                # Sum up lengths of all matching parts
                                score += len(part)
                    
                    if score > best_score:
                        best_score = score
                        best_match = col.name
                
                right_column = best_match
        
        elif rel_type == "one-to-one":
            # FK can be in either entity, try both
            # First try right_entity
            if right_entity in self.model.entities:
                right_entity_obj = self.model.entities[right_entity]
                left_entity_lower = left_entity.lower()
                
                best_match = None
                best_score = 0
                
                for col in right_entity_obj.columns:
                    if not col.is_fk:
                        continue
                    
                    col_name_lower = col.name.lower()
                    score = 0
                    
                    if left_entity_lower == col_name_lower.replace('_id', '').replace('_', ''):
                        score = 100
                    elif left_entity_lower in col_name_lower:
                        score = 50
                    else:
                        import re
                        entity_parts = re.findall('[A-Z][a-z]*', left_entity)
                        for part in entity_parts:
                            part_lower = part.lower()
                            if part_lower in col_name_lower:
                                score += len(part)
                    
                    if score > best_score:
                        best_score = score
                        best_match = col.name
                
                right_column = best_match
            
            # If not found in right_entity, try left_entity
            if not right_column and left_entity in self.model.entities:
                left_entity_obj = self.model.entities[left_entity]
                right_entity_lower = right_entity.lower()
                
                best_match = None
                best_score = 0
                
                for col in left_entity_obj.columns:
                    if not col.is_fk:
                        continue
                    
                    col_name_lower = col.name.lower()
                    score = 0
                    
                    if right_entity_lower == col_name_lower.replace('_id', '').replace('_', ''):
                        score = 100
                    elif right_entity_lower in col_name_lower:
                        score = 50
                    else:
                        import re
                        entity_parts = re.findall('[A-Z][a-z]*', right_entity)
                        for part in entity_parts:
                            part_lower = part.lower()
                            if part_lower in col_name_lower:
                                score += len(part)
                    
                    if score > best_score:
                        best_score = score
                        best_match = col.name
                
                left_column = best_match
                        
        elif rel_type == "many-to-one":
            # FK is in left_entity
            if left_entity in self.model.entities:
                left_entity_obj = self.model.entities[left_entity]
                # Look for a column that matches the right entity name
                right_entity_lower = right_entity.lower()
                
                best_match = None
                best_score = 0
                
                for col in left_entity_obj.columns:
                    if not col.is_fk:
                        continue
                    
                    col_name_lower = col.name.lower()
                    score = 0
                    
                    # Strategy 1: Exact match
                    if right_entity_lower == col_name_lower.replace('_id', '').replace('_', ''):
                        score = 100
                    # Strategy 2: Entity name is substring
                    elif right_entity_lower in col_name_lower:
                        score = 50
                    else:
                        # Strategy 3: Partial match - sum up all matching parts
                        import re
                        entity_parts = re.findall('[A-Z][a-z]*', right_entity)
                        for part in entity_parts:
                            part_lower = part.lower()
                            if part_lower in col_name_lower:
                                score += len(part)
                    
                    if score > best_score:
                        best_score = score
                        best_match = col.name
                
                left_column = best_match
        
        relationship = Relationship(
            left_entity=left_entity,
            right_entity=right_entity,
            relation_type=rel_type,
            right_label=label,
            left_column=left_column,
            right_column=right_column
        )
        self.model.add_relationship(relationship)


class MermaidAntlrParser(Parser):
    """
    ANTLR-based parser for Mermaid ER diagrams.
    Requires ANTLR generated code to be available.
    Run tools/generate_antlr.bat to generate the required parser code.
    """
    
    def parse(self, content: str) -> ERModel:
        assert isinstance(content, str), "Content must be a string"
        assert len(content) > 0, "Content cannot be empty"
        
        # Use ANTLR parser
        input_stream = InputStream(content)
        lexer = MermaidERLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = MermaidERParser(token_stream)
        
        # Enable error recovery - continue parsing even on errors
        parser.removeErrorListeners()
        parser.addErrorListener(ErrorListener())
        
        # Parse
        tree = parser.diagram()
        
        # Visit tree to build model
        visitor = MermaidERModelVisitor()
        model = visitor.visit(tree)
        
        return model
