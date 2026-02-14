# Generated from src/x007007007/er/parser/antlr/PlantUMLER.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .PlantUMLERParser import PlantUMLERParser
else:
    from PlantUMLERParser import PlantUMLERParser

# This class defines a complete generic visitor for a parse tree produced by PlantUMLERParser.

class PlantUMLERVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by PlantUMLERParser#diagram.
    def visitDiagram(self, ctx:PlantUMLERParser.DiagramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLERParser#invalidLine.
    def visitInvalidLine(self, ctx:PlantUMLERParser.InvalidLineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLERParser#entityDef.
    def visitEntityDef(self, ctx:PlantUMLERParser.EntityDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLERParser#entityName.
    def visitEntityName(self, ctx:PlantUMLERParser.EntityNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLERParser#entityAlias.
    def visitEntityAlias(self, ctx:PlantUMLERParser.EntityAliasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLERParser#columnDef.
    def visitColumnDef(self, ctx:PlantUMLERParser.ColumnDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLERParser#columnMarkers.
    def visitColumnMarkers(self, ctx:PlantUMLERParser.ColumnMarkersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLERParser#columnName.
    def visitColumnName(self, ctx:PlantUMLERParser.ColumnNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLERParser#columnType.
    def visitColumnType(self, ctx:PlantUMLERParser.ColumnTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLERParser#columnStereotype.
    def visitColumnStereotype(self, ctx:PlantUMLERParser.ColumnStereotypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLERParser#stereotypeContent.
    def visitStereotypeContent(self, ctx:PlantUMLERParser.StereotypeContentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLERParser#relationship.
    def visitRelationship(self, ctx:PlantUMLERParser.RelationshipContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLERParser#cardinality.
    def visitCardinality(self, ctx:PlantUMLERParser.CardinalityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLERParser#relationSymbol.
    def visitRelationSymbol(self, ctx:PlantUMLERParser.RelationSymbolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLERParser#relationshipLabel.
    def visitRelationshipLabel(self, ctx:PlantUMLERParser.RelationshipLabelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PlantUMLERParser#relationshipLabelText.
    def visitRelationshipLabelText(self, ctx:PlantUMLERParser.RelationshipLabelTextContext):
        return self.visitChildren(ctx)



del PlantUMLERParser