CLASS class
ID Factorial
LPARBR {
PUBLIC public
STATIC static
VOID void
ID Main
LPAREN (
ID String
LPARSQ [
RPARSQ ]
ID a
RPAREN )
LPARBR {
ID System
DOT .
ID out
DOT .
ID println
LPAREN (
NEW new
ID FactImpl
LPAREN (
RPAREN )
DOT .
ID Calc
LPAREN (
NUMBER 10
RPAREN )
RPAREN )
SEMICOL ;
RPARBR }
RPARBR }
CLASS class
ID FactImpl
LPARBR {
PUBLIC public
INT int
ID Calc
LPAREN (
INT int
ID num
RPAREN )
LPARBR {
INT int
ID accum
SEMICOL ;
IF if
LPAREN (
ID num
LESS <
NUMBER 1
RPAREN )
LPARBR {
ID accum
EQ =
NUMBER 1
SEMICOL ;
RPARBR }
ELSE else
LPARBR {
ID accum
EQ =
ID num
TIMES *
LPAREN (
THIS this
DOT .
ID Calc
LPAREN (
ID num
MINUS -
NUMBER 1
RPAREN )
RPAREN )
SEMICOL ;
RPARBR }
RETURN return
ID accum
SEMICOL ;
RPARBR }
RPARBR }
