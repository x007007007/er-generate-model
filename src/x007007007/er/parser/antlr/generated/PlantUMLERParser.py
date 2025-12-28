# Generated from src/x007007007/er/parser/antlr/PlantUMLER.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,26,132,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,1,0,1,0,1,0,1,0,5,0,37,8,0,10,0,12,0,40,9,0,
        1,0,1,0,1,0,1,1,1,1,3,1,47,8,1,1,2,1,2,1,2,3,2,52,8,2,1,2,1,2,5,
        2,56,8,2,10,2,12,2,59,9,2,1,2,1,2,1,3,1,3,1,4,1,4,1,4,1,5,3,5,69,
        8,5,1,5,1,5,1,5,1,5,3,5,75,8,5,1,6,4,6,78,8,6,11,6,12,6,79,1,7,1,
        7,1,8,1,8,1,9,1,9,1,9,1,9,1,10,1,10,1,10,1,10,1,10,5,10,95,8,10,
        10,10,12,10,98,9,10,3,10,100,8,10,1,11,1,11,3,11,104,8,11,1,11,1,
        11,3,11,108,8,11,1,11,1,11,3,11,112,8,11,1,12,1,12,1,13,1,13,1,14,
        1,14,1,14,1,14,3,14,122,8,14,1,15,1,15,1,15,5,15,127,8,15,10,15,
        12,15,130,9,15,1,15,0,0,16,0,2,4,6,8,10,12,14,16,18,20,22,24,26,
        28,30,0,5,5,0,1,3,8,8,10,12,15,19,21,26,1,0,10,11,1,0,13,14,2,0,
        15,15,22,22,1,0,16,20,131,0,32,1,0,0,0,2,46,1,0,0,0,4,48,1,0,0,0,
        6,62,1,0,0,0,8,64,1,0,0,0,10,68,1,0,0,0,12,77,1,0,0,0,14,81,1,0,
        0,0,16,83,1,0,0,0,18,85,1,0,0,0,20,89,1,0,0,0,22,101,1,0,0,0,24,
        113,1,0,0,0,26,115,1,0,0,0,28,121,1,0,0,0,30,123,1,0,0,0,32,38,5,
        8,0,0,33,37,3,4,2,0,34,37,3,22,11,0,35,37,3,2,1,0,36,33,1,0,0,0,
        36,34,1,0,0,0,36,35,1,0,0,0,37,40,1,0,0,0,38,36,1,0,0,0,38,39,1,
        0,0,0,39,41,1,0,0,0,40,38,1,0,0,0,41,42,5,9,0,0,42,43,5,0,0,1,43,
        1,1,0,0,0,44,47,5,21,0,0,45,47,8,0,0,0,46,44,1,0,0,0,46,45,1,0,0,
        0,47,3,1,0,0,0,48,49,7,1,0,0,49,51,3,6,3,0,50,52,3,8,4,0,51,50,1,
        0,0,0,51,52,1,0,0,0,52,53,1,0,0,0,53,57,5,1,0,0,54,56,3,10,5,0,55,
        54,1,0,0,0,56,59,1,0,0,0,57,55,1,0,0,0,57,58,1,0,0,0,58,60,1,0,0,
        0,59,57,1,0,0,0,60,61,5,2,0,0,61,5,1,0,0,0,62,63,5,21,0,0,63,7,1,
        0,0,0,64,65,5,12,0,0,65,66,5,22,0,0,66,9,1,0,0,0,67,69,3,12,6,0,
        68,67,1,0,0,0,68,69,1,0,0,0,69,70,1,0,0,0,70,71,3,14,7,0,71,72,5,
        3,0,0,72,74,3,16,8,0,73,75,3,18,9,0,74,73,1,0,0,0,74,75,1,0,0,0,
        75,11,1,0,0,0,76,78,7,2,0,0,77,76,1,0,0,0,78,79,1,0,0,0,79,77,1,
        0,0,0,79,80,1,0,0,0,80,13,1,0,0,0,81,82,5,21,0,0,82,15,1,0,0,0,83,
        84,5,21,0,0,84,17,1,0,0,0,85,86,5,4,0,0,86,87,3,20,10,0,87,88,5,
        5,0,0,88,19,1,0,0,0,89,99,5,21,0,0,90,91,5,3,0,0,91,96,5,21,0,0,
        92,93,5,6,0,0,93,95,5,21,0,0,94,92,1,0,0,0,95,98,1,0,0,0,96,94,1,
        0,0,0,96,97,1,0,0,0,97,100,1,0,0,0,98,96,1,0,0,0,99,90,1,0,0,0,99,
        100,1,0,0,0,100,21,1,0,0,0,101,103,3,6,3,0,102,104,3,24,12,0,103,
        102,1,0,0,0,103,104,1,0,0,0,104,105,1,0,0,0,105,107,3,26,13,0,106,
        108,3,24,12,0,107,106,1,0,0,0,107,108,1,0,0,0,108,109,1,0,0,0,109,
        111,3,6,3,0,110,112,3,28,14,0,111,110,1,0,0,0,111,112,1,0,0,0,112,
        23,1,0,0,0,113,114,7,3,0,0,114,25,1,0,0,0,115,116,7,4,0,0,116,27,
        1,0,0,0,117,118,5,3,0,0,118,122,5,22,0,0,119,120,5,3,0,0,120,122,
        3,30,15,0,121,117,1,0,0,0,121,119,1,0,0,0,122,29,1,0,0,0,123,128,
        5,21,0,0,124,125,5,7,0,0,125,127,5,21,0,0,126,124,1,0,0,0,127,130,
        1,0,0,0,128,126,1,0,0,0,128,129,1,0,0,0,129,31,1,0,0,0,130,128,1,
        0,0,0,15,36,38,46,51,57,68,74,79,96,99,103,107,111,121,128
    ]

