import ply.yacc as yacc

from lexer import MiniJavaLexer


class Node:
    children_names = []

    @property
    def children(self):
        result = []
        for name in self.children_names:
            attr = getattr(self, name)
            if attr is None:
                continue
            if isinstance(attr, list):
                result.extend(attr)
            else:
                result.append(attr)
        return result

    def __str__(self):
        return self.__class__.__name__


class BinOp(Node):
    children_names = ['left', 'right']

    def __init__(self, _op, lhs, rhs):
        self.left = lhs
        self.right = rhs
        self.op = _op

    def __str__(self):
        return str(self.op)


class UnOp(Node):
    children_names = ['child']

    def __init__(self, _op, child):
        self.child = child
        self.op = _op

    def __str__(self):
        return str(self.op)


class Goal(Node):
    children_names = ['main', 'user_class']

    def __init__(self, lhs, rhs):
        self.main = lhs
        self.user_class = rhs


class Classdecl(Node):
    children_names = ['parent', 'vardecl', 'methoddecl']

    def __init__(self, id, lhs, rhs, parent=None):
        self.vardecl = lhs
        self.methoddecl = rhs
        self.name = id
        self.parent = parent

    def __str__(self):
        return str(self.name)


class Mainclass(Node):
    children_names = ['statement']

    def __init__(self, statement):
        self.statement = statement



class Methoddecl(Node):

    children_names = ['argseq', 'vardecl', 'statement', 'retexpr']

    def __init__(self, is_public, modifier, name, argseq, vardecl, statement, retexpr):
        self.is_public = is_public
        self.modifier = modifier
        self.name = name
        self.argseq = argseq
        self.vardecl = vardecl
        self.statement = statement
        self.retexpr = retexpr

    def __str__(self):
        return str(self.name)


class Vardecl(Node):

    children_names = ['vartype']
    vartype = None
    varid = None

    def __init__(self, vartype, id):
        self.vartype = vartype
        self.varid = id

    def __str__(self):
        return str(self.varid)


class Type(Node):

    def __init__(self, typescheme):
        self.typescheme = typescheme

    def __str__(self):
        return str(self.typescheme)


class Arg(Node):
    children_names = ['cur_type']

    def __init__(self, cur_type, cur_id):
        self.cur_id = cur_id
        self.cur_type = cur_type

    def __str__(self):
        return self.cur_id


class Statement(Node):
    pass


class Literal(Node):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class BoolLiteral(Literal):
    pass


class IntLiteral(Literal):
    pass


class Identifier(Node):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)


class NewExpression(Node):
    def __init__(self, type):
        self.type = type

    def __str__(self):
        return 'new ' + self.type


class NewArrayExpression(Node):
    children_names = ['size']

    def __init__(self, size):
        self.size = size

    def __str__(self):
        return 'new int[]'


class IndexExpression(Node):
    children_names = ['obj', 'idx']

    def __init__(self, obj, idx):
        self.obj = obj
        self.idx = idx


class LengthExpression(Node):
    children_names = ['obj']

    def __init__(self, obj):
        self.obj = obj


class CallExpression(Node):
    children_names = ['obj', 'args']

    def __init__(self, obj, method, args):
        self.obj = obj
        self.method = method
        self.args = args

    def __str__(self):
        return str(self.method)


