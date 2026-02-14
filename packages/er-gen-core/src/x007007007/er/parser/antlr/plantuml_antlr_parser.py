"""
ANTLR-based PlantUML ER Diagram Parser
This parser uses ANTLR-generated code to parse PlantUML ER diagrams.
"""
import logging
import sys
from pathlib import Path

# Import ANTLR generated code
# Add generated directory to path if it exists
generated_path = Path(__file__).parent / "generated"
if generated_path.exists():
    sys.path.insert(0, str(generated_path))

from PlantUMLERLexer import PlantUMLERLexer
from PlantUMLERParser import PlantUMLERParser
from PlantUMLERVisitor import PlantUMLERVisitor

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


class PlantUMLERModelVisitor(PlantUMLERVisitor):
    """Visitor to build ERModel from ANTLR parse tree."""
    
    def __init__(self):
        super().__init__()
        self.model = ERModel()
        self.entities = {}  # Track entities for relationship processing
    
    def visitDiagram(self, ctx):
        """Visit diagram root."""
        # Collect all children
        children = list(ctx.getChildren())
        
        # First pass: collect all entities
        for child in children:
            # Check if this is an entityDef by checking for entityName attribute
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
        if not entity_name_ctx:
            return None
        
        entity_name = entity_name_ctx.IDENTIFIER().getText()
        
        # Get alias/comment if present
        comment = None
        if ctx.entityAlias():
            alias_ctx = ctx.entityAlias()
            if alias_ctx.STRING():
                comment = alias_ctx.STRING().getText().strip('"')
        
        entity = Entity(name=entity_name, comment=comment)
        
        # Process columns
        for col_ctx in ctx.columnDef():
            col = self.visitColumnDef(col_ctx)
            if col:
                entity.columns.append(col)
        
        self.model.add_entity(entity)
        self.entities[entity_name] = entity
        return entity
    
    def visitColumnDef(self, ctx):
        """Visit column definition."""
        col_name_ctx = ctx.columnName()
        col_name = col_name_ctx.IDENTIFIER().getText()
        
        col_type_ctx = ctx.columnType()
        col_type = col_type_ctx.IDENTIFIER().getText()
        
        # Check for PK marker
        is_pk = False
        if ctx.columnMarkers():
            markers_text = ctx.columnMarkers().getText()
            if '*' in markers_text:
                is_pk = True
        
        # Check for FK in stereotype
        is_fk = False
        comment = None
        if ctx.columnStereotype():
            stereotype_ctx = ctx.columnStereotype()
            content = stereotype_ctx.stereotypeContent()
            if content:
                content_text = content.getText()
                if "FK" in content_text:
                    is_fk = True
                if "enum:" in content_text:
                    comment = content_text
        
        return Column(
            name=col_name,
            type=col_type,
            is_pk=is_pk,
            is_fk=is_fk,
            comment=comment
        )
    
    def visitRelationship(self, ctx):
        """Visit relationship definition."""
        left_entity_ctx = ctx.entityName(0)
        right_entity_ctx = ctx.entityName(1)
        left_entity = left_entity_ctx.IDENTIFIER().getText()
        right_entity = right_entity_ctx.IDENTIFIER().getText()
        
        # Get relationship symbol
        rel_symbol_ctx = ctx.relationSymbol()
        rel_type = self._determine_relation_type(rel_symbol_ctx)
        
        # Get cardinalities
        left_card = None
        right_card = None
        card_ctxs = ctx.cardinality()
        if len(card_ctxs) >= 2:
            left_card = self._extract_cardinality(card_ctxs[0])
            right_card = self._extract_cardinality(card_ctxs[1])
        elif len(card_ctxs) == 1:
            right_card = self._extract_cardinality(card_ctxs[0])
        
        # Get label
        label = None
        if ctx.relationshipLabel():
            label_ctx = ctx.relationshipLabel()
            if label_ctx.STRING():
                label = label_ctx.STRING().getText().strip('"')
            elif label_ctx.relationshipLabelText():
                label = label_ctx.relationshipLabelText().getText()
        
        # Try to find foreign key column in right entity
        right_column = None
        if right_entity in self.entities:
            right_entity_obj = self.entities[right_entity]
            for col in right_entity_obj.columns:
                if col.is_fk:
                    if left_entity.lower() in col.name.lower() or col.name.endswith('_id'):
                        right_column = col.name
                        break
        
        self.model.add_relationship(Relationship(
            left_entity=left_entity,
            right_entity=right_entity,
            relation_type=rel_type,
            right_label=label,
            left_cardinality=left_card,
            right_cardinality=right_card,
            right_column=right_column
        ))
    
    def _determine_relation_type(self, rel_symbol_ctx):
        """Determine relationship type from symbol."""
        symbol_text = rel_symbol_ctx.getText()
        
        if symbol_text == '||--||':
            return "one-to-one"
        elif symbol_text in ('||--o{', '||--}o'):
            return "one-to-many"
        elif symbol_text in ('}|--|{', '}o--o{'):
            return "many-to-many"
        elif symbol_text in ('}o--||', '}o--||'):
            return "many-to-one"
        elif symbol_text == '--':
            return "one-to-one"  # Default for simple relation
        else:
            return "one-to-many"  # Default
    
    def _extract_cardinality(self, card_ctx):
        """Extract cardinality from context."""
        if card_ctx.CARDINALITY():
            return card_ctx.CARDINALITY().getText().strip('"')
        elif card_ctx.STRING():
            return card_ctx.STRING().getText().strip('"')
        return None


class PlantUMLAntlrParser(Parser):
    """ANTLR-based PlantUML ER diagram parser."""
    
    def parse(self, content: str) -> ERModel:
        """Parse PlantUML ER diagram content."""
        assert isinstance(content, str), "Content must be a string"
        assert len(content) > 0, "Content cannot be empty"
        
        input_stream = InputStream(content)
        lexer = PlantUMLERLexer(input_stream)
        lexer.removeErrorListeners()
        lexer.addErrorListener(ErrorListener())
        
        token_stream = CommonTokenStream(lexer)
        parser = PlantUMLERParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(ErrorListener())
        
        tree = parser.diagram()
        visitor = PlantUMLERModelVisitor()
        model = visitor.visitDiagram(tree)
        
        return model

