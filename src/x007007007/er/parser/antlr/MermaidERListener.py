# Generated from src/x007007007/er/parser/antlr/MermaidER.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .MermaidERParser import MermaidERParser
else:
    from MermaidERParser import MermaidERParser

# This class defines a complete listener for a parse tree produced by MermaidERParser.
class MermaidERListener(ParseTreeListener):

    # Enter a parse tree produced by MermaidERParser#diagram.
    def enterDiagram(self, ctx:MermaidERParser.DiagramContext):
        pass

    # Exit a parse tree produced by MermaidERParser#diagram.
    def exitDiagram(self, ctx:MermaidERParser.DiagramContext):
        pass


    # Enter a parse tree produced by MermaidERParser#invalidLine.
    def enterInvalidLine(self, ctx:MermaidERParser.InvalidLineContext):
        pass

    # Exit a parse tree produced by MermaidERParser#invalidLine.
    def exitInvalidLine(self, ctx:MermaidERParser.InvalidLineContext):
        pass


    # Enter a parse tree produced by MermaidERParser#entityDef.
    def enterEntityDef(self, ctx:MermaidERParser.EntityDefContext):
        pass

    # Exit a parse tree produced by MermaidERParser#entityDef.
    def exitEntityDef(self, ctx:MermaidERParser.EntityDefContext):
        pass


    # Enter a parse tree produced by MermaidERParser#entityName.
    def enterEntityName(self, ctx:MermaidERParser.EntityNameContext):
        pass

    # Exit a parse tree produced by MermaidERParser#entityName.
    def exitEntityName(self, ctx:MermaidERParser.EntityNameContext):
        pass


    # Enter a parse tree produced by MermaidERParser#columnDef.
    def enterColumnDef(self, ctx:MermaidERParser.ColumnDefContext):
        pass

    # Exit a parse tree produced by MermaidERParser#columnDef.
    def exitColumnDef(self, ctx:MermaidERParser.ColumnDefContext):
        pass


    # Enter a parse tree produced by MermaidERParser#columnType.
    def enterColumnType(self, ctx:MermaidERParser.ColumnTypeContext):
        pass

    # Exit a parse tree produced by MermaidERParser#columnType.
    def exitColumnType(self, ctx:MermaidERParser.ColumnTypeContext):
        pass


    # Enter a parse tree produced by MermaidERParser#columnName.
    def enterColumnName(self, ctx:MermaidERParser.ColumnNameContext):
        pass

    # Exit a parse tree produced by MermaidERParser#columnName.
    def exitColumnName(self, ctx:MermaidERParser.ColumnNameContext):
        pass


    # Enter a parse tree produced by MermaidERParser#columnModifiers.
    def enterColumnModifiers(self, ctx:MermaidERParser.ColumnModifiersContext):
        pass

    # Exit a parse tree produced by MermaidERParser#columnModifiers.
    def exitColumnModifiers(self, ctx:MermaidERParser.ColumnModifiersContext):
        pass


    # Enter a parse tree produced by MermaidERParser#columnComment.
    def enterColumnComment(self, ctx:MermaidERParser.ColumnCommentContext):
        pass

    # Exit a parse tree produced by MermaidERParser#columnComment.
    def exitColumnComment(self, ctx:MermaidERParser.ColumnCommentContext):
        pass


    # Enter a parse tree produced by MermaidERParser#relationship.
    def enterRelationship(self, ctx:MermaidERParser.RelationshipContext):
        pass

    # Exit a parse tree produced by MermaidERParser#relationship.
    def exitRelationship(self, ctx:MermaidERParser.RelationshipContext):
        pass


    # Enter a parse tree produced by MermaidERParser#relationSymbol.
    def enterRelationSymbol(self, ctx:MermaidERParser.RelationSymbolContext):
        pass

    # Exit a parse tree produced by MermaidERParser#relationSymbol.
    def exitRelationSymbol(self, ctx:MermaidERParser.RelationSymbolContext):
        pass


    # Enter a parse tree produced by MermaidERParser#relationshipLabel.
    def enterRelationshipLabel(self, ctx:MermaidERParser.RelationshipLabelContext):
        pass

    # Exit a parse tree produced by MermaidERParser#relationshipLabel.
    def exitRelationshipLabel(self, ctx:MermaidERParser.RelationshipLabelContext):
        pass


    # Enter a parse tree produced by MermaidERParser#relationshipLabelText.
    def enterRelationshipLabelText(self, ctx:MermaidERParser.RelationshipLabelTextContext):
        pass

    # Exit a parse tree produced by MermaidERParser#relationshipLabelText.
    def exitRelationshipLabelText(self, ctx:MermaidERParser.RelationshipLabelTextContext):
        pass



del MermaidERParser