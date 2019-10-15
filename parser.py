import ply.yacc as yacc

from lexer import MiniJavaLexer

class Node:
    children = []
    name = ""
    content = ""

    def __init__(self, name, children):
        self.name = name
        self.children = children


class BinOp(Node):
    left = None
    right = None
    op = None
    value = None

    def __init__(self, _op, lhs, rhs):
        self.left = lhs
        self.right = rhs
        self.op = _op
        super().__init__(_op, [self.left, self.right])

class Goal(Node):
    main = None
    userClass = None

    def __init__(self, lhs, rhs):
        self.main = lhs
        self.userClass = rhs
        super().__init__("Goal", [self.main, self.userClass])

class Classdecl(Node):
    vardecl = None
    methoddecl = None
    name = ""

    def __init__(self, id, lhs, rhs):
        self.vardecl = lhs
        self.methoddecl = rhs
        self.name = id
        super().__init__(self.name, [self.vardecl, self.methoddecl])

class Vardecl(Node):
    nextvardecl = None
    vartype = None
    varid = none

    def __init__(self, id, lhs, rhs):
        self.nextvardecl = rhs
        self.vartype = lhs
        self.varid = id
        super().__init__(self.varid, [self.vartype, self.nextvardecl])

class Type(Node):
    typescheme = None

    def __init__(self, typescheme):
        self.typescheme = typescheme
        super().__init__(self.typescheme, [])


class MiniJavaParser:
    tokens = MiniJavaLexer.tokens
    
    def p_goal(self, p):
        '''goal : mainclass LPAREN classdecl RPAREN'''

    def p_mainclass(self, p):
        '''mainclass : CLASS ID LPARBR PUBLIC STATIC VOID MAIN LPAREN ID LPARSQ RPARSQ ID RPAREN LPARBR statement RPARBR'''

    def p_classdecl(self, p):
        '''classdecl : CLASS ID LPARBR vardecl methoddecl RPARBR 
                     | CLASS ID EXTENDS ID LPARBR vardecl methoddecl RPARBR'''
           
    def p_vardecl(self, p):
        '''vardecl : vardecl SEMICOL type ID
                   | type ID'''

    def p_methoddecl(self, p):
        '''methoddecl : PUBLIC type ID LPAREN argseq RPAREN LPARBR vardecl statement RETURN expression RPARBR
                      | PRIVATE type ID LPAREN argseq RPAREN LPARBR vardecl statement RETURN expression RPARBR'''
    
    def p_type(self, p):
        '''type : INT LPARSQ RPARSQ
                | INT
                | BOOL
                | ID'''
    
    def p_argseq(self, p):
        '''argseq : type ID
                  | argseq COMMA type ID'''

    def p_statement(self, p):
        '''statement : LPARBR statement RPARBR
                     | IF LPAREN expression RPARBR statement ELSE statement
                     | WHILE LPAREN expression RPARBR statement
                     | expression SEMICOL
                     | ID ASSIGN expression SEMICOL
                     | ID LPARBR expression RPARBR ASSIGN SEMICOL'''


    def p_expression_plus_minus(self, p):
        '''expression : expression PLUS term 
                      | expression MINUS term'''
        p[0] = BinOp(p[2], p[1], p[3])
 
    def p_expression_term(self, p):
        'expression : term'
        p[0] = p[1]
    
    def p_term_times_div(self, p):
        '''term : term TIMES factor
                 | term DIVIDE factor'''
        p[0] = BinOp(p[2], p[1], p[3])

    def p_term_factor(self, p):
        'term : factor'
        p[0] = p[1]
    
    def p_factor_num(self, p):
        'factor : NUMBER'
        p[0] = BinOp(p[1], None, None)
        p[0].value = p[1]
    
    def p_factor_expr(self, p):
        'factor : LPAREN expression RPAREN'
        p[0] = p[2]
    
    # Error rule for syntax errors
    def p_error(self, p):
        print("Syntax error in input!")

    ##################
    # public methods
    ##################
    
    # Build the lexer
    def build(self,**kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)

    def get_AST(self, text, lexer):
        return self.parser.parse(text, lexer=lexer)

