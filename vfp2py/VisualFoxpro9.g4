grammar VisualFoxpro9
 ;

preprocessorCode
 : preprocessorLines EOF
 ;

preprocessorLines
 : preprocessorLine*
 ;

preprocessorLine
 : '#' (IF expr | IFDEF identifier) NL 
           ifBody=preprocessorLines
  ('#' ELSE NL
           elseBody=preprocessorLines)?
   '#' ENDIF lineEnd #preprocessorIf
 | '#' DEFINE identifier (~NL)* lineEnd #preprocessorDefine
 | '#' UNDEFINE identifier lineEnd #preprocessorUndefine
 | '#' INCLUDE specialExpr lineEnd #preprocessorInclude
 | '#' (~(IF | ELSE | ENDIF | DEFINE | INCLUDE | NL) (~NL)*) lineEnd #preprocessorJunk
 | (NL | ~('#' | NL | EOF) (~NL)* lineEnd) #nonpreprocessorLine
 ;

prg
 : (classDef | funcDef)* EOF
 ;

lineComment
 : ('*' | NOTE) (~NL)* lineEnd
 | NL
 ;

line
 : lineComment
 | (controlStmt | cmd) lineEnd
 ;

lineEnd
 : NL
 | EOF
 ;

lines
 : line*
 ;

classDefStart
 : DEFINE CLASS identifier (AS identifier)? NL
 ;

classDef
 : classDefStart (classDefProperty | funcDef)* ENDDEFINE lineEnd lineComment*
 ;

classDefProperty
 : ADD OBJECT identifier AS idAttr (WITH idAttr '=' expr (',' idAttr '=' expr)*)? NL #classDefAddObject
 | assign NL #classDefAssign
 | lineComment #classDefLineComment
 ;

funcDefStart
 : SCOPE? PROCEDURE idAttr2 ('(' parameters? ')')? NL parameterDef?
 ;

funcDefEnd
 : ENDPROC lineEnd lineComment*
 ;

parameterDef
 : PARAMETER parameters NL
 ;

funcDef
 :  funcDefStart lines funcDefEnd?
 ;

parameter
 : idAttr (AS idAttr)?
 ;

parameters
 : parameter (',' parameter)*
 ;

ifStart
 : IF expr THEN? NL
 ;

ifStmt
 : ifStart ifBody=lines (ELSE NL elseBody=lines)? ENDIF
 ;

forStart
 : FOR idAttr '=' loopStart=expr TO loopStop=expr (STEP loopStep=expr)? NL
 | FOR EACH idAttr IN expr NL
 ;

forEnd
 : (ENDFOR | NEXT idAttr?)
 ;

forStmt
 : forStart lines forEnd
 ;

singleCase
 : CASE expr NL lines
 ;

otherwise
 : OTHERWISE NL lines
 ;

caseStmt
 : DO CASE NL lineComment* singleCase* otherwise? ENDCASE
 ;

whileStart
 : DO? WHILE expr NL
 ;

whileStmt
 : whileStart lines ENDDO
 ;

withStmt
 : WITH idAttr NL lines ENDWITH
 ;

scanStmt
 : SCAN scopeClause? (FOR expr)? NL lines ENDSCAN
 ;

tryStmt
 : TRY NL tryLines=lines (CATCH (TO identifier)? NL catchLines=lines)? (FINALLY NL finallyLines=lines)? ENDTRY
 ;

controlStmt
 : whileStmt
 | ifStmt
 | caseStmt
 | forStmt
 | withStmt
 | scanStmt
 | tryStmt
 ;

cmd
 : funcDo
 | assign
 | declaration
 | printStmt
 | waitCmd
 | filesystemCmd
 | returnStmt
 | release
 | setup
 | otherCmds
 | '=' expr
 | complexId
 ;

release
 : RELEASE (ALL | vartype=(PROCEDURE|CLASSLIB)? args | POPUP args EXTENDED?)
 ;

