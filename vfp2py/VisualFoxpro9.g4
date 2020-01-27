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
 | MACROLINE lineEnd
 | (controlStmt | cmd) lineEnd
 ;

lineEnd
 : NL
 | EOF
 ;

lines
 : line*
 ;

nongreedyLines
 : line*?
 ;

classDefStart
 : DEFINE CLASS identifier asTypeOf? NL
 ;

classDef
 : classDefStart classProperty* ENDDEFINE lineEnd lineComment*
 ;

classProperty
 : cmd NL
 | lineComment
 | funcDef
 ;

parameter
 : idAttr asType?
 ;

parameters
 : parameter (',' parameter)*
 ;

funcDefStart
 : SCOPE? PROCEDURE idAttr2 ('(' parameters? ')')? asType? NL
 ;

funcDef
 : funcDefStart lines (ENDPROC lineEnd lineComment*)?
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
 : CASE expr NL nongreedyLines
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
 : WITH idAttr asTypeOf? NL lines ENDWITH
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
 : ADD OBJECT identifier asType (WITH idAttr '=' expr (',' idAttr '=' expr)*)? #addObject
 | (PROGRAMCONTROL) #programControl
 | '@' args (CLEAR (TO toArgs=args)? | (SAY sayExpr=expr | STYLE styleExpr=expr)+)? #atPos
 | DO (FORM ('?' | specialExpr) (NAME nameId=identifier LINKED? | WITH args | TO toId=identifier | NOSHOW)*
   | specialExpr (IN specialExpr | WITH args)*) #funcDo
 | (STORE expr TO idAttr (',' idAttr)*
   | idAttr '=' expr) #assign
 | (((SCOPE|EXTERNAL) (ARRAY | DIMENSION | DECLARE)? | DIMENSION | DECLARE | PARAMETER) declarationItem (',' declarationItem)*
   | EXTERNAL PROCEDURE specialExpr) #declaration
 | ('?' '?'? | DEBUGOUT) args? #printStmt
 | WAIT (TO toExpr=expr | WINDOW (AT atExpr1=expr ',' atExpr2=expr)? | NOWAIT | CLEAR | NOCLEAR | TIMEOUT timeout=expr | message=expr)* #waitCmd
 | (ERASE | DELETE FILE) (specialExpr|'?') RECYCLE? #deleteFile
 | (RENAME | COPY FILE) specialExpr TO specialExpr #copyMoveFile
 | (CHDIR | MKDIR | RMDIR) specialExpr #chMkRmDir
 | RETURN expr? #returnStmt
 | ON ((PAD specialExpr | BAR NUMBER_LITERAL) OF specialExpr (ACTIVATE (POPUP | MENU) specialExpr)? | (KEY (LABEL identifier ('+' identifier)?)? | SELECTION BAR NUMBER_LITERAL OF specialExpr | identifier) cmd?) #onStmt
 | RELEASE (ALL | vartype=(PROCEDURE|CLASSLIB)? args | POPUP args EXTENDED?) #release
 | SET setCmd #setStmt
 | PUSH (KEY CLEAR? | (MENU | POPUP) identifier) #push
 | POP (KEY ALL? | MENU (identifier | TO MASTER)* | POPUP identifier) #pop
 | KEYBOARD expr PLAIN? CLEAR? #keyboard

 | DEFINE MENU specialExpr (BAR (AT LINE NUMBER_LITERAL)?) (IN (SCREEN | WINDOW? specialExpr))? NOMARGIN? #defineMenu
 | DEFINE PAD specialExpr OF specialExpr PROMPT expr (AT NUMBER_LITERAL ',' NUMBER_LITERAL)?
         (BEFORE identifier | AFTER identifier)? (NEGOTIATE identifier (',' identifier)?)?
         (FONT identifier (',' NUMBER_LITERAL (',' expr (',' identifier)?)?)?)? (STYLE identifier)?
         (MESSAGE expr)? (KEY identifier ('+' identifier)? (',' expr)?)? (MARK identifier)?
         (SKIPKW (FOR expr)?)? (COLOR SCHEME NUMBER_LITERAL)? #definePad
 | DEFINE POPUP specialExpr SHADOW? MARGIN? RELATIVE? (COLOR SCHEME NUMBER_LITERAL)? #definePopup
 | DEFINE BAR NUMBER_LITERAL OF specialExpr PROMPT expr (MESSAGE expr)? #defineBar
 | ACTIVATE WINDOW (parameters | ALL) (IN (WINDOW? identifier | SCREEN))? (BOTTOM | TOP | SAME)? NOSHOW? #activateWindow
 | ACTIVATE SCREEN #activateScreen
 | ACTIVATE MENU specialExpr NOWAIT? (PAD specialExpr)? #activateMenu
 | ACTIVATE POPUP identifier #activatePopup

 | DEACTIVATE (MENU|POPUP) (ALL | parameters) #deactivate

 | MODIFY WINDOW (SCREEN | identifier) (FROM args TO args | AT args SIZE args | FONT args | STYLE expr | TITLE expr | identifier | ICON FILE specialExpr | FILL FILE specialExpr | COLOR SCHEME expr | COLOR args)* #modifyWindow
 | MODIFY (FILE | COMMAND) ('?' | specialExpr) (IN (WINDOW identifier | SCREEN) | AS expr | identifier)* #modifyFile

 | ERROR expr? #raiseError
 | THROW expr? #throwError

 | CREATE (TABLE|DBF|CURSOR) specialExpr (FREE? '(' tableField (',' tableField)* ')' | FROM ARRAY expr) #createTable
 | ALTER TABLE specialExpr (ADD COLUMN tableField | DROP COLUMN identifier | ALTER COLUMN identifier (NOT NULL)?)* #alterTable
 | SELECT (tablename=specialExpr | (DISTINCT? (specialArgs | '*') (FROM fromExpr=specialExpr)? (WHERE whereExpr=expr)? (INTO (TABLE | CURSOR) intoExpr=specialExpr)? (ORDER BY orderbyid=identifier)?)) #select
 | USE (IN workArea=specialExpr | ORDER TAG? orderExpr=expr | ALIAS aliasExpr=specialExpr | SHARED | EXCLUSIVE | NOUPDATE | name=specialExpr)* #use
 | LOCATE queryCondition* #locate
 | CONTINUE #continueLocate
 | RETRY #retry
 | REPLACE (queryCondition | specialExpr WITH expr)* #replace
 | INDEX ON specialExpr (TAG | TO) specialExpr COMPACT? (ASCENDING | DESCENDING)? (UNIQUE | CANDIDATE)? ADDITIVE? #indexOn
 | COUNT (TO toExpr=expr | queryCondition)* #count
 | SUM (TO toExpr=expr | queryCondition | sumExpr=expr)* #sum
 | SORT TO expr ON expr ('/' identifier)* (',' expr ('/' identifier)*)* (ASCENDING | DESCENDING | FIELDS (LIKE | EXCEPT)? args | queryCondition)* #sortCmd
 | (RECALL | DELETE) (queryCondition | IN inExpr=specialExpr)* #deleteRecord
 | APPEND FROM (ARRAY expr | specialExpr FOR expr | specialExpr ) (TYPE typeExpr=specialExpr)? #appendFrom
 | APPEND BLANK? (IN specialExpr NOMENU | IN specialExpr)? #append
 | INSERT INTO specialExpr (FROM (ARRAY expr | MEMVAR | NAME expr) | ('(' specialArgs ')')? VALUES '(' args ')') #insert
 | SKIPKW expr? (IN specialExpr)? #skipRecord
 | PACK (DATABASE | (MEMO | DBF)? (IN workArea=specialExpr | tableName=specialExpr IN workArea=specialExpr | tableName=specialExpr)?) #pack
 | REINDEX COMPACT? #reindex
 | SEEK seekExpr=expr ((ORDER orderExpr=expr | TAG tagName=specialExpr (OF cdxFileExpr=specialExpr)? | idxFileExpr=specialExpr) (ASCENDING | DESCENDING)?)? (IN tablenameExpr=specialExpr)? #seekRecord
 | UPDATE tableExpr=specialExpr SET identifier '=' expr (',' identifier '=' expr)* (FROM FORCE? fromArgs=specialArgs | JOIN joinArgs=specialArgs | WHERE whereExpr=expr)* #updateCmd
 | GOTO (TOP | BOTTOM | RECORD? expr) (IN specialExpr)? #goRecord
 | COPY (TO ARRAY specialExpr | FIELDS (LIKE | EXCEPT) ? args | queryCondition)* #copyToArray
 | COPY STRUCTURE? TO specialExpr #copyTo
 | ZAP (IN specialExpr)? #zapTable
 | BROWSE (~NL)* #browse
 | SCATTER (FIELDS (LIKE | EXCEPT)? args | MEMO | BLANK | MEMVAR | NAME expr ADDITIVE? | TO expr)* #scatterExpr
 | GATHER (FIELDS (LIKE | EXCEPT)? args | MEMO | MEMVAR | NAME expr | FROM expr)* #gatherExpr

 | CLOSE ((DATABASE | INDEXES | TABLE) ALL? | ALL) #closeStmt
 | (READ EVENTS? | DOEVENTS FORCE?) #readEvent
 | UNLOCK ALL #unlockCmd
 | CLEAR (ALL | CLASS expr | CLASSLIB specialExpr | DEBUG | DLLS specialArgs | EVENTS | ERROR | FIELDS | GETS | MACROS | MEMORY | MENUS | POPUP | PROGRAM | PROMPT | READ ALL? | RESOURCES expr | TYPEAHEAD | WINDOW)? #clearStmt
 | REPORT FORM ('?' | specialExpr) (NOEJECT | TO PRINTER PROMPT? | NOCONSOLE)* #report
 | DECLARE returnType=datatype? identifier IN specialExpr (AS alias=identifier)? dllArgs? #dllDeclare
 | (RUN | EXCLAMATION) ('/' identifier)? (~NL)* #shellRun
 | ASSERT expr (MESSAGE expr)? #assert
 | COMPILE (DATABASE | FORM | CLASSLIB | LABEL | REPORT)? (ALL | ENCRYPT | NODEBUG | AS specialExpr | specialExpr)* #compileCmd
 | LIST scopeClause #listStmt
 | SAVE TO (MEMO specialExpr | specialExpr) (ALL (LIKE | EXCEPT) specialExpr)? #saveToCmd
 | RESTORE FROM specialExpr ADDITIVE? #restoreCmd
 | ZOOM WINDOW specialExpr (MIN | MAX | NORM) (AT expr ',' expr | FROM AT expr ',' expr (SIZE AT expr ',' expr | TO expr ',' expr)?)? #zoomCmd
 | TEXT (TO idAttr | ADDITIVE | TEXTMERGE | NOSHOW | FLAGS flagExpr=expr | PRETEXT pretext=expr)* NL textChunk ENDTEXT #textBlock
 | SHOW GETS #showCmd
 | HIDE WINDOW (ALL | SCREEN | args) #hideCmd
 | '=' expr #exprCmd
 | complexId #complexIdCmd
 ;