class PlantUMLERParser ( Parser ):

    grammarFileName = "PlantUMLER.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'{'", "'}'", "':'", "'<<'", "'>>'", "','", 
                     "'-'", "'@startuml'", "'@enduml'", "'entity'", "'class'", 
                     "'as'", "'*'", "'+'", "<INVALID>", "'||--||'", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'--'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "STARTUML", "ENDUM", "ENTITY", "CLASS", "AS", "PK_MARKER", 
                      "VISIBILITY_MARKER", "CARDINALITY", "ONE_TO_ONE", 
                      "ONE_TO_MANY", "MANY_TO_MANY", "MANY_TO_ONE", "SIMPLE_RELATION", 
                      "IDENTIFIER", "STRING", "WS", "NEWLINE", "COMMENT", 
                      "ENDUML" ]

    RULE_diagram = 0
    RULE_invalidLine = 1
    RULE_entityDef = 2
    RULE_entityName = 3
    RULE_entityAlias = 4
    RULE_columnDef = 5
    RULE_columnMarkers = 6
    RULE_columnName = 7
    RULE_columnType = 8
    RULE_columnStereotype = 9
    RULE_stereotypeContent = 10
    RULE_relationship = 11
    RULE_cardinality = 12
    RULE_relationSymbol = 13
    RULE_relationshipLabel = 14
    RULE_relationshipLabelText = 15

    ruleNames =  [ "diagram", "invalidLine", "entityDef", "entityName", 
                   "entityAlias", "columnDef", "columnMarkers", "columnName", 
                   "columnType", "columnStereotype", "stereotypeContent", 
                   "relationship", "cardinality", "relationSymbol", "relationshipLabel", 
                   "relationshipLabelText" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    STARTUML=8
    ENDUM=9
    ENTITY=10
    CLASS=11
    AS=12
    PK_MARKER=13
    VISIBILITY_MARKER=14
    CARDINALITY=15
    ONE_TO_ONE=16
    ONE_TO_MANY=17
    MANY_TO_MANY=18
    MANY_TO_ONE=19
    SIMPLE_RELATION=20
    IDENTIFIER=21
    STRING=22
    WS=23
    NEWLINE=24
    COMMENT=25
    ENDUML=26

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class DiagramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STARTUML(self):
            return self.getToken(PlantUMLERParser.STARTUML, 0)

        def ENDUM(self):
            return self.getToken(PlantUMLERParser.ENDUM, 0)

        def EOF(self):
            return self.getToken(PlantUMLERParser.EOF, 0)

        def entityDef(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PlantUMLERParser.EntityDefContext)
            else:
                return self.getTypedRuleContext(PlantUMLERParser.EntityDefContext,i)


        def relationship(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PlantUMLERParser.RelationshipContext)
            else:
                return self.getTypedRuleContext(PlantUMLERParser.RelationshipContext,i)


        def invalidLine(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PlantUMLERParser.InvalidLineContext)
            else:
                return self.getTypedRuleContext(PlantUMLERParser.InvalidLineContext,i)


        def getRuleIndex(self):
            return PlantUMLERParser.RULE_diagram

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDiagram" ):
                listener.enterDiagram(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDiagram" ):
                listener.exitDiagram(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDiagram" ):
                return visitor.visitDiagram(self)
            else:
                return visitor.visitChildren(self)




    def diagram(self):

        localctx = PlantUMLERParser.DiagramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_diagram)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 32
            self.match(PlantUMLERParser.STARTUML)
            self.state = 38
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,1,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 36
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
                    if la_ == 1:
                        self.state = 33
                        self.entityDef()
                        pass

                    elif la_ == 2:
                        self.state = 34
                        self.relationship()
                        pass

                    elif la_ == 3:
                        self.state = 35
                        self.invalidLine()
                        pass

             
                self.state = 40
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

            self.state = 41
            self.match(PlantUMLERParser.ENDUM)
            self.state = 42
            self.match(PlantUMLERParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class InvalidLineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(PlantUMLERParser.IDENTIFIER, 0)

        def ONE_TO_ONE(self):
            return self.getToken(PlantUMLERParser.ONE_TO_ONE, 0)

        def ONE_TO_MANY(self):
            return self.getToken(PlantUMLERParser.ONE_TO_MANY, 0)

        def MANY_TO_MANY(self):
            return self.getToken(PlantUMLERParser.MANY_TO_MANY, 0)

        def MANY_TO_ONE(self):
            return self.getToken(PlantUMLERParser.MANY_TO_ONE, 0)

        def WS(self):
            return self.getToken(PlantUMLERParser.WS, 0)

        def NEWLINE(self):
            return self.getToken(PlantUMLERParser.NEWLINE, 0)

        def COMMENT(self):
            return self.getToken(PlantUMLERParser.COMMENT, 0)

        def STARTUML(self):
            return self.getToken(PlantUMLERParser.STARTUML, 0)

        def ENDUML(self):
            return self.getToken(PlantUMLERParser.ENDUML, 0)

        def ENTITY(self):
            return self.getToken(PlantUMLERParser.ENTITY, 0)

        def CLASS(self):
            return self.getToken(PlantUMLERParser.CLASS, 0)

        def AS(self):
            return self.getToken(PlantUMLERParser.AS, 0)

        def STRING(self):
            return self.getToken(PlantUMLERParser.STRING, 0)

        def CARDINALITY(self):
            return self.getToken(PlantUMLERParser.CARDINALITY, 0)

        def getRuleIndex(self):
            return PlantUMLERParser.RULE_invalidLine

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInvalidLine" ):
                listener.enterInvalidLine(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInvalidLine" ):
                listener.exitInvalidLine(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitInvalidLine" ):
                return visitor.visitInvalidLine(self)
            else:
                return visitor.visitChildren(self)




    def invalidLine(self):

        localctx = PlantUMLERParser.InvalidLineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_invalidLine)
        self._la = 0 # Token type
        try:
            self.state = 46
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [21]:
                self.enterOuterAlt(localctx, 1)
                self.state = 44
                self.match(PlantUMLERParser.IDENTIFIER)
                pass
            elif token in [4, 5, 6, 7, 9, 13, 14, 20]:
                self.enterOuterAlt(localctx, 2)
                self.state = 45
                _la = self._input.LA(1)
                if _la <= 0 or (((_la) & ~0x3f) == 0 and ((1 << _la) & 133143822) != 0):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EntityDefContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def entityName(self):
            return self.getTypedRuleContext(PlantUMLERParser.EntityNameContext,0)


        def ENTITY(self):
            return self.getToken(PlantUMLERParser.ENTITY, 0)

        def CLASS(self):
            return self.getToken(PlantUMLERParser.CLASS, 0)

        def entityAlias(self):
            return self.getTypedRuleContext(PlantUMLERParser.EntityAliasContext,0)


        def columnDef(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PlantUMLERParser.ColumnDefContext)
            else:
                return self.getTypedRuleContext(PlantUMLERParser.ColumnDefContext,i)


        def getRuleIndex(self):
            return PlantUMLERParser.RULE_entityDef

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEntityDef" ):
                listener.enterEntityDef(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEntityDef" ):
                listener.exitEntityDef(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEntityDef" ):
                return visitor.visitEntityDef(self)
            else:
                return visitor.visitChildren(self)




    def entityDef(self):

        localctx = PlantUMLERParser.EntityDefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_entityDef)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 48
            _la = self._input.LA(1)
            if not(_la==10 or _la==11):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 49
            self.entityName()
            self.state = 51
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==12:
                self.state = 50
                self.entityAlias()


            self.state = 53
            self.match(PlantUMLERParser.T__0)
            self.state = 57
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 2121728) != 0):
                self.state = 54
                self.columnDef()
                self.state = 59
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 60
            self.match(PlantUMLERParser.T__1)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EntityNameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(PlantUMLERParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return PlantUMLERParser.RULE_entityName

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEntityName" ):
                listener.enterEntityName(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEntityName" ):
                listener.exitEntityName(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEntityName" ):
                return visitor.visitEntityName(self)
            else:
                return visitor.visitChildren(self)




    def entityName(self):

        localctx = PlantUMLERParser.EntityNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_entityName)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 62
            self.match(PlantUMLERParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EntityAliasContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def AS(self):
            return self.getToken(PlantUMLERParser.AS, 0)

        def STRING(self):
            return self.getToken(PlantUMLERParser.STRING, 0)

        def getRuleIndex(self):
            return PlantUMLERParser.RULE_entityAlias

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEntityAlias" ):
                listener.enterEntityAlias(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEntityAlias" ):
                listener.exitEntityAlias(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEntityAlias" ):
                return visitor.visitEntityAlias(self)
            else:
                return visitor.visitChildren(self)




    def entityAlias(self):

        localctx = PlantUMLERParser.EntityAliasContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_entityAlias)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 64
            self.match(PlantUMLERParser.AS)
            self.state = 65
            self.match(PlantUMLERParser.STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ColumnDefContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def columnName(self):
            return self.getTypedRuleContext(PlantUMLERParser.ColumnNameContext,0)


        def columnType(self):
            return self.getTypedRuleContext(PlantUMLERParser.ColumnTypeContext,0)


        def columnMarkers(self):
            return self.getTypedRuleContext(PlantUMLERParser.ColumnMarkersContext,0)


        def columnStereotype(self):
            return self.getTypedRuleContext(PlantUMLERParser.ColumnStereotypeContext,0)


        def getRuleIndex(self):
            return PlantUMLERParser.RULE_columnDef

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterColumnDef" ):
                listener.enterColumnDef(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitColumnDef" ):
                listener.exitColumnDef(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitColumnDef" ):
                return visitor.visitColumnDef(self)
            else:
                return visitor.visitChildren(self)




    def columnDef(self):

        localctx = PlantUMLERParser.ColumnDefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_columnDef)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 68
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==13 or _la==14:
                self.state = 67
                self.columnMarkers()


            self.state = 70
            self.columnName()
            self.state = 71
            self.match(PlantUMLERParser.T__2)
            self.state = 72
            self.columnType()
            self.state = 74
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==4:
                self.state = 73
                self.columnStereotype()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ColumnMarkersContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PK_MARKER(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLERParser.PK_MARKER)
            else:
                return self.getToken(PlantUMLERParser.PK_MARKER, i)

        def VISIBILITY_MARKER(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLERParser.VISIBILITY_MARKER)
            else:
                return self.getToken(PlantUMLERParser.VISIBILITY_MARKER, i)

        def getRuleIndex(self):
            return PlantUMLERParser.RULE_columnMarkers

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterColumnMarkers" ):
                listener.enterColumnMarkers(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitColumnMarkers" ):
                listener.exitColumnMarkers(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitColumnMarkers" ):
                return visitor.visitColumnMarkers(self)
            else:
                return visitor.visitChildren(self)




    def columnMarkers(self):

        localctx = PlantUMLERParser.ColumnMarkersContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_columnMarkers)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 77 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 76
                _la = self._input.LA(1)
                if not(_la==13 or _la==14):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 79 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==13 or _la==14):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ColumnNameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(PlantUMLERParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return PlantUMLERParser.RULE_columnName

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterColumnName" ):
                listener.enterColumnName(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitColumnName" ):
                listener.exitColumnName(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitColumnName" ):
                return visitor.visitColumnName(self)
            else:
                return visitor.visitChildren(self)




    def columnName(self):

        localctx = PlantUMLERParser.ColumnNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_columnName)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 81
            self.match(PlantUMLERParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ColumnTypeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(PlantUMLERParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return PlantUMLERParser.RULE_columnType

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterColumnType" ):
                listener.enterColumnType(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitColumnType" ):
                listener.exitColumnType(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitColumnType" ):
                return visitor.visitColumnType(self)
            else:
                return visitor.visitChildren(self)




    def columnType(self):

        localctx = PlantUMLERParser.ColumnTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_columnType)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 83
            self.match(PlantUMLERParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ColumnStereotypeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def stereotypeContent(self):
            return self.getTypedRuleContext(PlantUMLERParser.StereotypeContentContext,0)


        def getRuleIndex(self):
            return PlantUMLERParser.RULE_columnStereotype

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterColumnStereotype" ):
                listener.enterColumnStereotype(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitColumnStereotype" ):
                listener.exitColumnStereotype(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitColumnStereotype" ):
                return visitor.visitColumnStereotype(self)
            else:
                return visitor.visitChildren(self)




    def columnStereotype(self):

        localctx = PlantUMLERParser.ColumnStereotypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_columnStereotype)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 85
            self.match(PlantUMLERParser.T__3)
            self.state = 86
            self.stereotypeContent()
            self.state = 87
            self.match(PlantUMLERParser.T__4)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StereotypeContentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLERParser.IDENTIFIER)
            else:
                return self.getToken(PlantUMLERParser.IDENTIFIER, i)

        def getRuleIndex(self):
            return PlantUMLERParser.RULE_stereotypeContent

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStereotypeContent" ):
                listener.enterStereotypeContent(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStereotypeContent" ):
                listener.exitStereotypeContent(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStereotypeContent" ):
                return visitor.visitStereotypeContent(self)
            else:
                return visitor.visitChildren(self)




    def stereotypeContent(self):

        localctx = PlantUMLERParser.StereotypeContentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_stereotypeContent)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 89
            self.match(PlantUMLERParser.IDENTIFIER)
            self.state = 99
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 90
                self.match(PlantUMLERParser.T__2)
                self.state = 91
                self.match(PlantUMLERParser.IDENTIFIER)
                self.state = 96
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==6:
                    self.state = 92
                    self.match(PlantUMLERParser.T__5)
                    self.state = 93
                    self.match(PlantUMLERParser.IDENTIFIER)
                    self.state = 98
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)



        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RelationshipContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def entityName(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PlantUMLERParser.EntityNameContext)
            else:
                return self.getTypedRuleContext(PlantUMLERParser.EntityNameContext,i)


        def relationSymbol(self):
            return self.getTypedRuleContext(PlantUMLERParser.RelationSymbolContext,0)


        def cardinality(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(PlantUMLERParser.CardinalityContext)
            else:
                return self.getTypedRuleContext(PlantUMLERParser.CardinalityContext,i)


        def relationshipLabel(self):
            return self.getTypedRuleContext(PlantUMLERParser.RelationshipLabelContext,0)


        def getRuleIndex(self):
            return PlantUMLERParser.RULE_relationship

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRelationship" ):
                listener.enterRelationship(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRelationship" ):
                listener.exitRelationship(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRelationship" ):
                return visitor.visitRelationship(self)
            else:
                return visitor.visitChildren(self)




    def relationship(self):

        localctx = PlantUMLERParser.RelationshipContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_relationship)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 101
            self.entityName()
            self.state = 103
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==15 or _la==22:
                self.state = 102
                self.cardinality()


            self.state = 105
            self.relationSymbol()
            self.state = 107
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==15 or _la==22:
                self.state = 106
                self.cardinality()


            self.state = 109
            self.entityName()
            self.state = 111
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 110
                self.relationshipLabel()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CardinalityContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CARDINALITY(self):
            return self.getToken(PlantUMLERParser.CARDINALITY, 0)

        def STRING(self):
            return self.getToken(PlantUMLERParser.STRING, 0)

        def getRuleIndex(self):
            return PlantUMLERParser.RULE_cardinality

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCardinality" ):
                listener.enterCardinality(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCardinality" ):
                listener.exitCardinality(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCardinality" ):
                return visitor.visitCardinality(self)
            else:
                return visitor.visitChildren(self)




    def cardinality(self):

        localctx = PlantUMLERParser.CardinalityContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_cardinality)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 113
            _la = self._input.LA(1)
            if not(_la==15 or _la==22):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RelationSymbolContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ONE_TO_ONE(self):
            return self.getToken(PlantUMLERParser.ONE_TO_ONE, 0)

        def ONE_TO_MANY(self):
            return self.getToken(PlantUMLERParser.ONE_TO_MANY, 0)

        def MANY_TO_MANY(self):
            return self.getToken(PlantUMLERParser.MANY_TO_MANY, 0)

        def MANY_TO_ONE(self):
            return self.getToken(PlantUMLERParser.MANY_TO_ONE, 0)

        def SIMPLE_RELATION(self):
            return self.getToken(PlantUMLERParser.SIMPLE_RELATION, 0)

        def getRuleIndex(self):
            return PlantUMLERParser.RULE_relationSymbol

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRelationSymbol" ):
                listener.enterRelationSymbol(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRelationSymbol" ):
                listener.exitRelationSymbol(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRelationSymbol" ):
                return visitor.visitRelationSymbol(self)
            else:
                return visitor.visitChildren(self)




    def relationSymbol(self):

        localctx = PlantUMLERParser.RelationSymbolContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_relationSymbol)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 115
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 2031616) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RelationshipLabelContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(PlantUMLERParser.STRING, 0)

        def relationshipLabelText(self):
            return self.getTypedRuleContext(PlantUMLERParser.RelationshipLabelTextContext,0)


        def getRuleIndex(self):
            return PlantUMLERParser.RULE_relationshipLabel

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRelationshipLabel" ):
                listener.enterRelationshipLabel(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRelationshipLabel" ):
                listener.exitRelationshipLabel(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRelationshipLabel" ):
                return visitor.visitRelationshipLabel(self)
            else:
                return visitor.visitChildren(self)




    def relationshipLabel(self):

        localctx = PlantUMLERParser.RelationshipLabelContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_relationshipLabel)
        try:
            self.state = 121
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,13,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 117
                self.match(PlantUMLERParser.T__2)
                self.state = 118
                self.match(PlantUMLERParser.STRING)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 119
                self.match(PlantUMLERParser.T__2)
                self.state = 120
                self.relationshipLabelText()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RelationshipLabelTextContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self, i:int=None):
            if i is None:
                return self.getTokens(PlantUMLERParser.IDENTIFIER)
            else:
                return self.getToken(PlantUMLERParser.IDENTIFIER, i)

        def getRuleIndex(self):
            return PlantUMLERParser.RULE_relationshipLabelText

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRelationshipLabelText" ):
                listener.enterRelationshipLabelText(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRelationshipLabelText" ):
                listener.exitRelationshipLabelText(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRelationshipLabelText" ):
                return visitor.visitRelationshipLabelText(self)
            else:
                return visitor.visitChildren(self)




    def relationshipLabelText(self):

        localctx = PlantUMLERParser.RelationshipLabelTextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_relationshipLabelText)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 123
            self.match(PlantUMLERParser.IDENTIFIER)
            self.state = 128
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,14,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 124
                    self.match(PlantUMLERParser.T__6)
                    self.state = 125
                    self.match(PlantUMLERParser.IDENTIFIER) 
                self.state = 130
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,14,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