otherCmds
 : ON KEY (LABEL identifier ('+' identifier)?)? cmd #onKey
 | (PROGRAMCONTROL) #programControl
 | '@' args (SAY sayExpr=expr | STYLE styleExpr=expr)* #atSay
 | PUSH KEY CLEAR? #pushKey
 | POP KEY ALL? #popKey
 | KEYBOARD expr PLAIN? CLEAR? #keyboard

 | DEFINE MENU identifier (BAR (AT LINE NUMBER_LITERAL)?) (IN (WINDOW? identifier | SCREEN))? NOMARGIN? #defineMenu
 | DEFINE PAD identifier OF expr PROMPT expr (AT NUMBER_LITERAL ',' NUMBER_LITERAL)?
         (BEFORE identifier | AFTER identifier)? (NEGOTIATE identifier (',' identifier)?)?
         (FONT identifier (',' NUMBER_LITERAL (',' expr (',' identifier)?)?)?)? (STYLE identifier)?
         (MESSAGE expr)? (KEY identifier ('+' identifier)? (',' expr)?)? (MARK identifier)?
         (SKIPKW (FOR expr)?)? (COLOR SCHEME NUMBER_LITERAL)? #definePad
 | DEFINE POPUP identifier SHADOW? MARGIN? RELATIVE? (COLOR SCHEME NUMBER_LITERAL)? #definePopup
 | DEFINE BAR NUMBER_LITERAL OF identifier PROMPT expr (MESSAGE expr)? #defineBar
 | ON PAD identifier OF identifier (ACTIVATE (POPUP | MENU) identifier)? #onPad
 | ON BAR NUMBER_LITERAL OF identifier (ACTIVATE (POPUP | MENU) identifier)? #onBar
 | ON SELECTION BAR NUMBER_LITERAL OF identifier cmd #onSelectionBar
 | ACTIVATE WINDOW (parameters | ALL) (IN (WINDOW? identifier | SCREEN))? (BOTTOM | TOP | SAME)? NOSHOW? #activateWindow
 | ACTIVATE MENU identifier NOWAIT? (PAD identifier)? #activateMenu
 | DEACTIVATE (MENU|POPUP) (ALL | parameters) #deactivate

 | ERROR expr? #raiseError
 | THROW expr? #throwError

 | CREATE (TABLE|DBF|CURSOR) specialExpr FREE? '(' identifier identifier arrayIndex (',' identifier identifier arrayIndex)* ')' #createTable
 | ALTER TABLE specialExpr (ADD COLUMN identifier identifier arrayIndex | DROP COLUMN identifier) #alterTable
 | SELECT (tablename=specialExpr | (DISTINCT? (specialArgs | '*') (FROM fromExpr=specialExpr)? (WHERE whereExpr=expr)? (INTO (TABLE | CURSOR) intoExpr=specialExpr)? (ORDER BY orderbyid=identifier)?)) #select
 | USE (SHARED | EXCLUSIVE)? (IN workArea=specialExpr | name=specialExpr IN workArea=specialExpr | name=specialExpr)? (SHARED | EXCLUSIVE)? (ALIAS aliasExpr=specialExpr)? #use
 | LOCATE queryCondition* #locate
 | CONTINUE #continueLocate
 | REPLACE (queryCondition | specialExpr WITH expr)* #replace
 | INDEX ON specialExpr (TAG | TO) specialExpr COMPACT? (ASCENDING | DESCENDING)? (UNIQUE | CANDIDATE)? ADDITIVE? #indexOn
 | COUNT (TO toExpr=expr | queryCondition)* #count
 | SUM (TO toExpr=expr | queryCondition | sumExpr=expr)* #sum
 | (RECALL | DELETE) (queryCondition | IN inExpr=specialExpr)* #deleteRecord
 | APPEND FROM (ARRAY expr | specialExpr FOR expr | specialExpr ) (TYPE typeExpr=specialExpr)? #appendFrom
 | APPEND BLANK? (IN specialExpr NOMENU | IN specialExpr)? #append
 | INSERT INTO specialExpr (FROM (ARRAY expr | MEMVAR | NAME expr) | ('(' specialArgs ')')? VALUES '(' args ')') #insert
 | SKIPKW expr? (IN specialExpr)? #skipRecord
 | PACK (DATABASE | (MEMO | DBF)? (IN workArea=specialExpr | tableName=specialExpr IN workArea=specialExpr | tableName=specialExpr)?) #pack
 | REINDEX COMPACT? #reindex
 | SEEK seekExpr=expr ((ORDER orderExpr=expr | TAG tagName=specialExpr (OF cdxFileExpr=specialExpr)? | idxFileExpr=specialExpr) (ASCENDING | DESCENDING)?)? (IN tablenameExpr=specialExpr)? #seekRecord
 | GOTO (TOP | BOTTOM | RECORD? expr) (IN specialExpr)? #goRecord
 | COPY STRUCTURE? TO specialExpr #copyTo
 | ZAP (IN specialExpr)? #zapTable
 | BROWSE (~NL)* #browse
 | SCATTER (FIELDS (LIKE | EXCEPT)? expr)? MEMO? BLANK? (MEMVAR | NAME expr ADDITIVE? | TO expr) #scatterExpr
 | GATHER (FIELDS (LIKE | EXCEPT)? expr)? MEMO? FROM (MEMVAR | NAME expr | expr) #gatherExpr

 | CLOSE ((DATABASE | INDEXES | TABLES) ALL? | ALL) #closeStmt
 | READ EVENTS #readEvent
 | CLEAR (ALL | CLASS expr | CLASSLIB specialExpr | DEBUG | DLLS specialArgs | EVENTS | ERROR | FIELDS | GETS | MACROS | MEMORY | MENUS | POPUP | PROGRAM | PROMPT | READ ALL? | RESOURCES expr | TYPEAHEAD | WINDOW)? #clearStmt
 | REPORT FORM ('?' | specialExpr) (NOEJECT | TO PRINTER PROMPT? | NOCONSOLE)* #report
 | DECLARE returnType=datatype? identifier IN specialExpr (AS alias=identifier)? dllArgs? #dllDeclare
 | NODEFAULT #nodefault
 | (RUN | EXCLAMATION) ('/' identifier)? (~NL)* #shellRun
 | ASSERT expr (MESSAGE expr)? #assert
 ;