class MiniJavaParser:
    tokens = MiniJavaLexer.tokens

    precedence = (
        ('left', 'AND', 'OR'),
        ('nonassoc', 'LESS'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'MOD'),
        ('right', 'NOT'),
    )
    
    def p_goal(self, p):
        '''goal : mainclass classdecls'''
        p[0] = Goal(p[1], p[2])

    def p_classdecls(self, p):
        '''classdecls : classdecl classdecls
                      | empty'''
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = []

    def p_mainclass(self, p):
        '''mainclass : CLASS ID LPARBR PUBLIC STATIC VOID ID LPAREN ID LPARSQ RPARSQ ID RPAREN LPARBR statement RPARBR RPARBR'''
        p[0] = Mainclass(p[15])

    def p_classdecl(self, p):
        '''classdecl : CLASS ID LPARBR vardecls methoddecls RPARBR
                     | CLASS ID EXTENDS ID LPARBR vardecls methoddecls RPARBR'''
        if len(p) == 7:
            p[0] = Classdecl(p[2], p[4], p[5])
        else:
            p[0] = Classdecl(p[2], p[6], p[7])

    def p_vardecls(self, p):
        '''vardecls : vardecls vardecl
                    | empty'''
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = []

    def p_vardecl(self, p):
        '''vardecl : type ID SEMICOL'''
        p[0] = Vardecl(p[1], p[2])

    def p_methoddecls(self, p):
        '''methoddecls : methoddecl methoddecls
                       | empty'''
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = []

    def p_access_mod(self, p):
        '''access_mod : PUBLIC
                      | PRIVATE'''
        p[0] = p[1]

    def p_methoddecl(self, p):
        '''methoddecl : access_mod type ID LPAREN argseq RPAREN LPARBR vardecls statements RETURN expression SEMICOL RPARBR'''
        p[0] = Methoddecl(p[1] == 'PUBLIC', p[2], p[3], p[5], p[8], p[9], p[11])

    def p_statements(self, p):
        '''statements : statement statements
                      | empty'''
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = []

    def p_type(self, p):
        '''type : INT LPARSQ RPARSQ
                | INT
                | BOOL
                | ID'''
        if len(p) == 4:
            p[0] = Type("int[]")
        else:
            p[0] = Type(p[1])

    def p_argseq(self, p):
        '''argseq : args
                  | empty'''
        if p[1] is None:
            p[0] = []
        else:
            p[0] = p[1]

    def p_args(self, p):
        '''args : type ID
                | type ID COMMA args'''
        if len(p) == 5:
            p[0] = [Arg(p[1], p[2])] + p[4]
        else:
            p[0] = [Arg(p[1], p[2])]

    def p_paramseq(self, p):
        '''paramseq : params
                    | empty'''
        if p[1] is None:
            p[0] = []
        else:
            p[0] = p[1]

    def p_params(self, p):
        '''params : expression
                  | expression COMMA params'''
        if len(p) == 4:
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1]]


    def p_statement(self, p):
        '''statement : LPARBR statements RPARBR
                     | IF LPAREN expression RPAREN statement ELSE statement
                     | WHILE LPAREN expression RPAREN statement
                     | ID DOT ID DOT ID LPAREN expression RPAREN SEMICOL
                     | ID ASSIGN expression SEMICOL
                     | ID LPARSQ expression RPARSQ ASSIGN expression SEMICOL '''
        p[0] = Statement()

    def p_expression(self, p):
        '''expression : expression PLUS expression
                      | expression MINUS expression
                      | expression TIMES expression
                      | expression MOD expression
                      | expression AND expression
                      | expression OR expression
                      | expression LESS expression
                      | NOT expression
                      | term'''
        if len(p) == 4:
            p[0] = BinOp(p[2], p[1], p[3])
        elif len(p) == 3:
            p[0] = UnOp(p[1], p[2])
        else:
            p[0] = p[1]

    def p_term(self, p):
        '''term : term DOT ID
                | term DOT ID LPAREN paramseq RPAREN'''
        if len(p) == 4:
            if p[3] != 'length':
                assert False  # TODO
            p[0] = LengthExpression(p[1])
        else:
            p[0] = CallExpression(p[1], p[3], p[5])

    def p_term_index(self, p):
        '''term : term LPARSQ expression RPARSQ'''
        p[0] = IndexExpression(p[1], p[3])

    def p_term_new_array(self, p):
        '''term : NEW INT LPARSQ expression RPARSQ'''
        p[0] = NewArrayExpression(p[4])

    def p_term_new(self, p):
        '''term :  NEW ID LPAREN RPAREN'''
        p[0] = NewExpression(p[2])

    def p_term_paren(self, p):
        '''term : LPAREN expression RPAREN'''
        p[0] = p[2]

    def p_term_true(self, p):
        '''term : TRUE'''
        p[0] = BoolLiteral(True)

    def p_term_false(self, p):
        '''term : FALSE'''
        p[0] = BoolLiteral(False)

    def p_term_number(self, p):
        '''term : NUMBER'''
        p[0] = IntLiteral(int(p[1]))

    def p_term_id(self, p):
        '''term : ID'''
        p[0] = Identifier(p[1])

    def p_empty(self, p):
        'empty :'
        p[0] = None
    
    # Error rule for syntax errors
    def p_error(self, p):
        print(p)
        print("Syntax error in input!")

    ##################
    # public methods
    ##################
    
    # Build the lexer
    def build(self,**kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)

    def get_AST(self, text, lexer, debug=False):
        return self.parser.parse(text, lexer=lexer, debug=debug)

