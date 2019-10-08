import ply.lex as lex
 
class MiniJavaLexer(object):
    # List of token names.   This is always required
    reserved = {
        'if' : 'IF',
        'else' : 'ELSE',
        'while' : 'WHILE',
        
        'class' : 'CLASS',
        'this'  : 'THIS',
        'public' : 'PUBLIC',
        'private' : 'PRIVATE',
        'protected' : 'PROTECTED',
        'static' : 'STATIC',
        
        'new' : 'NEW',
        'return' : 'RETURN',


        # types
        'void'     : 'VOID',
        'int'      : 'INT',
        'short'    : 'SHORT',
        'char'     : 'CHAR',
        'double'   : 'DOUBLE',
        'float'    : 'FLOAT',
        'bool'     : 'BOOL'
    }
   
    tokens = list((
       'NUMBER',
       'PLUS',
       'MINUS',
       'TIMES',
       'DIVIDE',
       # cmp
       'EQ',
       'LESS',
       'LESSEQ',
       'MORE',
       'MOREEQ',
       # pars
       'LPAREN',
       'RPAREN',
       'LPARBR',
       'RPARBR',
       'LPARSQ',
       'RPARSQ',

       'DOT',
       'LINESEP',
       'ID',
    )) + list(reserved.values())

    # Regular expression rules for simple tokens
    t_PLUS    = r'\+'
    t_MINUS   = r'-'
    t_TIMES   = r'\*'
    t_DIVIDE  = r'/'
    
    # cmp
    t_EQ      = r'\='
    t_MORE    = r'\>'
    t_MOREEQ  = r'\>\='
    t_LESS    = r'\<'
    t_LESSEQ  = r'\<\='
    
    # pars
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_LPARBR  = r'\{'
    t_RPARBR  = r'\}'
    t_LPARSQ  = r'\['
    t_RPARSQ  = r'\]'
    
    t_DOT     = r'\.'
    t_LINESEP = r'\;'

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value,'ID')    # Check for reserved words
        return t

    # A regular expression rule with some action code
    # Note addition of self parameter since we're in a class
    def t_NUMBER(self,t):
        r'\d+'
        t.value = int(t.value)    
        return t

    # Define a rule so we can track line numbers
    def t_newline(self,t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'
    t_ignore_ONE_LINE_COMMENT   = '\/\/.*\n'
    t_ignore_MULTI_LINE_COMMENT = '\/\*.*\*\/' 

    # Error handling rule
    def t_error(self,t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Build the lexer
    def build(self,**kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
    
    # Test it output
    def test(self,data):
        self.lexer.input(data)
        while True:
             tok = self.lexer.token()
             if not tok: 
                 break
             print(tok.type, tok.value)
    
    def get_tokens(self, data):
        self.lexer.input(data)
        tok_arr = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            tok_arr.append(tok)
        return tok_arr
        
 