queryCondition
 : scopeClause
 | FOR expr
 | WHILE expr
 | NOOPTIMIZE
 ;

dllArgs
 : dllArg (',' dllArg)*
 ;

dllArg
 : datatype '@'? identifier?
 ;

printStmt
 : ('?' '?'? | DEBUGOUT) args?
 ;

waitCmd
 : WAIT (TO toExpr=expr | WINDOW (AT atExpr1=expr ',' atExpr2=expr)? | NOWAIT | CLEAR | NOCLEAR | TIMEOUT timeout=expr | message=expr)*
 ;

filesystemCmd
 : (ERASE | DELETE FILE) (specialExpr|'?') RECYCLE? #deleteFile
 | (RENAME | COPY FILE) specialExpr TO specialExpr #copyMoveFile
 | (CHDIR | MKDIR | RMDIR) specialExpr #chMkRmDir
 ;

returnStmt
 : RETURN expr?
 ;

setup
 : onError
 | setStmt
 | onShutdown
 ;

onError
 : ON ERROR cmd?
 ;

onShutdown
 : ON SHUTDOWN cmd?
 ;

setStmt
 : SET setCmd
 ;

setCmd
 : setword=ALTERNATE (ON | OFF | TO specialExpr ADDITIVE?)
 | setword=ASSERTS (ON | OFF)
 | setword=BELL (ON | OFF | TO specialExpr)
 | setword=CENTURY (ON | OFF | TO (expr (ROLLOVER expr)?)?) 
 | setword=CLASSLIB TO specialExpr (IN specialExpr)? (ALIAS specialExpr)? ADDITIVE?
 | setword=CLOCK (ON | OFF | STATUS | TO (expr ',' expr)?)
 | setword=COMPATIBLE (ON | OFF | DB4 | FOXPLUS) (PROMPT | NOPROMPT)?
 | setword=CURSOR (ON | OFF)
 | setword=DATE TO? identifier
 | setword=DELETED (ON | OFF)
 | setword=EXACT (ON | OFF)
 | setword=EXCLUSIVE (ON | OFF)
 | setword=FILTER TO (specialExpr (IN specialExpr)?)?
 | setword=HELP (ON | OFF | TO specialExpr? | COLLECTION specialExpr? | SYSTEM)
 | setword=INDEX TO specialExpr?
 | setword=LIBRARY TO (specialExpr ADDITIVE?)
 | setword=MEMOWIDTH TO expr
 | setword=MULTILOCKS (ON | OFF)
 | setword=NEAR (ON | OFF)
 | setword=NOTIFY CURSOR? (ON | OFF)
 | setword=ORDER TO (specialExpr | TAG? specialExpr (OF ofExpr=specialExpr)? (IN inExpr=specialExpr)? (ASCENDING | DESCENDING)?)?
 | setword=PRINTER (ON PROMPT? | OFF | TO (DEFAULT | NAME specialExpr | specialExpr ADDITIVE?)?)
 | setword=PROCEDURE TO specialExpr (',' specialExpr)* ADDITIVE?
 | setword=REFRESH TO expr (',' expr)?
 | setword=RELATION TO expr INTO specialExpr (IN specialExpr)? ADDITIVE?
 | setword=SAFETY (ON | OFF)
 | setword=STATUS BAR? (ON | OFF)
 | setword=SYSMENU (ON | OFF | TO (DEFAULT | expr)? | SAVE | NOSAVE)
 | setword=TABLEPROMPT (ON | OFF)
 | setword=TALK (ON | OFF)
 | setword=TYPEAHEAD TO expr
 | setword=UNIQUE (ON | OFF)
 ;