queryCondition
 : scopeClause
 | FOR expr
 | WHILE expr
 | NOOPTIMIZE
 ;

textChunk
 : (~ENDTEXT)*
 ;

dllArgs
 : dllArg (',' dllArg)*
 ;

dllArg
 : datatype '@'? identifier?
 ;

tableField
 : identifier identifier arrayIndex?
 ;

setCmd
 : setword=ALTERNATE (ON | OFF | TO specialExpr ADDITIVE?)
 | setword=(ASSERT | ASSERTS) (ON | OFF)
 | setword=BELL (ON | OFF | TO specialExpr)
 | setword=CENTURY (ON | OFF | TO (expr (ROLLOVER expr)?)?) 
 | setword=CLASSLIB TO specialExpr (IN specialExpr)? (ALIAS specialExpr)? ADDITIVE?
 | setword=CLOCK (ON | OFF | STATUS | TO (expr ',' expr)?)
 | setword=COMPATIBLE (ON | OFF | DB4 | FOXPLUS) (PROMPT | NOPROMPT)?
 | setword=CONSOLE (ON | OFF)
 | setword=CURSOR (ON | OFF)
 | setword=DATABASE TO specialExpr
 | setword=DATASESSION TO expr
 | setword=DATE TO? identifier
 | setword=DEFAULT TO specialExpr
 | setword=(DELETE | DELETED) (ON | OFF)
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
 | setword=STEP (ON | OFF)
 | setword=SYSMENU (ON | OFF | TO (DEFAULT | expr)? | SAVE | NOSAVE)
 | setword=TABLEPROMPT (ON | OFF)
 | setword=TALK (ON | OFF)
 | setword=TYPEAHEAD TO expr
 | setword=UNIQUE (ON | OFF)
 ;

