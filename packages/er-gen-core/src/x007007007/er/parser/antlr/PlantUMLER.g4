grammar PlantUMLER;

// PlantUML ER Diagram Grammar
// Based on PlantUML entity-relationship diagram syntax

diagram: STARTUML (entityDef | relationship | invalidLine)* ENDUM EOF;

invalidLine: IDENTIFIER | ~(IDENTIFIER | '{' | '}' | ':' | ONE_TO_ONE | ONE_TO_MANY | MANY_TO_MANY | MANY_TO_ONE | WS | NEWLINE | COMMENT | STARTUML | ENDUML | ENTITY | CLASS | AS | STRING | CARDINALITY);

STARTUML: '@startuml';
ENDUM: '@enduml';

ENTITY: 'entity';
CLASS: 'class';
AS: 'as';

entityDef: (ENTITY | CLASS) entityName entityAlias? '{' columnDef* '}';

entityName: IDENTIFIER;

entityAlias: AS STRING;

columnDef: columnMarkers? columnName ':' columnType columnStereotype?;

columnMarkers: (PK_MARKER | VISIBILITY_MARKER)+;

PK_MARKER: '*';
VISIBILITY_MARKER: '+';

columnName: IDENTIFIER;

columnType: IDENTIFIER;

columnStereotype: '<<' stereotypeContent '>>';

stereotypeContent: IDENTIFIER (':' IDENTIFIER (',' IDENTIFIER)*)?;

relationship: entityName cardinality? relationSymbol cardinality? entityName relationshipLabel?;

cardinality: CARDINALITY | STRING;

CARDINALITY: '"' [^"]* '"';

relationSymbol: ONE_TO_ONE | ONE_TO_MANY | MANY_TO_MANY | MANY_TO_ONE | SIMPLE_RELATION;

// Define relation symbols as single string literals
ONE_TO_ONE: '||--||';
ONE_TO_MANY: '||--o{' | '||--}o';
MANY_TO_MANY: '}|--|{' | '}o--o{';
MANY_TO_ONE: '}o--||';
SIMPLE_RELATION: '--';

relationshipLabel: ':' STRING | ':' relationshipLabelText;

relationshipLabelText: IDENTIFIER ('-' IDENTIFIER)*;

// IDENTIFIER must come after relation symbols
IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;
STRING: '"' (~["\r\n] | '\\"')* '"';

WS: [ \t]+ -> skip;
NEWLINE: [\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;