declaration
 : ((SCOPE|EXTERNAL) (ARRAY | DIMENSION | DECLARE)? | DIMENSION | DECLARE) declarationItem (',' declarationItem)*
 | EXTERNAL PROCEDURE specialExpr
 ;

declarationItem
 : (idAttr2 arrayIndex | idAttr (AS datatype (OF specialExpr)?)?)
 ;

args
 : expr (',' expr)* ','?
 ;

specialArgs
 : specialExpr (',' specialExpr)*
 ;

funcDo
 : DO FORM specialExpr
 | DO specialExpr (IN specialExpr)? (WITH args)?
 ;

reference
 : '@' idAttr
 ;

argReplace
 : '&' identifier
 ;

expr
 : '(' expr ')' #subExpr
 | op=('+'|'-') expr #unaryNegation
 | ('!'|NOT) expr #booleanNegation
 | expr ('*' '*'|'^') expr #power
 | expr op=('*'|'/') expr #multiplication
 | expr '%' expr #modulo
 | expr op=('+'|'-') expr #addition
 | expr op=('=='|NOTEQUALS|'='|'#'|'>'|GTEQ|'<'|LTEQ|'$') expr #comparison
 | expr op=(OR|OTHEROR|AND|OTHERAND) expr #booleanOperation
 | constant #constantExpr
 | CAST '(' expr AS datatype ')' #castExpr
 | PERIOD? atom trailer? #atomExpr
 ;

complexId
 : PERIOD? atom trailer
 | PERIOD atom trailer?
 ;

atom
 : identifier
 | reference
 | argReplace
 ;

trailer
 : ('(' args? ')' | '[' args? ']') trailer? #funcCallTrailer
 | '.' identifier trailer? #identTrailer
 ;

pathname
 : (identifier ':')? pathElement+?
 ;