declarationItem
 : (idAttr2 arrayIndex | idAttr asTypeOf?)
 ;

asType
 : AS datatype
 ;

asTypeOf
 : asType (OF specialExpr)?
 ;

argsItem
 : ',' expr?
 ;

args
 : expr argsItem*
 | argsItem+
 ;

specialArgs
 : specialExpr (',' specialExpr)*
 ;

reference
 : '@' idAttr
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
 | expr andOp expr #booleanAnd
 | expr orOp expr #booleanOr
 | constant #constantExpr
 | CAST '(' expr asType ')' #castExpr
 | (PERIOD | idAttr ':' ':')? atom trailer? #atomExpr
 ;

andOp
 : OTHERAND
 | AND
 ;

orOp
 : OTHEROR
 | OR
 ;

complexId
 : (PERIOD | idAttr ':' ':')? atom trailer
 | (PERIOD | idAttr ':' ':') atom trailer?
 ;

atom
 : identifier
 | reference
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
 : idAttr
 ;

scopeClause
 : ALL | NEXT expr | RECORD expr | REST
 ;

identifier
 : ID
 | ACTIVATE
 | ADD
 | ADDITIVE
 | AFTER
 | ALIAS
 | ALL
 | ALTER
 | ALTERNATE
 | AND
 | APPEND
 | ARRAY
 | AS
 | ASCENDING
 | ASSERT
 | ASSERTS
 | AT
 | BAR
 | BEFORE
 | BELL
 | BLANK
 | BOOLEANCHAR
 | BOTTOM
 | BROWSE
 | BY
 | CANDIDATE
 | CASE
 | CAST
 | CATCH
 | CENTURY
 | CHDIR
 | CLASS
 | CLASSLIB
 | CLEAR
 | CLOCK
 | CLOSE
 | COLLECTION
 | COLOR
 | COLUMN
 | COMMAND
 | COMPACT
 | COMPATIBLE
 | COMPILE
 | CONSOLE
 | CONTINUE
 | COPY
 | COUNT
 | CREATE
 | CURSOR
 | DATABASE
 | DATASESSION
 | DATE
 | DBF
 | DEACTIVATE
 | DEBUG
 | DEBUGOUT
 | DECLARE
 | DEFAULT
 | DEFINE
 | DELETE
 | DELETED
 | DESCENDING
 | DIMENSION
 | DISTINCT
 | DLLS
 | DO
 | DOEVENTS
 | DROP
 | EACH
 | ELIF
 | ELSE
 | ENCRYPT
 | ENDCASE
 | ENDDEFINE
 | ENDDO
 | ENDFOR
 | ENDIF
 | ENDPROC
 | ENDSCAN
 | ENDTEXT
 | ENDTRY
 | ENDWITH
 | ERASE
 | ERROR
 | EVENTS
 | EXACT
 | EXCEPT
 | EXCLUSIVE
 | EXTENDED
 | EXTERNAL
 | FIELDS
 | FILE
 | FILL
 | FILTER
 | FINALLY
 | FLAGS
 | FONT
 | FOR
 | FORCE
 | FORM
 | FOXPLUS
 | FREE
 | FROM
 | GATHER
 | GETS
 | GOTO
 | HELP
 | HIDE
 | ICON
 | IF
 | IFDEF
 | IN
 | INCLUDE
 | INDEX
 | INDEXES
 | INSERT
 | INTO
 | JOIN
 | KEY
 | KEYBOARD
 | LABEL
 | LIBRARY
 | LIKE
 | LINE
 | LINKED
 | LIST
 | LOCATE
 | MACROS
 | MARGIN
 | MARK
 | MASTER
 | MAX
 | MEMO
 | MEMORY
 | MEMOWIDTH
 | MEMVAR
 | MENU
 | MENUS
 | MESSAGE
 | MIN
 | MKDIR
 | MODIFY
 | MULTILOCKS
 | NAME
 | NEAR
 | NEGOTIATE
 | NEXT
 | NOCLEAR
 | NOCONSOLE
 | NODEBUG
 | NOEJECT
 | NOMARGIN
 | NOMENU
 | NOOPTIMIZE
 | NOPROMPT
 | NORM
 | NOSAVE
 | NOSHOW
 | NOT
 | NOTE
 | NOTIFY
 | NOUPDATE
 | NOWAIT
 | NULL
 | NUMBER
 | OBJECT
 | OF
 | OFF
 | ON
 | OR
 | ORDER
 | OTHERWISE
 | PACK
 | PAD
 | PARAMETER
 | PLAIN
 | POP
 | POPUP
 | PRETEXT
 | PRINTER
 | PROCEDURE
 | PROGRAM
 | PROGRAMCONTROL
 | PROMPT
 | PUSH
 | READ
 | RECALL
 | RECORD
 | RECYCLE
 | REFRESH
 | REINDEX
 | RELATION
 | RELATIVE
 | RELEASE
 | RENAME
 | REPLACE
 | REPORT
 | RESOURCES
 | REST
 | RESTORE
 | RETRY
 | RETURN
 | RMDIR
 | ROLLOVER
 | RUN
 | SAFETY
 | SAME
 | SAVE
 | SAY
 | SCAN
 | SCATTER
 | SCHEME
 | SCOPE
 | SCREEN
 | SEEK
 | SELECT
 | SELECTION
 | SET
 | SHADOW
 | SHARED
 | SHOW
 | SHUTDOWN
 | SIZE
 | SKIPKW
 | SORT
 | STATUS
 | STEP
 | STORE
 | STRUCTURE
 | STYLE
 | SUM
 | SYSMENU
 | SYSTEM
 | TABLE
 | TABLEPROMPT
 | TAG
 | TALK
 | TEXT
 | TEXTMERGE
 | THEN
 | THROW
 | TIMEOUT
 | TITLE
 | TO
 | TOP
 | TRY
 | TYPE
 | TYPEAHEAD
 | UNDEFINE
 | UNIQUE
 | UNLOCK
 | UPDATE
 | USE
 | VALUES
 | WAIT
 | WHERE
 | WHILE
 | WINDOW
 | WITH
 | ZAP
 | ZOOM
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

