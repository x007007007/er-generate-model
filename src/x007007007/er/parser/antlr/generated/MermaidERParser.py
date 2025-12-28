# Generated from C:/Users/xxc/workspace/github.com/find-partner/ER/tools/../src/x007007007/er/parser/antlr/MermaidER.g4 by ANTLR 4.13.2
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
        4,1,16,97,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,1,0,1,0,
        1,0,1,0,5,0,31,8,0,10,0,12,0,34,9,0,1,0,1,0,1,1,1,1,3,1,40,8,1,1,
        2,1,2,1,2,5,2,45,8,2,10,2,12,2,48,9,2,1,2,1,2,1,3,1,3,1,4,1,4,1,
        4,3,4,57,8,4,1,4,3,4,60,8,4,1,5,1,5,1,6,1,6,1,7,1,7,1,7,1,7,1,7,
        1,7,3,7,72,8,7,1,8,1,8,1,9,1,9,1,9,1,9,1,9,3,9,81,8,9,1,10,1,10,
        1,11,1,11,3,11,87,8,11,1,12,1,12,1,12,5,12,92,8,12,10,12,12,12,95,
        9,12,1,12,0,0,13,0,2,4,6,8,10,12,14,16,18,20,22,24,0,2,3,0,1,3,8,
        12,14,16,1,0,8,11,96,0,26,1,0,0,0,2,39,1,0,0,0,4,41,1,0,0,0,6,51,
        1,0,0,0,8,53,1,0,0,0,10,61,1,0,0,0,12,63,1,0,0,0,14,71,1,0,0,0,16,
        73,1,0,0,0,18,75,1,0,0,0,20,82,1,0,0,0,22,86,1,0,0,0,24,88,1,0,0,
        0,26,32,5,5,0,0,27,31,3,4,2,0,28,31,3,18,9,0,29,31,3,2,1,0,30,27,
        1,0,0,0,30,28,1,0,0,0,30,29,1,0,0,0,31,34,1,0,0,0,32,30,1,0,0,0,
        32,33,1,0,0,0,33,35,1,0,0,0,34,32,1,0,0,0,35,36,5,0,0,1,36,1,1,0,
        0,0,37,40,5,12,0,0,38,40,8,0,0,0,39,37,1,0,0,0,39,38,1,0,0,0,40,
        3,1,0,0,0,41,42,3,6,3,0,42,46,5,1,0,0,43,45,3,8,4,0,44,43,1,0,0,
        0,45,48,1,0,0,0,46,44,1,0,0,0,46,47,1,0,0,0,47,49,1,0,0,0,48,46,
        1,0,0,0,49,50,5,2,0,0,50,5,1,0,0,0,51,52,5,12,0,0,52,7,1,0,0,0,53,
        54,3,10,5,0,54,56,3,12,6,0,55,57,3,14,7,0,56,55,1,0,0,0,56,57,1,
        0,0,0,57,59,1,0,0,0,58,60,3,16,8,0,59,58,1,0,0,0,59,60,1,0,0,0,60,
        9,1,0,0,0,61,62,5,12,0,0,62,11,1,0,0,0,63,64,5,12,0,0,64,13,1,0,
        0,0,65,72,5,6,0,0,66,72,5,7,0,0,67,68,5,6,0,0,68,72,5,7,0,0,69,70,
        5,7,0,0,70,72,5,6,0,0,71,65,1,0,0,0,71,66,1,0,0,0,71,67,1,0,0,0,
        71,69,1,0,0,0,72,15,1,0,0,0,73,74,5,13,0,0,74,17,1,0,0,0,75,76,3,
        6,3,0,76,77,3,20,10,0,77,78,3,6,3,0,78,80,5,3,0,0,79,81,3,22,11,
        0,80,79,1,0,0,0,80,81,1,0,0,0,81,19,1,0,0,0,82,83,7,1,0,0,83,21,
        1,0,0,0,84,87,5,13,0,0,85,87,3,24,12,0,86,84,1,0,0,0,86,85,1,0,0,
        0,87,23,1,0,0,0,88,93,5,12,0,0,89,90,5,4,0,0,90,92,5,12,0,0,91,89,
        1,0,0,0,92,95,1,0,0,0,93,91,1,0,0,0,93,94,1,0,0,0,94,25,1,0,0,0,
        95,93,1,0,0,0,10,30,32,39,46,56,59,71,80,86,93
    ]