pathElement
 : identifier
 | NUMBER_LITERAL 
 | BACKSLASH 
 | ';' 
 | '&' 
 | '@' 
 | '+' 
 | '-' 
 | '.' 
 | '[' 
 | ']' 
 | '{' 
 | '}' 
 | '(' 
 | ')' 
 | '!' 
 | '#' 
 | '==' 
 | NOTEQUALS 
 | '%' 
 | '=' 
 | '^' 
 | ',' 
 | '$' 
 | '_'
 ;

specialExpr
 : expr
 | pathname
 ;

constant
 : '$'? NUMBER_LITERAL #numberOrCurrency
 | ('.' (BOOLEANCHAR | NULL) '.' | NULL) #boolOrNull
 | '{' ( '/' '/'  | ':' | '^' (NUMBER_LITERAL '-' NUMBER_LITERAL '-' NUMBER_LITERAL | NUMBER_LITERAL '/' NUMBER_LITERAL '/' NUMBER_LITERAL) (','? NUMBER_LITERAL (':' NUMBER_LITERAL (':' NUMBER_LITERAL)?)? identifier)? )? '}' #date
 | ('\'' (~(NL | '\''))* '\'' | '"' (~(NL | '"'))* '"' | '[' (~(NL | ']'))* ']') #string
 | BLOB_LITERAL #blob
 ;

assign
 : STORE expr TO idAttr (',' idAttr)*
 | idAttr '=' expr
 ;

idAttr2
 : (startPeriod='.')? identifier ('.' identifier)*
 ;

idAttr
 : PERIOD? identifier trailer?
 ;

twoExpr
 : expr ',' expr
 ;

arrayIndex
 : '(' (expr | twoExpr) ')'
 | '[' (expr | twoExpr) ']'
 ;

datatype
 : identifier
 ;

scopeClause
 : ALL | NEXT expr | RECORD expr | REST
 ;

identifier
 : TO|DO|IN|AS|IF|ELIF|ELSE|ENDIF|ON|OFF|ERROR|WITH|STORE|EXTERNAL|SCOPE|ARRAY|RECALL|DELETE|FILE|SET|RELEASE|RECYCLE|CREATE|TABLE|DATABASE|DBF|NAME|FREE|SELECT|USE|READ|EVENTS|SHUTDOWN|CLEAR|PROCEDURE|DEFINE|CLASS|ENDDEFINE|LOCATE|CONTINUE|FOR|ENDFOR|WHILE|NOOPTIMIZE|STATUS|BAR|MEMOWIDTH|CURSOR|REFRESH|BELL|CENTURY|DATE|ADD|OBJECT|REPLACE|LIBRARY|SHARED|WAIT|WINDOW|NOWAIT|NOCLEAR|NOTIFY|ENDDO|DECLARE|ERASE|SYSMENU|CLOCK|RETURN|PARAMETER|ALTERNATE|EXACT|ALL|COUNT|GOTO|TOP|BOTTOM|RECORD|CLOSE|APPEND|BLANK|NOMENU|CASE|FROM|REPORT|FORM|NOEJECT|PRINTER
 | PROMPT
 | NOPROMPT
 | NOCONSOLE|COPY|STRUCTURE|DELETED|SUM|DISTINCT|INTO|NEXT|REST|SKIPKW|PACK|EXCLUSIVE|NEAR|MKDIR|RMDIR|KEY|KEYBOARD|LABEL|PLAIN|MENU|AT|LINE|SCREEN|NOMARGIN|PAD|OF|COLOR|SCHEME|BEFORE|AFTER|NEGOTIATE|FONT|STYLE|MARK|MESSAGE|ACTIVATE|POPUP|SHADOW|MARGIN|RELATIVE|SELECTION|DEACTIVATE|SAME|NOSHOW|STEP|THEN|UNDEFINE|IFDEF|PUSH|POP|TIMEOUT|ENDWITH|TYPEAHEAD|ALIAS|ORDER|SEEK|WHERE|FILTER|RENAME|INCLUDE|CLASSLIB|BY|UNIQUE|INDEX|TAG|COMPACT|ASCENDING|DESCENDING|CANDIDATE|ADDITIVE|DIMENSION|NOT|AND|OR|SCAN|ENDSCAN|NULL|BOOLEANCHAR|NODEFAULT|DLLS|MACROS|NUMBER|ZAP|ROLLOVER|DEFAULT|SAVE|NOSAVE|PROGRAM|THROW|TABLES|EACH|CAST|ENDCASE|ENDPROC|REINDEX|INDEXES|OTHERWISE|RUN|EXTENDED
 | ASSERT
 | TRY
 | CATCH
 | FINALLY
 | ENDTRY
 | BROWSE
 | INSERT
 | VALUES
 | MEMVAR
 | COMPATIBLE
 | DB4
 | FOXPLUS
 | TYPE
 | SCATTER
 | GATHER
 | EXCEPT
 | LIKE
 | FIELDS
 | ALTER
 | COLUMN
 | DROP
 | ID
 | HELP
 | SAY
 | COLLECTION
 | SYSTEM
 | TALK
 | PROGRAMCONTROL
 | RELATION
 ;

