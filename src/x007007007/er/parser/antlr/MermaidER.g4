grammar MermaidER;

// Mermaid ER Diagram Grammar
// Based on Mermaid ER diagram syntax

diagram: ER_DIAGRAM (entityDef | relationship | invalidLine)* EOF;

invalidLine: IDENTIFIER | ~(IDENTIFIER | '{' | '}' | ':' | ONE_TO_ONE | ONE_TO_MANY | MANY_TO_MANY | MANY_TO_ONE | WS | NEWLINE | COMMENT);

ER_DIAGRAM: 'erDiagram';

entityDef: entityName '{' columnDef* '}';

entityName: IDENTIFIER;

columnDef: columnType columnName columnModifiers? columnComment?;

columnType: IDENTIFIER;
columnName: IDENTIFIER;
columnModifiers: (PK | FK | UK | PK FK | FK PK | PK UK | UK PK | FK UK | UK FK);
columnComment: STRING;

PK: 'PK';
FK: 'FK';
UK: 'UK';

relationship: entityName relationSymbol entityName ':' relationshipLabel?;

relationSymbol: ONE_TO_ONE | ONE_TO_MANY | MANY_TO_MANY | MANY_TO_ONE;

// Define relation symbols as single string literals - these must match before IDENTIFIER
ONE_TO_ONE: '||--||';
ONE_TO_MANY: '||--o{' | '||--}o';
MANY_TO_MANY: '}|--|{' | '}o--o{';
MANY_TO_ONE: '}o--||';

relationshipLabel: STRING | relationshipLabelText;

relationshipLabelText: IDENTIFIER ('-' IDENTIFIER)*;

// IDENTIFIER must come after relation symbols
IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;
STRING: '"' (~["\r\n] | '\\"')* '"';

WS: [ \t]+ -> skip;
NEWLINE: [\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;