class MermaidERParser ( Parser ):

    grammarFileName = "MermaidER.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'{'", "'}'", "':'", "'-'", "'erDiagram'", 
                     "'PK'", "'FK'", "'||--||'", "<INVALID>", "<INVALID>", 
                     "'}o--||'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "ER_DIAGRAM", "PK", "FK", "ONE_TO_ONE", 
                      "ONE_TO_MANY", "MANY_TO_MANY", "MANY_TO_ONE", "IDENTIFIER", 
                      "STRING", "WS", "NEWLINE", "COMMENT" ]

    RULE_diagram = 0
    RULE_invalidLine = 1
    RULE_entityDef = 2
    RULE_entityName = 3
    RULE_columnDef = 4
    RULE_columnType = 5
    RULE_columnName = 6
    RULE_columnModifiers = 7
    RULE_columnComment = 8
    RULE_relationship = 9
    RULE_relationSymbol = 10
    RULE_relationshipLabel = 11
    RULE_relationshipLabelText = 12

    ruleNames =  [ "diagram", "invalidLine", "entityDef", "entityName", 
                   "columnDef", "columnType", "columnName", "columnModifiers", 
                   "columnComment", "relationship", "relationSymbol", "relationshipLabel", 
                   "relationshipLabelText" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    ER_DIAGRAM=5
    PK=6
    FK=7
    ONE_TO_ONE=8
    ONE_TO_MANY=9
    MANY_TO_MANY=10
    MANY_TO_ONE=11
    IDENTIFIER=12
    STRING=13
    WS=14
    NEWLINE=15
    COMMENT=16

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

        def ER_DIAGRAM(self):
            return self.getToken(MermaidERParser.ER_DIAGRAM, 0)

        def EOF(self):
            return self.getToken(MermaidERParser.EOF, 0)

        def entityDef(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidERParser.EntityDefContext)
            else:
                return self.getTypedRuleContext(MermaidERParser.EntityDefContext,i)


        def relationship(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidERParser.RelationshipContext)
            else:
                return self.getTypedRuleContext(MermaidERParser.RelationshipContext,i)


        def invalidLine(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidERParser.InvalidLineContext)
            else:
                return self.getTypedRuleContext(MermaidERParser.InvalidLineContext,i)


        def getRuleIndex(self):
            return MermaidERParser.RULE_diagram

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

        localctx = MermaidERParser.DiagramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_diagram)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 26
            self.match(MermaidERParser.ER_DIAGRAM)
            self.state = 32
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 12528) != 0):
                self.state = 30
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
                if la_ == 1:
                    self.state = 27
                    self.entityDef()
                    pass

                elif la_ == 2:
                    self.state = 28
                    self.relationship()
                    pass

                elif la_ == 3:
                    self.state = 29
                    self.invalidLine()
                    pass


                self.state = 34
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 35
            self.match(MermaidERParser.EOF)
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
            return self.getToken(MermaidERParser.IDENTIFIER, 0)

        def ONE_TO_ONE(self):
            return self.getToken(MermaidERParser.ONE_TO_ONE, 0)

        def ONE_TO_MANY(self):
            return self.getToken(MermaidERParser.ONE_TO_MANY, 0)

        def MANY_TO_MANY(self):
            return self.getToken(MermaidERParser.MANY_TO_MANY, 0)

        def MANY_TO_ONE(self):
            return self.getToken(MermaidERParser.MANY_TO_ONE, 0)

        def WS(self):
            return self.getToken(MermaidERParser.WS, 0)

        def NEWLINE(self):
            return self.getToken(MermaidERParser.NEWLINE, 0)

        def COMMENT(self):
            return self.getToken(MermaidERParser.COMMENT, 0)

        def getRuleIndex(self):
            return MermaidERParser.RULE_invalidLine

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

        localctx = MermaidERParser.InvalidLineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_invalidLine)
        self._la = 0 # Token type
        try:
            self.state = 39
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [12]:
                self.enterOuterAlt(localctx, 1)
                self.state = 37
                self.match(MermaidERParser.IDENTIFIER)
                pass
            elif token in [4, 5, 6, 7, 13]:
                self.enterOuterAlt(localctx, 2)
                self.state = 38
                _la = self._input.LA(1)
                if _la <= 0 or (((_la) & ~0x3f) == 0 and ((1 << _la) & 122638) != 0):
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
            return self.getTypedRuleContext(MermaidERParser.EntityNameContext,0)


        def columnDef(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MermaidERParser.ColumnDefContext)
            else:
                return self.getTypedRuleContext(MermaidERParser.ColumnDefContext,i)


        def getRuleIndex(self):
            return MermaidERParser.RULE_entityDef

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

        localctx = MermaidERParser.EntityDefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_entityDef)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 41
            self.entityName()
            self.state = 42
            self.match(MermaidERParser.T__0)
            self.state = 46
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==12:
                self.state = 43
                self.columnDef()
                self.state = 48
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 49
            self.match(MermaidERParser.T__1)
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
            return self.getToken(MermaidERParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return MermaidERParser.RULE_entityName

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

        localctx = MermaidERParser.EntityNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_entityName)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 51
            self.match(MermaidERParser.IDENTIFIER)
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

        def columnType(self):
            return self.getTypedRuleContext(MermaidERParser.ColumnTypeContext,0)


        def columnName(self):
            return self.getTypedRuleContext(MermaidERParser.ColumnNameContext,0)


        def columnModifiers(self):
            return self.getTypedRuleContext(MermaidERParser.ColumnModifiersContext,0)


        def columnComment(self):
            return self.getTypedRuleContext(MermaidERParser.ColumnCommentContext,0)


        def getRuleIndex(self):
            return MermaidERParser.RULE_columnDef

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

        localctx = MermaidERParser.ColumnDefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_columnDef)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 53
            self.columnType()
            self.state = 54
            self.columnName()
            self.state = 56
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==6 or _la==7:
                self.state = 55
                self.columnModifiers()


            self.state = 59
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==13:
                self.state = 58
                self.columnComment()


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
            return self.getToken(MermaidERParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return MermaidERParser.RULE_columnType

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

        localctx = MermaidERParser.ColumnTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_columnType)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 61
            self.match(MermaidERParser.IDENTIFIER)
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
            return self.getToken(MermaidERParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return MermaidERParser.RULE_columnName

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

        localctx = MermaidERParser.ColumnNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_columnName)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 63
            self.match(MermaidERParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ColumnModifiersContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PK(self):
            return self.getToken(MermaidERParser.PK, 0)

        def FK(self):
            return self.getToken(MermaidERParser.FK, 0)

        def getRuleIndex(self):
            return MermaidERParser.RULE_columnModifiers

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterColumnModifiers" ):
                listener.enterColumnModifiers(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitColumnModifiers" ):
                listener.exitColumnModifiers(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitColumnModifiers" ):
                return visitor.visitColumnModifiers(self)
            else:
                return visitor.visitChildren(self)




    def columnModifiers(self):

        localctx = MermaidERParser.ColumnModifiersContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_columnModifiers)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 71
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,6,self._ctx)
            if la_ == 1:
                self.state = 65
                self.match(MermaidERParser.PK)
                pass

            elif la_ == 2:
                self.state = 66
                self.match(MermaidERParser.FK)
                pass

            elif la_ == 3:
                self.state = 67
                self.match(MermaidERParser.PK)
                self.state = 68
                self.match(MermaidERParser.FK)
                pass

            elif la_ == 4:
                self.state = 69
                self.match(MermaidERParser.FK)
                self.state = 70
                self.match(MermaidERParser.PK)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ColumnCommentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(MermaidERParser.STRING, 0)

        def getRuleIndex(self):
            return MermaidERParser.RULE_columnComment

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterColumnComment" ):
                listener.enterColumnComment(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitColumnComment" ):
                listener.exitColumnComment(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitColumnComment" ):
                return visitor.visitColumnComment(self)
            else:
                return visitor.visitChildren(self)




    def columnComment(self):

        localctx = MermaidERParser.ColumnCommentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_columnComment)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 73
            self.match(MermaidERParser.STRING)
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
                return self.getTypedRuleContexts(MermaidERParser.EntityNameContext)
            else:
                return self.getTypedRuleContext(MermaidERParser.EntityNameContext,i)


        def relationSymbol(self):
            return self.getTypedRuleContext(MermaidERParser.RelationSymbolContext,0)


        def relationshipLabel(self):
            return self.getTypedRuleContext(MermaidERParser.RelationshipLabelContext,0)


        def getRuleIndex(self):
            return MermaidERParser.RULE_relationship

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

        localctx = MermaidERParser.RelationshipContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_relationship)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 75
            self.entityName()
            self.state = 76
            self.relationSymbol()
            self.state = 77
            self.entityName()
            self.state = 78
            self.match(MermaidERParser.T__2)
            self.state = 80
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,7,self._ctx)
            if la_ == 1:
                self.state = 79
                self.relationshipLabel()


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
            return self.getToken(MermaidERParser.ONE_TO_ONE, 0)

        def ONE_TO_MANY(self):
            return self.getToken(MermaidERParser.ONE_TO_MANY, 0)

        def MANY_TO_MANY(self):
            return self.getToken(MermaidERParser.MANY_TO_MANY, 0)

        def MANY_TO_ONE(self):
            return self.getToken(MermaidERParser.MANY_TO_ONE, 0)

        def getRuleIndex(self):
            return MermaidERParser.RULE_relationSymbol

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

        localctx = MermaidERParser.RelationSymbolContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_relationSymbol)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 82
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 3840) != 0)):
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
            return self.getToken(MermaidERParser.STRING, 0)

        def relationshipLabelText(self):
            return self.getTypedRuleContext(MermaidERParser.RelationshipLabelTextContext,0)


        def getRuleIndex(self):
            return MermaidERParser.RULE_relationshipLabel

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

        localctx = MermaidERParser.RelationshipLabelContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_relationshipLabel)
        try:
            self.state = 86
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [13]:
                self.enterOuterAlt(localctx, 1)
                self.state = 84
                self.match(MermaidERParser.STRING)
                pass
            elif token in [12]:
                self.enterOuterAlt(localctx, 2)
                self.state = 85
                self.relationshipLabelText()
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


    class RelationshipLabelTextContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self, i:int=None):
            if i is None:
                return self.getTokens(MermaidERParser.IDENTIFIER)
            else:
                return self.getToken(MermaidERParser.IDENTIFIER, i)

        def getRuleIndex(self):
            return MermaidERParser.RULE_relationshipLabelText

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

        localctx = MermaidERParser.RelationshipLabelTextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_relationshipLabelText)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 88
            self.match(MermaidERParser.IDENTIFIER)
            self.state = 93
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,9,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 89
                    self.match(MermaidERParser.T__3)
                    self.state = 90
                    self.match(MermaidERParser.IDENTIFIER) 
                self.state = 95
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,9,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