NUMBER_LITERAL : (DIGIT* '.')? DIGIT+ (E [+-]? DIGIT*)?
               | DIGIT+ '.'
               | '0' X HEXDIGIT*
               ;

BLOB_LITERAL : '0' H HEXDIGIT* ;

SEMICOLON: ';';
AMPERSAND: '&';
COMMERCIALAT: '@';
ASTERISK: '*';
PLUS_SIGN: '+';
MINUS_SIGN: '-';
FORWARDSLASH: '/';
PERIOD: '.';
LEFTBRACKET: '[';
RIGHTBRACKET: ']';
LEFTBRACE: '{';
RIGHTBRACE: '}';
LEFTPAREN: '(';
RIGHTPAREN: ')';
BACKSLASH: '\\';
LESSTHAN: '<';
GREATERTHAN: '>';
EXCLAMATION: '!';
HASH: '#';
DOUBLEEQUALS: '==';
NOTEQUALS: ('!='|'<>');
GTEQ: ('>='|'=>');
LTEQ: ('<='|'=<');
MODULO: '%';
EQUALS: '=';
CARAT: '^';
COMMA: ',';
DOLLAR: '$';
COLON: ':';
QUESTION: '?';
DOUBLEQUOTE: '"';
SINGLEQUOTE: '\'';

COMMENT: ('&&' (~'\n')* | ';' WS* '&&' (~'\n')* NL) -> channel(1);

LINECONT : ';' WS* NL -> channel(2);

