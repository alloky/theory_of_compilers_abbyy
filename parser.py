import ply.yacc as yacc

from lexer import MiniJavaLexer

class Node:
    left = None
    right = None
    op = None
    value = None

    def __init__(self, _op, lhs, rhs):
        self.left = lhs
        self.right = rhs
        self.op = _op


class MiniJavaParser:
    tokens = MiniJavaLexer.tokens
    
    def p_expression_plus(self, p):
        'expression : expression PLUS term'
        p[0] = Node('PLUS', p[1], p[3])
 
    def p_expression_minus(self, p):
        'expression : expression MINUS term'
        p[0] = Node('MINUS', p[1], p[3])
 
    def p_expression_term(self, p):
        'expression : term'
        p[0] = p[1]
    
    def p_term_times(self, p):
        'term : term TIMES factor'
        p[0] = Node('TIMES', p[1], p[3])
    
    def p_term_div(self, p):
        'term : term DIVIDE factor'
        p[0] = Node('DIVIDE', p[1], p[3])
    
    def p_term_factor(self, p):
        'term : factor'
        p[0] = p[1]
    
    def p_factor_num(self, p):
        'factor : NUMBER'
        p[0] = Node('NUMBER', None, None)
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

