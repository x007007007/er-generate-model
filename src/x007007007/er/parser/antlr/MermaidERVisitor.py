# Generated from src/x007007007/er/parser/antlr/MermaidER.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .MermaidERParser import MermaidERParser
else:
    from MermaidERParser import MermaidERParser

# This class defines a complete generic visitor for a parse tree produced by MermaidERParser.

class MermaidERVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by MermaidERParser#diagram.
    def visitDiagram(self, ctx:MermaidERParser.DiagramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidERParser#invalidLine.
    def visitInvalidLine(self, ctx:MermaidERParser.InvalidLineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidERParser#entityDef.
    def visitEntityDef(self, ctx:MermaidERParser.EntityDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidERParser#entityName.
    def visitEntityName(self, ctx:MermaidERParser.EntityNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidERParser#columnDef.
    def visitColumnDef(self, ctx:MermaidERParser.ColumnDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidERParser#columnType.
    def visitColumnType(self, ctx:MermaidERParser.ColumnTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidERParser#columnName.
    def visitColumnName(self, ctx:MermaidERParser.ColumnNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidERParser#columnModifiers.
    def visitColumnModifiers(self, ctx:MermaidERParser.ColumnModifiersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidERParser#columnComment.
    def visitColumnComment(self, ctx:MermaidERParser.ColumnCommentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidERParser#relationship.
    def visitRelationship(self, ctx:MermaidERParser.RelationshipContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidERParser#relationSymbol.
    def visitRelationSymbol(self, ctx:MermaidERParser.RelationSymbolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidERParser#relationshipLabel.
    def visitRelationshipLabel(self, ctx:MermaidERParser.RelationshipLabelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MermaidERParser#relationshipLabelText.
    def visitRelationshipLabelText(self, ctx:MermaidERParser.RelationshipLabelTextContext):
        return self.visitChildren(ctx)



del MermaidERParser