NOTE: N O T E;
ASSERT: A S S E R T;
ASSERTS: ASSERT S;
TO : T O;
DO : D O;
IN : I N;
AS : A S;
IF : I F;
ELIF : E L I F;
ELSE : E L S E;
ENDIF : E N D I F;
ON : O N;
OFF : O F F;
ERROR : E R R O R;
WITH : W I T H;
STORE : S T O R E;
EXTERNAL: E X T E R N A L;
ARRAY : A R R A Y;
DELETE : D E L E T E;
RECALL : R E C A L L;
FILE : F I L E S?;
SET : S E T;
RELEASE : R E L E A S E;
RECYCLE : R E C Y C L E;
CREATE : C R E A T E;
TABLE : T A B L E;
TABLEPROMPT: T A B L E P R O M P T;
DBF : D B F;
NAME : N A M E;
FREE : F R E E;
SELECT : S E L E (C T?)?;
USE : U S E;
READ : R E A D;
EVENTS : E V E N T S;
SHUTDOWN : S H U T D O W N;
CLEAR : C L E A R;
PROCEDURE : P R O C (E D U R E)? | F U N C T I O N;
ENDPROC : E N D P R O C? | E N D F U N C;
DEFINE : D E F I N E;
CLASS : C L A S S;
ENDDEFINE : E N D D E F I N E;
LOCATE : L O C A T E;
CONTINUE : C O N T I N U E;
FOR : F O R;
ENDFOR : E N D F O R;
WHILE : W H I L E;
NOOPTIMIZE : N O O P T I M I Z E;
SAFETY: S A F E T Y;
STATUS : S T A T U S;
BAR : B A R;
MEMOWIDTH : M E M O W I D T H;
CURSOR : C U R S O R;
REFRESH : R E F R E S H;
BELL : B E L L;
CENTURY : C E N T U R Y;
COMPATIBLE: C O M P A T I B L E;
DATE : D A T E;
ADD : A D D;
OBJECT : O B J E C T;
REPLACE : R E P L A C E;
LIBRARY : L I B R A R Y;
SHARED : S H A R E D?;
WAIT : W A I T;
WINDOW : W I N D (O W (S)?)?;
NOWAIT : N O W A I T;
NOCLEAR : N O C L E A R;
NOTIFY : N O T I F Y;
ENDDO : E N D D O;
DECLARE : D E C L A R E;
ERASE : E R A S E;
SYSMENU : S Y S M E N U;
CLOCK : C L O C K;
RETURN : R E T U R N;
PARAMETER : L? P A R A M E T E R S?;
ALTERNATE : A L T E R N A T E;
EXACT : E X A C T;
ALL : A L L;
COUNT : C O U N T;
GOTO : G O (T O)?;
TOP : T O P;
BOTTOM : B O T T O M | B O T T;
RECORD : R E C O R D;
CLOSE : C L O S E;
APPEND : A P P E N D;
BLANK : B L A N K;
NOMENU : N O M E N U;
CASE : C A S E;
ENDCASE : E N D C A S E;
OTHERWISE : O T H E R W I S E;
FROM : F R O M;
REPORT : R E P O R T;
FORM : F O R M;
NOEJECT : N O E J E C T;
PRINTER : P R I N T E R;
PROMPT : P R O M P T;
NOPROMPT : N O P R O M P T;
DB4 : D B '4';
FOXPLUS : F O X P L U S;
NOCONSOLE : N O C O N S O L E;
COPY : C O P Y;
STRUCTURE : S T R U C T U R E;
DELETED : D E L E T E D;
SUM : S U M;
DISTINCT : D I S T I N C T;
INTO : I N T O;
NEXT : N E X T;
REST : R E S T;
SKIPKW : S K I P;
EXCLUSIVE : E X C L (U S I V E)?;
NEAR : N E A R;
MKDIR : (M K D I R | M D);
RMDIR : (R M D I R | R D);
KEY : K E Y;
KEYBOARD : K E Y B O A R D;
LABEL : L A B E L;
PLAIN : P L A I N;
MENU : M E N U;
AT : A T;
LINE : L I N E;
SCREEN : S C R E E N;
NOMARGIN : N O M A R G I N;
PAD : P A D;
OF : O F;
COLOR : C O L O R;
SCHEME : S C H E M E;
BEFORE : B E F O R E;
AFTER : A F T E R;
NEGOTIATE : N E G O T I A T E;
FONT : F O N T;
STYLE : S T Y L E;
MARK : M A R K;
MESSAGE : M E S S A G E;
ACTIVATE : A C T I V A T E;
POPUP : P O P U P S?;
EXTENDED : E X T E N D E D;
SHADOW : S H A D O W;
MARGIN : M A R G I N;
RELATIVE : R E L A T I V E;
SELECTION : S E L E C T I O N;
DEACTIVATE : D E A C T I V A T E;
SAME : S A M E;
NOSHOW : N O S H O W;
STEP : S T E P;
THEN : T H E N;
UNDEFINE : U N D E F (I N E)?;
IFDEF : I F D E F;
PUSH : P U S H;
POP : P O P;
TIMEOUT : T I M E O U T;
ENDWITH : E N D W I T H;
TYPEAHEAD : T Y P E A H E A D;
ALIAS : A L I A S;
ORDER : O R D E R;
SEEK : S E E K;
WHERE : W H E R E;
FILTER : F I L T E R;
RENAME : R E N A M E;
INCLUDE : I N C L U D E;
CLASSLIB : C L A S S L I B;
BY : B Y;
UNIQUE : U N I Q U E;
INDEX : I N D E X;
TAG : T A G;
COMPACT : C O M P A C T;
ASCENDING : A S C E N D I N G;
DESCENDING : D E S C E N D I N G;
CANDIDATE : C A N D I D A T E;
ADDITIVE : A D D I T I V E;
DIMENSION : D I M E N S I O N;
NOT : N O T;
AND : A N D;
OTHERAND : '.' AND '.';
OR : O R;
OTHEROR : '.' OR '.';
SCAN : S C A N;
ENDSCAN : E N D S C A N;
NULL : N U L L;
BOOLEANCHAR : (F | N | T | Y);
NODEFAULT : N O D E F A U L T;
DLLS : D L L S;
MACROS : M A C R O S;
NUMBER : N U M B E R;
ZAP : Z A P;
ROLLOVER : R O L L O V E R;
DEFAULT : D E F A U L T;
SAVE : S A V E;
NOSAVE : N O S A V E;
DATABASE : D A T A (B A S E (S)?)?;
TABLES : T A B L E S;
INDEXES : I N D E X E S;
PACK: P A C K;
REINDEX: R E I N D E X;
MEMO: M E M O;
PROGRAM: P R O G R A M;
SCOPE: (P R O T E C T E D | H I D D E N | P U B L I C | P R I V A T E | L O C A L);
THROW: T H R O W;
EACH: E A C H;
CAST: C A S T;
RUN: R U N;
MULTILOCKS: M U L T I L O C K S;
TRY: T R Y;
CATCH: C A T C H;
FINALLY: F I N A L L Y;
ENDTRY: E N D T R Y;
BROWSE: B R O W S E;
INSERT: I N S E R T;
VALUES: V A L U E S;
MEMVAR: M E M V A R;
TYPE: T Y P E;
CHDIR: C D | C H D I R;
SCATTER: S C A T T E R;
GATHER: G A T H E R;
EXCEPT: E X C E P T;
LIKE: L I K E;
FIELDS: F I E L D S;
ALTER: A L T E R;
COLUMN: C O L U M N;
DROP: D R O P;
DEBUG: D E B U G;
GETS: G E T S;
DEBUGOUT: DEBUG O U T;
MEMORY: M E M O R Y;
MENUS: M E N U S;
RESOURCES: R E S O U R C E S;
HELP: H E L P;
SAY: S A Y;
COLLECTION: C O L L E C T I O N;
SYSTEM: S Y S T E M;
TALK: T A L K;
PROGRAMCONTROL: (C A N C E L | S U S P E N D | R E S U M E | Q U I T | E X I T | L O O P);
RELATION: R E L A T I O N;

ID : [A-Za-z_] [a-zA-Z0-9_]*;

NL : '\n';

WS : [ \t\r] -> channel(1);

UNMATCHED : . ;

fragment A : [Aa];
fragment B : [Bb];
fragment C : [Cc];
fragment D : [Dd];
fragment E : [Ee];
fragment F : [Ff];
fragment G : [Gg];
fragment H : [Hh];
fragment I : [Ii];
fragment J : [Jj];
fragment K : [Kk];
fragment L : [Ll];
fragment M : [Mm];
fragment N : [Nn];
fragment O : [Oo];
fragment P : [Pp];
fragment Q : [Qq];
fragment R : [Rr];
fragment S : [Ss];
fragment T : [Tt];
fragment U : [Uu];
fragment V : [Vv];
fragment W : [Ww];
fragment X : [Xx];
fragment Y : [Yy];
fragment Z : [Zz];
fragment DIGIT : [0-9];
fragment HEXDIGIT : [0-9A-Fa-f];