MACROLINE : ~[\n&]* '&' ID (~'\n')*;

ACTIVATE : A C T I (V (A (T E?)?)?)?;
ADD : A D D;
ADDITIVE : A D D I T I V E;
AFTER : A F T E R;
ALIAS : A L I A S;
ALL : A L L;
ALTER: A L T E R;
ALTERNATE : A L T E R N A T E;
AND : A N D;
APPEND : A P P E (N D?)?;
ARRAY : A R R A Y?;
AS : A S;
ASCENDING : A S C E N D I N G;
ASSERT: A S S E (R T?)?;
ASSERTS: A S S E R T S;
AT : A T;
//'AVER|AGE'
BAR : B A R;
BEFORE : B E F O R E;
BELL : B E L L;
BLANK : B L A N K?;
BOOLEANCHAR : (F | N | T | Y);
BOTTOM : B O T T O M | B O T T;
//'BRIT|ISH'
BROWSE: B R O W (S E?)?;
//'BUIL|D'
BY : B Y;
//'CALC|ULATE'
CANDIDATE : C A N D I D A T E;
CASE : C A S E;
CAST: C A S T;
CATCH: C A T C H?;
CENTURY : C E N T (U (R Y?)?)?;
//'CHAN|GE'
CHDIR: C D | C H D I R?;
CLASS : C L A S S;
CLASSLIB : C L A S S L I B;
CLEAR : C L E A R?;
CLOCK : C L O C K;
CLOSE : C L O S E?;
COLLECTION: C O L L E C T I O N;
COLOR : C O L O R;
COLUMN: C O L U M N;
COMMAND: C O M M A N D;
COMPACT : C O M P A C T;
COMPATIBLE: C O M P A T I B L E;
COMPILE: C O M P (I (L E?)?)?;
CONSOLE: C O N S O L E;
CONTINUE : C O N T (I (N (U E?)?)?)?;
COPY : C O P Y;
COUNT : C O U N T?;
CREATE : C R E A (T E?)?;
CURSOR : C U R S (O R?)?;
DATABASE : D A T A (B A S E (S)?)?;
DATASESSION: D A T A S E S S I O N;
DATE : D A T E;
DB4 : D B '4';
DBF : D B F;
DEACTIVATE : D E A C (T (I (V (A (T E?)?)?)?)?)?;
DEBUG: D E B U G?;
DEBUGOUT: D E B U G O (U T?)?;
DECLARE : D E C L (A (R E?)?)?;
DEFAULT : D E F A U L T;
DEFINE : D E F I (N E?)?;
DELETE : D E L E (T E?)?;
DELETED : D E L E T E D;
DESCENDING : D E S C E N D I N G;
//'DEVI|CE'
DIMENSION : D I M E (N (S (I (O N?)?)?)?)?;
//'DISP|LAY'
DISTINCT : D I S T I N C T;
DLLS : D L L S;
DO : D O;
DOEVENTS: D O E V (E (N (T S?)?)?)?;
DROP: D R O P;
EACH: E A C H;
//'EJEC|T'
ELIF : E L I F;
ELSE : E L S E;
ENCRYPT: E N C R Y P T;
ENDCASE : E N D C (A (S E?)?)?;
ENDDEFINE : E N D D E (F (I (N E?)?)?)?;
ENDDO : E N D D O;
ENDFOR : E N D F O R?;
ENDIF : E N D I F?;
ENDPROC : E N D P (R (O C?)?)? | E N D (F (U (N C?)?)?)?;
//'ENDPRI|NTJOB'
ENDSCAN : E N D S (C (A N?)?)?;
ENDTEXT: E N D T (E (X T?)?)?;
ENDTRY: E N D T R Y?;
ENDWITH : E N D W (I (T H?)?)?;
ERASE : E R A S E?;
ERROR : E R R O R?;
EVENTS : E V E N T S;
EXACT : E X A C T?;
EXCEPT: E X C E P T;
EXCLUSIVE : E X C L (U S I V E)?;
//'EXPO|RT'
EXTENDED : E X T E N D E D;
EXTERNAL: E X T E (R (N (A L?)?)?)?;
FIELDS: F I E L D S;
FILE : F I L E S?;
FILL: F I L L;
FILTER : F I L T (E R?)?;
FINALLY: F I N A (L (L Y?)?)?;
FLAGS: F L A G S;
//'FLUS|H'
FONT : F O N T;
FOR : F O R;
FORCE: F O R C E;
FORM : F O R M;
FOXPLUS : F O X P L U S;
FREE : F R E E;
FROM : F R O M;
GATHER: G A T H (E R?)?;
//'GETE|XPR'
GETS: G E T S;
GOTO : G O (T O)?;
HELP: H E L P;
HIDE: H I D E;
ICON: I C O N;
IF : I F;
IFDEF : I F D E F;
//'IMPL|EMENTS'
IN : I N;
INCLUDE : I N C L U D E;
INDEX : I N D E X;
INDEXES : I N D E X E S;
INSERT: I N S E (R T?)?;
INTO : I N T O;
JOIN: J O I N;
KEY : K E Y;
KEYBOARD : K E Y B (O (A (R D?)?)?)?;
LABEL : L A B E L;
LIBRARY : L I B R A R Y;
LIKE: L I K E;
LINE : L I N E;
LINKED: L I N K E D;
LIST: L I S T;
LOCATE : L O C A (T E?)?;
MACROS : M A C R O S;
MARGIN : M A R G I N;
MARK : M A R K;
MASTER: M A S T E R;
MAX: M A X;
MEMO: M E M O;
MEMORY: M E M O R Y;
MEMOWIDTH : M E M O W I D T H;
MEMVAR: M E M V A R;
MENU : M E N U;
MENUS: M E N U S;
MESSAGE : M E S S (A (G E?)?)?;
MIN: M I N;
MKDIR : (M K D I R? | M D);
MODIFY: M O D I (F Y?)?;
//'MOUS|E'
MULTILOCKS: M U L T I L O C K S;
NAME : N A M E;
NEAR : N E A R;
NEGOTIATE : N E G O T I A T E;
NEXT : N E X T;
NOCLEAR : N O C L E A R;
NOCONSOLE : N O C O N S O L E;
NODEBUG: N O DEBUG;
NOEJECT : N O E J E C T;
NOMARGIN : N O M A R G I N;
NOMENU : N O M E N U;
NOOPTIMIZE : N O O P T I M I Z E;
NOPROMPT : N O P R O M P T;
NORM: N O R M;
NOSAVE : N O S A V E;
NOSHOW : N O S H O W;
NOT : N O T;
NOTE: N O T E;
NOTIFY : N O T I F Y;
NOUPDATE: N O U P D A T E;
NOWAIT : N O W A I T;
NULL : N U L L;
NUMBER : N U M B E R;
OBJECT : O B J E C T;
OF : O F;
OFF : O F F;
ON : O N;
OR : O R;
ORDER : O R D E R;
OTHERAND : '.' AND '.';
OTHEROR : '.' OR '.';
OTHERWISE : O T H E (R (W (I (S E?)?)?)?)?;
PACK: P A C K;
PAD : P A D;
PARAMETER : L P A R (A (M (E (T (E (R S?)?)?)?)?)?)? | P A R A (M (E (T (E (R S?)?)?)?)?)?;
//'PICT|URE'
PLAIN : P L A I N;
POP : P O P;
POPUP : P O P U P S?;
PRETEXT: P R E TEXT;
PRINTER : P R I N (T (E R?)?)?;
//'PRIN|TJOB'
PROCEDURE : P R O C (E (D (U (R E?)?)?)?)? | F U N C (T (I (O N?)?)?)?;
PROGRAM: P R O G R A M;
PROGRAMCONTROL: (C A N C (E L?)? | S U S P (E (N D?)?)? | R E S U (M E?)? | Q U I T | E X I T | L O O P | N O D E (F (A (U (L T?)?)?)?)?);
PROMPT : P R O M P T;
PUSH : P U S H;
READ : R E A D;
RECALL : R E C A (L L?)?;
RECORD : R E C O R D;
RECYCLE : R E C Y C L E;
REFRESH : R E F R E S H;
REINDEX: R E I N (D (E X?)?)?;
RELATION: R E L A T I O N;
RELATIVE : R E L A T I V E;
RELEASE : R E L E (A (S E?)?)?;
//'REMO|VE'
RENAME : R E N A (M E?)?;
REPLACE : R E P L (A (C E?)?)?;
REPORT : R E P O R T;
RESOURCES: R E S O U R C E S;
REST : R E S T;
RESTORE: R E S T (O (R E?)?)?;
RETRY: R E T R Y?;
RETURN : R E T U (R N?)?;
RMDIR : (R M D I R? | R D);
//'ROLL|BACK'
ROLLOVER : R O L L O V E R;
RUN: R U N;
SAFETY: S A F E (T Y?)?;
SAME : S A M E;
SAVE : S A V E;
SAY: S A Y;
SCAN : S C A N;
SCATTER: S C A T (T (E R?)?)?;
SCHEME : S C H E M E;
SCOPE: (P R O T (E (C (T (E D?)?)?)?)? | H I D D (E N?)? | P U B L (I C?)? | P R I V (A (T E?)?)? | L O C A L);
SCREEN : S C R E (E N?)?;
SEEK : S E E K;
SELECT : S E L E (C T?)?;
SELECTION : S E L E C T I O N;
SET : S E T;
SHADOW : S H A D O W;
SHARED : S H A R E D?;
SHOW: S H O W;
SHUTDOWN : S H U T D O W N;
SIZE: S I Z E;
SKIPKW : S K I P;
SORT: S O R T;
STATUS : S T A T U S;
STEP : S T E P;
STORE : S T O R E?;
STRUCTURE : S T R U (C (T (U (R E?)?)?)?)?;
STYLE : S T Y L E;
SUM : S U M;
SYSMENU : S Y S M E N U;
SYSTEM: S Y S T E M;
TABLE : T A B L (E S?)?;
TABLEPROMPT: T A B L E P R O M P T;
TAG : T A G;
TALK: T A L K;
TEXT: T E X T;
TEXTMERGE: TEXT M E R G E;
THEN : T H E N;
THROW: T H R O W?;
TIMEOUT : T I M E (O (U T?)?)?;
TITLE: T I T L E;
TO : T O;
TOP : T O P;
//'TOTA|L'
TRY: T R Y;
TYPE: T Y P E;
TYPEAHEAD : T Y P E A H E A D;
UNDEFINE : U N D E F (I N E)?;
UNIQUE : U N I Q U E;
UNLOCK: U N L O (C K?)?;
UPDATE: U P D A (T E?)?;
USE : U S E;
VALUES: V A L U E S;
WAIT : W A I T;
WHERE : W H E R E;
WHILE : W H I L E;
WINDOW : W I N D (O (W S?)?)?;
WITH : W I T H;
ZAP : Z A P;
ZOOM: Z O O M;

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

