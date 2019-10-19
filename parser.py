import ply.yacc as yacc

from lexer import MiniJavaLexer

class Node:
    children = []
    name = ""
    content = ""

    def __init__(self, name, children):
        self.name = name
        self.children = children

    def __str__(self):
        return str(self.name)

class Value(Node):
    value = None

    def __init__(self, value):
        self.value = value
        super().__init__(str(value), [])

    def __str__(self):
        return str(self.value)

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

class Mainclass(Node):
    statement = None

    def __init__(self, statement):
        self.statement = statement
        super().__init__("Main", [self.statement])


class Methoddecl(Node):
    modifyer = None
    methodtype = None
    name = None
    argseq = None
    vardecl = None
    statement = None
    retexpr = None
    
    def __init__(self, modifyer, name, argseq, vardecl, statement, retexpr):
        self.modifyer = modifyer
        self.name = name
        self.argseq = argseq
        self.vardecl = vardecl
        self.statement = statement
        self.retexpr = retexpr
        super().__init__(self.name, [self.argseq, \
                                     self.vardecl, \
                                     self.statement, \
                                     self.retexpr])


class Vardecl(Node):
    nextvardecl = None
    vartype = None
    varid = None

    def __init__(self, nextvardecl, vartype, id):
        self.nextvardecl = nextvardecl
        self.vartype = vartype
        self.varid = id
        children = []
        if self.vartype is not None:
            children.append(self.vartype)
        if self.nextvardecl is not None:
            children.append(self.nextvardecl)
        super().__init__(self.varid, children)

class Type(Node):
    typescheme = None

    def __init__(self, typescheme):
        self.typescheme = typescheme
        super().__init__(self.typescheme, [])

class Argseq(Node):
    nextArgseq = None
    curType = None
    curId = None

    def __init__(self, argseq, curType, curId):
        self.curId = curId
        self.curType = curType
        self.nextArgseq = argseq
        children = []
        if self.curType is not None:
            children.append(self.curType)
        if self.nextArgseq is not None:
            children.append(self.nextArgseq)
        super().__init__(self.curId, children)

class Statement(Node):
    def __init__(self):
        super().__init__("statement", [])


class MiniJavaParser:
    tokens = MiniJavaLexer.tokens
    
    def p_goal(self, p):
        '''goal : mainclass classdecl'''
        p[0] = Goal(p[1], p[2])

    def p_mainclass(self, p):
        '''mainclass : CLASS MAIN LPARBR PUBLIC STATIC VOID MAIN LPAREN ID LPARSQ RPARSQ ID RPAREN LPARBR statement RPARBR RPARBR'''
        p[0] = Mainclass(p[15])

    def p_classdecl(self, p):
        '''classdecl : CLASS ID LPARBR vardecl methoddecl RPARBR 
                     | CLASS ID EXTENDS ID LPARBR vardecl methoddecl RPARBR'''
        if len(p) == 7:
            p[0] = Classdecl(p[2], p[4], p[5])

    def p_vardecl(self, p):
        '''vardecl : vardecl type ID SEMICOL
                   | type ID SEMICOL
                   | empty'''
        if len(p) == 5:
            p[0] = Vardecl(p[1], p[3], p[4])
        if len(p) == 4:
            p[0] = Vardecl(None, p[1], p[2])
        if len(p) == 2:
            p[0] = Vardecl(None, None, None)    

    def p_methoddecl(self, p):
        '''methoddecl : PUBLIC type ID LPAREN argseq RPAREN LPARBR vardecl statement RETURN expression SEMICOL RPARBR
                      | PRIVATE type ID LPAREN argseq RPAREN LPARBR vardecl statement RETURN expression SEMICOL RPARBR'''
        p[0] = Methoddecl(p[2], p[3], p[5], p[8], p[9], p[11])

    def p_type(self, p):
        '''type : INT LPARSQ RPARSQ
                | INT
                | BOOL
                | ID'''
        p[0] = Type("int")

    def p_argseq(self, p):
        '''argseq : type ID
                  | argseq COMMA type ID
                  | empty'''
        if len(p) == 5:
            p[0] = Argseq(p[1], p[3], p[4])
        if len(p) == 3:
            p[0] = Argseq(None, p[1], p[2])
        if len(p) == 2:
            p[0] = Argseq(None, None, None)

    def p_statement(self, p):
        '''statement : LPARBR statement RPARBR
                     | IF LPAREN expression RPARBR statement ELSE statement
                     | WHILE LPAREN expression RPARBR statement
                     | expression SEMICOL
                     | ID ASSIGN expression SEMICOL
                     | ID LPARBR expression RPARBR ASSIGN SEMICOL
                     | empty'''
        p[0] = Statement()

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
        p[0] = Value(p[1])
    
    def p_factor_expr(self, p):
        'factor : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_empty(self, p):
        'empty :'
        p[0] = Node('empty', [])
    
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

