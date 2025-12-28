# Generated from src/x007007007/er/parser/antlr/PlantUMLER.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .PlantUMLERParser import PlantUMLERParser
else:
    from PlantUMLERParser import PlantUMLERParser

# This class defines a complete listener for a parse tree produced by PlantUMLERParser.
class PlantUMLERListener(ParseTreeListener):

    # Enter a parse tree produced by PlantUMLERParser#diagram.
    def enterDiagram(self, ctx:PlantUMLERParser.DiagramContext):
        pass

    # Exit a parse tree produced by PlantUMLERParser#diagram.
    def exitDiagram(self, ctx:PlantUMLERParser.DiagramContext):
        pass


    # Enter a parse tree produced by PlantUMLERParser#invalidLine.
    def enterInvalidLine(self, ctx:PlantUMLERParser.InvalidLineContext):
        pass

    # Exit a parse tree produced by PlantUMLERParser#invalidLine.
    def exitInvalidLine(self, ctx:PlantUMLERParser.InvalidLineContext):
        pass


    # Enter a parse tree produced by PlantUMLERParser#entityDef.
    def enterEntityDef(self, ctx:PlantUMLERParser.EntityDefContext):
        pass

    # Exit a parse tree produced by PlantUMLERParser#entityDef.
    def exitEntityDef(self, ctx:PlantUMLERParser.EntityDefContext):
        pass


    # Enter a parse tree produced by PlantUMLERParser#entityName.
    def enterEntityName(self, ctx:PlantUMLERParser.EntityNameContext):
        pass

    # Exit a parse tree produced by PlantUMLERParser#entityName.
    def exitEntityName(self, ctx:PlantUMLERParser.EntityNameContext):
        pass


    # Enter a parse tree produced by PlantUMLERParser#entityAlias.
    def enterEntityAlias(self, ctx:PlantUMLERParser.EntityAliasContext):
        pass

    # Exit a parse tree produced by PlantUMLERParser#entityAlias.
    def exitEntityAlias(self, ctx:PlantUMLERParser.EntityAliasContext):
        pass


    # Enter a parse tree produced by PlantUMLERParser#columnDef.
    def enterColumnDef(self, ctx:PlantUMLERParser.ColumnDefContext):
        pass

    # Exit a parse tree produced by PlantUMLERParser#columnDef.
    def exitColumnDef(self, ctx:PlantUMLERParser.ColumnDefContext):
        pass


    # Enter a parse tree produced by PlantUMLERParser#columnMarkers.
    def enterColumnMarkers(self, ctx:PlantUMLERParser.ColumnMarkersContext):
        pass

    # Exit a parse tree produced by PlantUMLERParser#columnMarkers.
    def exitColumnMarkers(self, ctx:PlantUMLERParser.ColumnMarkersContext):
        pass


    # Enter a parse tree produced by PlantUMLERParser#columnName.
    def enterColumnName(self, ctx:PlantUMLERParser.ColumnNameContext):
        pass

    # Exit a parse tree produced by PlantUMLERParser#columnName.
    def exitColumnName(self, ctx:PlantUMLERParser.ColumnNameContext):
        pass


    # Enter a parse tree produced by PlantUMLERParser#columnType.
    def enterColumnType(self, ctx:PlantUMLERParser.ColumnTypeContext):
        pass

    # Exit a parse tree produced by PlantUMLERParser#columnType.
    def exitColumnType(self, ctx:PlantUMLERParser.ColumnTypeContext):
        pass


    # Enter a parse tree produced by PlantUMLERParser#columnStereotype.
    def enterColumnStereotype(self, ctx:PlantUMLERParser.ColumnStereotypeContext):
        pass

    # Exit a parse tree produced by PlantUMLERParser#columnStereotype.
    def exitColumnStereotype(self, ctx:PlantUMLERParser.ColumnStereotypeContext):
        pass


    # Enter a parse tree produced by PlantUMLERParser#stereotypeContent.
    def enterStereotypeContent(self, ctx:PlantUMLERParser.StereotypeContentContext):
        pass

    # Exit a parse tree produced by PlantUMLERParser#stereotypeContent.
    def exitStereotypeContent(self, ctx:PlantUMLERParser.StereotypeContentContext):
        pass


    # Enter a parse tree produced by PlantUMLERParser#relationship.
    def enterRelationship(self, ctx:PlantUMLERParser.RelationshipContext):
        pass

    # Exit a parse tree produced by PlantUMLERParser#relationship.
    def exitRelationship(self, ctx:PlantUMLERParser.RelationshipContext):
        pass


    # Enter a parse tree produced by PlantUMLERParser#cardinality.
    def enterCardinality(self, ctx:PlantUMLERParser.CardinalityContext):
        pass

    # Exit a parse tree produced by PlantUMLERParser#cardinality.
    def exitCardinality(self, ctx:PlantUMLERParser.CardinalityContext):
        pass


    # Enter a parse tree produced by PlantUMLERParser#relationSymbol.
    def enterRelationSymbol(self, ctx:PlantUMLERParser.RelationSymbolContext):
        pass

    # Exit a parse tree produced by PlantUMLERParser#relationSymbol.
    def exitRelationSymbol(self, ctx:PlantUMLERParser.RelationSymbolContext):
        pass


    # Enter a parse tree produced by PlantUMLERParser#relationshipLabel.
    def enterRelationshipLabel(self, ctx:PlantUMLERParser.RelationshipLabelContext):
        pass

    # Exit a parse tree produced by PlantUMLERParser#relationshipLabel.
    def exitRelationshipLabel(self, ctx:PlantUMLERParser.RelationshipLabelContext):
        pass


    # Enter a parse tree produced by PlantUMLERParser#relationshipLabelText.
    def enterRelationshipLabelText(self, ctx:PlantUMLERParser.RelationshipLabelTextContext):
        pass

    # Exit a parse tree produced by PlantUMLERParser#relationshipLabelText.
    def exitRelationshipLabelText(self, ctx:PlantUMLERParser.RelationshipLabelTextContext):
        pass



del PlantUMLERParser