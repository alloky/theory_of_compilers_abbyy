CLASS class
ID BinaryTree
LPARBR {
PUBLIC public
STATIC static
VOID void
ID main
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
ID BT
LPAREN (
RPAREN )
DOT .
ID Start
LPAREN (
RPAREN )
RPAREN )
SEMICOL ;
RPARBR }
RPARBR }
CLASS class
ID BT
LPARBR {
PUBLIC public
INT int
ID Start
LPAREN (
RPAREN )
LPARBR {
ID Tree
ID root
SEMICOL ;
ID boolean
ID ntb
SEMICOL ;
INT int
ID nti
SEMICOL ;
ID root
EQ =
NEW new
ID Tree
LPAREN (
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID root
DOT .
ID Init
LPAREN (
NUMBER 16
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID root
DOT .
ID Print
LPAREN (
RPAREN )
SEMICOL ;
ID System
DOT .
ID out
DOT .
ID println
LPAREN (
NUMBER 100000000
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID root
DOT .
ID Insert
LPAREN (
NUMBER 8
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID root
DOT .
ID Print
LPAREN (
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID root
DOT .
ID Insert
LPAREN (
NUMBER 24
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID root
DOT .
ID Insert
LPAREN (
NUMBER 4
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID root
DOT .
ID Insert
LPAREN (
NUMBER 12
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID root
DOT .
ID Insert
LPAREN (
NUMBER 20
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID root
DOT .
ID Insert
LPAREN (
NUMBER 28
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID root
DOT .
ID Insert
LPAREN (
NUMBER 14
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID root
DOT .
ID Print
LPAREN (
RPAREN )
SEMICOL ;
ID System
DOT .
ID out
DOT .
ID println
LPAREN (
ID root
DOT .
ID Search
LPAREN (
NUMBER 24
RPAREN )
RPAREN )
SEMICOL ;
ID System
DOT .
ID out
DOT .
ID println
LPAREN (
ID root
DOT .
ID Search
LPAREN (
NUMBER 12
RPAREN )
RPAREN )
SEMICOL ;
ID System
DOT .
ID out
DOT .
ID println
LPAREN (
ID root
DOT .
ID Search
LPAREN (
NUMBER 16
RPAREN )
RPAREN )
SEMICOL ;
ID System
DOT .
ID out
DOT .
ID println
LPAREN (
ID root
DOT .
ID Search
LPAREN (
NUMBER 50
RPAREN )
RPAREN )
SEMICOL ;
ID System
DOT .
ID out
DOT .
ID println
LPAREN (
ID root
DOT .
ID Search
LPAREN (
NUMBER 12
RPAREN )
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID root
DOT .
ID Delete
LPAREN (
NUMBER 12
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID root
DOT .
ID Print
LPAREN (
RPAREN )
SEMICOL ;
ID System
DOT .
ID out
DOT .
ID println
LPAREN (
ID root
DOT .
ID Search
LPAREN (
NUMBER 12
RPAREN )
RPAREN )
SEMICOL ;
RETURN return
NUMBER 0
SEMICOL ;
RPARBR }
RPARBR }
CLASS class
ID Tree
LPARBR {
ID Tree
ID left
SEMICOL ;
ID Tree
ID right
SEMICOL ;
INT int
ID key
SEMICOL ;
ID boolean
ID has_left
SEMICOL ;
ID boolean
ID has_right
SEMICOL ;
ID Tree
ID my_null
SEMICOL ;
PUBLIC public
ID boolean
ID Init
LPAREN (
INT int
ID v_key
RPAREN )
LPARBR {
ID key
EQ =
ID v_key
SEMICOL ;
ID has_left
EQ =
ID false
SEMICOL ;
ID has_right
EQ =
ID false
SEMICOL ;
RETURN return
ID true
SEMICOL ;
RPARBR }
PUBLIC public
ID boolean
ID SetRight
LPAREN (
ID Tree
ID rn
RPAREN )
LPARBR {
ID right
EQ =
ID rn
SEMICOL ;
RETURN return
ID true
SEMICOL ;
RPARBR }
PUBLIC public
ID boolean
ID SetLeft
LPAREN (
ID Tree
ID ln
RPAREN )
LPARBR {
ID left
EQ =
ID ln
SEMICOL ;
RETURN return
ID true
SEMICOL ;
RPARBR }
PUBLIC public
ID Tree
ID GetRight
LPAREN (
RPAREN )
LPARBR {
RETURN return
ID right
SEMICOL ;
RPARBR }
PUBLIC public
ID Tree
ID GetLeft
LPAREN (
RPAREN )
LPARBR {
RETURN return
ID left
SEMICOL ;
RPARBR }
PUBLIC public
INT int
ID GetKey
LPAREN (
RPAREN )
LPARBR {
RETURN return
ID key
SEMICOL ;
RPARBR }
PUBLIC public
ID boolean
ID SetKey
LPAREN (
INT int
ID v_key
RPAREN )
LPARBR {
ID key
EQ =
ID v_key
SEMICOL ;
RETURN return
ID true
SEMICOL ;
RPARBR }
PUBLIC public
ID boolean
ID GetHas_Right
LPAREN (
RPAREN )
LPARBR {
RETURN return
ID has_right
SEMICOL ;
RPARBR }
PUBLIC public
ID boolean
ID GetHas_Left
LPAREN (
RPAREN )
LPARBR {
RETURN return
ID has_left
SEMICOL ;
RPARBR }
PUBLIC public
ID boolean
ID SetHas_Left
LPAREN (
ID boolean
ID val
RPAREN )
LPARBR {
ID has_left
EQ =
ID val
SEMICOL ;
RETURN return
ID true
SEMICOL ;
RPARBR }
PUBLIC public
ID boolean
ID SetHas_Right
LPAREN (
ID boolean
ID val
RPAREN )
LPARBR {
ID has_right
EQ =
ID val
SEMICOL ;
RETURN return
ID true
SEMICOL ;
RPARBR }
PUBLIC public
ID boolean
ID Compare
LPAREN (
INT int
ID num1
COMMA ,
INT int
ID num2
RPAREN )
LPARBR {
ID boolean
ID ntb
SEMICOL ;
INT int
ID nti
SEMICOL ;
ID ntb
EQ =
ID false
SEMICOL ;
ID nti
EQ =
ID num2
PLUS +
NUMBER 1
SEMICOL ;
IF if
LPAREN (
ID num1
LESS <
ID num2
RPAREN )
ID ntb
EQ =
ID false
SEMICOL ;
ELSE else
IF if
LPAREN (
NOT !
LPAREN (
ID num1
LESS <
ID nti
RPAREN )
RPAREN )
ID ntb
EQ =
ID false
SEMICOL ;
ELSE else
ID ntb
EQ =
ID true
SEMICOL ;
RETURN return
ID ntb
SEMICOL ;
RPARBR }
PUBLIC public
ID boolean
ID Insert
LPAREN (
INT int
ID v_key
RPAREN )
LPARBR {
ID Tree
ID new_node
SEMICOL ;
ID boolean
ID ntb
SEMICOL ;
ID boolean
ID cont
SEMICOL ;
INT int
ID key_aux
SEMICOL ;
ID Tree
ID current_node
SEMICOL ;
ID new_node
EQ =
NEW new
ID Tree
LPAREN (
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID new_node
DOT .
ID Init
LPAREN (
ID v_key
RPAREN )
SEMICOL ;
ID current_node
EQ =
THIS this
SEMICOL ;
ID cont
EQ =
ID true
SEMICOL ;
WHILE while
LPAREN (
ID cont
RPAREN )
LPARBR {
ID key_aux
EQ =
ID current_node
DOT .
ID GetKey
LPAREN (
RPAREN )
SEMICOL ;
IF if
LPAREN (
ID v_key
LESS <
ID key_aux
RPAREN )
LPARBR {
IF if
LPAREN (
ID current_node
DOT .
ID GetHas_Left
LPAREN (
RPAREN )
RPAREN )
ID current_node
EQ =
ID current_node
DOT .
ID GetLeft
LPAREN (
RPAREN )
SEMICOL ;
ELSE else
LPARBR {
ID cont
EQ =
ID false
SEMICOL ;
ID ntb
EQ =
ID current_node
DOT .
ID SetHas_Left
LPAREN (
ID true
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID current_node
DOT .
ID SetLeft
LPAREN (
ID new_node
RPAREN )
SEMICOL ;
RPARBR }
RPARBR }
ELSE else
LPARBR {
IF if
LPAREN (
ID current_node
DOT .
ID GetHas_Right
LPAREN (
RPAREN )
RPAREN )
ID current_node
EQ =
ID current_node
DOT .
ID GetRight
LPAREN (
RPAREN )
SEMICOL ;
ELSE else
LPARBR {
ID cont
EQ =
ID false
SEMICOL ;
ID ntb
EQ =
ID current_node
DOT .
ID SetHas_Right
LPAREN (
ID true
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID current_node
DOT .
ID SetRight
LPAREN (
ID new_node
RPAREN )
SEMICOL ;
RPARBR }
RPARBR }
RPARBR }
RETURN return
ID true
SEMICOL ;
RPARBR }
PUBLIC public
ID boolean
ID Delete
LPAREN (
INT int
ID v_key
RPAREN )
LPARBR {
ID Tree
ID current_node
SEMICOL ;
ID Tree
ID parent_node
SEMICOL ;
ID boolean
ID cont
SEMICOL ;
ID boolean
ID found
SEMICOL ;
ID boolean
ID is_root
SEMICOL ;
INT int
ID key_aux
SEMICOL ;
ID boolean
ID ntb
SEMICOL ;
ID current_node
EQ =
THIS this
SEMICOL ;
ID parent_node
EQ =
THIS this
SEMICOL ;
ID cont
EQ =
ID true
SEMICOL ;
ID found
EQ =
ID false
SEMICOL ;
ID is_root
EQ =
ID true
SEMICOL ;
WHILE while
LPAREN (
ID cont
RPAREN )
LPARBR {
ID key_aux
EQ =
ID current_node
DOT .
ID GetKey
LPAREN (
RPAREN )
SEMICOL ;
IF if
LPAREN (
ID v_key
LESS <
ID key_aux
RPAREN )
IF if
LPAREN (
ID current_node
DOT .
ID GetHas_Left
LPAREN (
RPAREN )
RPAREN )
LPARBR {
ID parent_node
EQ =
ID current_node
SEMICOL ;
ID current_node
EQ =
ID current_node
DOT .
ID GetLeft
LPAREN (
RPAREN )
SEMICOL ;
RPARBR }
ELSE else
ID cont
EQ =
ID false
SEMICOL ;
ELSE else
IF if
LPAREN (
ID key_aux
LESS <
ID v_key
RPAREN )
IF if
LPAREN (
ID current_node
DOT .
ID GetHas_Right
LPAREN (
RPAREN )
RPAREN )
LPARBR {
ID parent_node
EQ =
ID current_node
SEMICOL ;
ID current_node
EQ =
ID current_node
DOT .
ID GetRight
LPAREN (
RPAREN )
SEMICOL ;
RPARBR }
ELSE else
ID cont
EQ =
ID false
SEMICOL ;
ELSE else
LPARBR {
IF if
LPAREN (
ID is_root
RPAREN )
IF if
LPAREN (
LPAREN (
NOT !
ID current_node
DOT .
ID GetHas_Right
LPAREN (
RPAREN )
RPAREN )
AND &&
LPAREN (
NOT !
ID current_node
DOT .
ID GetHas_Left
LPAREN (
RPAREN )
RPAREN )
RPAREN )
ID ntb
EQ =
ID true
SEMICOL ;
ELSE else
ID ntb
EQ =
THIS this
DOT .
ID Remove
LPAREN (
ID parent_node
COMMA ,
ID current_node
RPAREN )
SEMICOL ;
ELSE else
ID ntb
EQ =
THIS this
DOT .
ID Remove
LPAREN (
ID parent_node
COMMA ,
ID current_node
RPAREN )
SEMICOL ;
ID found
EQ =
ID true
SEMICOL ;
ID cont
EQ =
ID false
SEMICOL ;
RPARBR }
ID is_root
EQ =
ID false
SEMICOL ;
RPARBR }
RETURN return
ID found
SEMICOL ;
RPARBR }
PUBLIC public
ID boolean
ID Remove
LPAREN (
ID Tree
ID p_node
COMMA ,
ID Tree
ID c_node
RPAREN )
LPARBR {
ID boolean
ID ntb
SEMICOL ;
INT int
ID auxkey1
SEMICOL ;
INT int
ID auxkey2
SEMICOL ;
IF if
LPAREN (
ID c_node
DOT .
ID GetHas_Left
LPAREN (
RPAREN )
RPAREN )
ID ntb
EQ =
THIS this
DOT .
ID RemoveLeft
LPAREN (
ID p_node
COMMA ,
ID c_node
RPAREN )
SEMICOL ;
ELSE else
IF if
LPAREN (
ID c_node
DOT .
ID GetHas_Right
LPAREN (
RPAREN )
RPAREN )
ID ntb
EQ =
THIS this
DOT .
ID RemoveRight
LPAREN (
ID p_node
COMMA ,
ID c_node
RPAREN )
SEMICOL ;
ELSE else
LPARBR {
ID auxkey1
EQ =
ID c_node
DOT .
ID GetKey
LPAREN (
RPAREN )
SEMICOL ;
ID auxkey2
EQ =
LPAREN (
ID p_node
DOT .
ID GetLeft
LPAREN (
RPAREN )
RPAREN )
DOT .
ID GetKey
LPAREN (
RPAREN )
SEMICOL ;
IF if
LPAREN (
THIS this
DOT .
ID Compare
LPAREN (
ID auxkey1
COMMA ,
ID auxkey2
RPAREN )
RPAREN )
LPARBR {
ID ntb
EQ =
ID p_node
DOT .
ID SetLeft
LPAREN (
ID my_null
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID p_node
DOT .
ID SetHas_Left
LPAREN (
ID false
RPAREN )
SEMICOL ;
RPARBR }
ELSE else
LPARBR {
ID ntb
EQ =
ID p_node
DOT .
ID SetRight
LPAREN (
ID my_null
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID p_node
DOT .
ID SetHas_Right
LPAREN (
ID false
RPAREN )
SEMICOL ;
RPARBR }
RPARBR }
RETURN return
ID true
SEMICOL ;
RPARBR }
PUBLIC public
ID boolean
ID RemoveRight
LPAREN (
ID Tree
ID p_node
COMMA ,
ID Tree
ID c_node
RPAREN )
LPARBR {
ID boolean
ID ntb
SEMICOL ;
WHILE while
LPAREN (
ID c_node
DOT .
ID GetHas_Right
LPAREN (
RPAREN )
RPAREN )
LPARBR {
ID ntb
EQ =
ID c_node
DOT .
ID SetKey
LPAREN (
LPAREN (
ID c_node
DOT .
ID GetRight
LPAREN (
RPAREN )
RPAREN )
DOT .
ID GetKey
LPAREN (
RPAREN )
RPAREN )
SEMICOL ;
ID p_node
EQ =
ID c_node
SEMICOL ;
ID c_node
EQ =
ID c_node
DOT .
ID GetRight
LPAREN (
RPAREN )
SEMICOL ;
RPARBR }
ID ntb
EQ =
ID p_node
DOT .
ID SetRight
LPAREN (
ID my_null
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID p_node
DOT .
ID SetHas_Right
LPAREN (
ID false
RPAREN )
SEMICOL ;
RETURN return
ID true
SEMICOL ;
RPARBR }
PUBLIC public
ID boolean
ID RemoveLeft
LPAREN (
ID Tree
ID p_node
COMMA ,
ID Tree
ID c_node
RPAREN )
LPARBR {
ID boolean
ID ntb
SEMICOL ;
WHILE while
LPAREN (
ID c_node
DOT .
ID GetHas_Left
LPAREN (
RPAREN )
RPAREN )
LPARBR {
ID ntb
EQ =
ID c_node
DOT .
ID SetKey
LPAREN (
LPAREN (
ID c_node
DOT .
ID GetLeft
LPAREN (
RPAREN )
RPAREN )
DOT .
ID GetKey
LPAREN (
RPAREN )
RPAREN )
SEMICOL ;
ID p_node
EQ =
ID c_node
SEMICOL ;
ID c_node
EQ =
ID c_node
DOT .
ID GetLeft
LPAREN (
RPAREN )
SEMICOL ;
RPARBR }
ID ntb
EQ =
ID p_node
DOT .
ID SetLeft
LPAREN (
ID my_null
RPAREN )
SEMICOL ;
ID ntb
EQ =
ID p_node
DOT .
ID SetHas_Left
LPAREN (
ID false
RPAREN )
SEMICOL ;
RETURN return
ID true
SEMICOL ;
RPARBR }
PUBLIC public
INT int
ID Search
LPAREN (
INT int
ID v_key
RPAREN )
LPARBR {
ID boolean
ID cont
SEMICOL ;
INT int
ID ifound
SEMICOL ;
ID Tree
ID current_node
SEMICOL ;
INT int
ID key_aux
SEMICOL ;
ID current_node
EQ =
THIS this
SEMICOL ;
ID cont
EQ =
ID true
SEMICOL ;
ID ifound
EQ =
NUMBER 0
SEMICOL ;
WHILE while
LPAREN (
ID cont
RPAREN )
LPARBR {
ID key_aux
EQ =
ID current_node
DOT .
ID GetKey
LPAREN (
RPAREN )
SEMICOL ;
IF if
LPAREN (
ID v_key
LESS <
ID key_aux
RPAREN )
IF if
LPAREN (
ID current_node
DOT .
ID GetHas_Left
LPAREN (
RPAREN )
RPAREN )
ID current_node
EQ =
ID current_node
DOT .
ID GetLeft
LPAREN (
RPAREN )
SEMICOL ;
ELSE else
ID cont
EQ =
ID false
SEMICOL ;
ELSE else
IF if
LPAREN (
ID key_aux
LESS <
ID v_key
RPAREN )
IF if
LPAREN (
ID current_node
DOT .
ID GetHas_Right
LPAREN (
RPAREN )
RPAREN )
ID current_node
EQ =
ID current_node
DOT .
ID GetRight
LPAREN (
RPAREN )
SEMICOL ;
ELSE else
ID cont
EQ =
ID false
SEMICOL ;
ELSE else
LPARBR {
ID ifound
EQ =
NUMBER 1
SEMICOL ;
ID cont
EQ =
ID false
SEMICOL ;
RPARBR }
RPARBR }
RETURN return
ID ifound
SEMICOL ;
RPARBR }
PUBLIC public
ID boolean
ID Print
LPAREN (
RPAREN )
LPARBR {
ID Tree
ID current_node
SEMICOL ;
ID boolean
ID ntb
SEMICOL ;
ID current_node
EQ =
THIS this
SEMICOL ;
ID ntb
EQ =
THIS this
DOT .
ID RecPrint
LPAREN (
ID current_node
RPAREN )
SEMICOL ;
RETURN return
ID true
SEMICOL ;
RPARBR }
PUBLIC public
ID boolean
ID RecPrint
LPAREN (
ID Tree
ID node
RPAREN )
LPARBR {
ID boolean
ID ntb
SEMICOL ;
IF if
LPAREN (
ID node
DOT .
ID GetHas_Left
LPAREN (
RPAREN )
RPAREN )
LPARBR {
ID ntb
EQ =
THIS this
DOT .
ID RecPrint
LPAREN (
ID node
DOT .
ID GetLeft
LPAREN (
RPAREN )
RPAREN )
SEMICOL ;
RPARBR }
ELSE else
ID ntb
EQ =
ID true
SEMICOL ;
ID System
DOT .
ID out
DOT .
ID println
LPAREN (
ID node
DOT .
ID GetKey
LPAREN (
RPAREN )
RPAREN )
SEMICOL ;
IF if
LPAREN (
ID node
DOT .
ID GetHas_Right
LPAREN (
RPAREN )
RPAREN )
LPARBR {
ID ntb
EQ =
THIS this
DOT .
ID RecPrint
LPAREN (
ID node
DOT .
ID GetRight
LPAREN (
RPAREN )
RPAREN )
SEMICOL ;
RPARBR }
ELSE else
ID ntb
EQ =
ID true
SEMICOL ;
RETURN return
ID true
SEMICOL ;
RPARBR }
RPARBR }
