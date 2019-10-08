from lexer import MiniJavaLexer
from utils import read_file
import sys

lexer = MiniJavaLexer()
lexer.build()
data = read_file(sys.argv[1])
lexer.test(data)
