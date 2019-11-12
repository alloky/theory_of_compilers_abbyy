import ply.yacc as yacc

from lexer import MiniJavaLexer
import ast


def to_list(obj):
    if isinstance(obj, ast.Node):
        return [obj]
    return obj


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
        p[0] = ast.Goal(p[1], p[2])

    def p_classdecls(self, p):
        '''classdecls : classdecl classdecls
                      | empty'''
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = []

    def p_mainclass(self, p):
        '''mainclass : CLASS ID LPARBR PUBLIC STATIC VOID ID LPAREN ID LPARSQ RPARSQ ID RPAREN LPARBR statement RPARBR RPARBR'''
        p[0] = ast.MainClass(p[15])

    def p_classdecl(self, p):
        '''classdecl : CLASS ID LPARBR vardecls methoddecls RPARBR
                     | CLASS ID EXTENDS ID LPARBR vardecls methoddecls RPARBR'''
        if len(p) == 7:
            p[0] = ast.ClassDeclaration(p[2], p[4], p[5])
        else:
            p[0] = ast.ClassDeclaration(p[2], p[6], p[7], p[4])

    def p_vardecls(self, p):
        '''vardecls : vardecls vardecl
                    | empty'''
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = []

    def p_vardecl(self, p):
        '''vardecl : type ID SEMICOL'''
        p[0] = ast.VarDeclaration(p[1], p[2])

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
        p[0] = ast.MethodDeclaration(p[1] == 'PUBLIC', p[2], p[3], p[5], p[8], p[9], p[11])

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
            p[0] = ast.Type("int[]")
        else:
            p[0] = ast.Type(p[1])

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
            p[0] = [ast.MethodParameter(p[1], p[2])] + p[4]
        else:
            p[0] = [ast.MethodParameter(p[1], p[2])]

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


    def p_statement_compound(self, p):
        '''statement : LPARBR statements RPARBR'''
        p[0] = p[2]

    def p_statement_if(self, p):
        '''statement : IF LPAREN expression RPAREN statement ELSE statement'''
        p[0] = ast.IfStatement(p[3], to_list(p[5]), to_list(p[7]))

    def p_statement_while(self, p):
        '''statement : WHILE LPAREN expression RPAREN statement'''
        p[0] = ast.WhileStatement(p[3], to_list(p[5]))

    def p_statement_print(self, p):
        '''statement : ID DOT ID DOT ID LPAREN expression RPAREN SEMICOL'''
        if p[1] != 'System' or p[3] != 'out' or p[5] != 'println':
            assert False  # TODO
        p[0] = ast.PrintStatement(p[7])

    def p_statement_assign(self, p):
        '''statement : ID ASSIGN expression SEMICOL'''
        p[0] = ast.AssignStatement(p[1], p[3])

    def p_statement_array_assign(self, p):
        '''statement : ID LPARSQ expression RPARSQ ASSIGN expression SEMICOL'''
        p[0] = ast.ArrayAssignStatement(p[1], p[3], p[6])


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
            p[0] = ast.BinOp(p[2], p[1], p[3])
        elif len(p) == 3:
            p[0] = ast.UnOp(p[1], p[2])
        else:
            p[0] = p[1]

    def p_term(self, p):
        '''term : term DOT ID
                | term DOT ID LPAREN paramseq RPAREN'''
        if len(p) == 4:
            if p[3] != 'length':
                assert False  # TODO
            p[0] = ast.LengthExpression(p[1])
        else:
            p[0] = ast.CallExpression(p[1], p[3], p[5])

    def p_term_index(self, p):
        '''term : term LPARSQ expression RPARSQ'''
        p[0] = ast.IndexExpression(p[1], p[3])

    def p_term_new_array(self, p):
        '''term : NEW INT LPARSQ expression RPARSQ'''
        p[0] = ast.NewArrayExpression(p[4])

    def p_term_new(self, p):
        '''term :  NEW ID LPAREN RPAREN'''
        p[0] = ast.NewExpression(p[2])

    def p_term_paren(self, p):
        '''term : LPAREN expression RPAREN'''
        p[0] = p[2]

    def p_term_true(self, p):
        '''term : TRUE'''
        p[0] = ast.BoolLiteral(True)

    def p_term_false(self, p):
        '''term : FALSE'''
        p[0] = ast.BoolLiteral(False)

    def p_term_number(self, p):
        '''term : NUMBER'''
        p[0] = ast.IntLiteral(int(p[1]))

    def p_term_id(self, p):
        '''term : ID'''
        p[0] = ast.Identifier(p[1])

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
    def build(self, **kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)

    def get_AST(self, text, lexer, debug=False):
        return self.parser.parse(text, lexer=lexer, debug=debug)

