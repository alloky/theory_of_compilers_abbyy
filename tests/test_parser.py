#!/usr/bin/env python3

import unittest
import os
import sys
import inspect

# currentdir = os.path.dirname(
#     os.path.abspath(
#         inspect.getfile(
#             inspect.currentframe())))
# parentdir = os.path.dirname(currentdir)
# sys.path.insert(0, parentdir)

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)


import utils

from mjparser import MiniJavaParser
from lexer import MiniJavaLexer
from symbols import build_symbol_table
from typecheck import typecheck
from compilation_error import ErrorType, CompilationError

class TestParser(unittest.TestCase):
    def test_good_examples(self):
        mjl = MiniJavaLexer()
        mjl.build()
        mpj = MiniJavaParser()
        mpj.build()

        exmpls_path = "../tests/codeExamples"

        good_files = os.listdir(exmpls_path)

        for idx, file in enumerate(good_files):
            print("{} out of {} Parsing {} ...".format(idx + 1,len(good_files), file), end=" ")
            
            file_path = os.path.join(exmpls_path, file) 
            code = utils.read_file(file_path)
            
            prog_ast = mpj.get_AST(code, lexer=mjl.lexer, debug=False)
            symbol_table = build_symbol_table(prog_ast)
            typecheck(prog_ast, symbol_table)

            print("[done]")

        print("Success.")

    def test_bad_examples(self):
        mjl = MiniJavaLexer()
        mjl.build()
        mpj = MiniJavaParser()
        mpj.build()

        exmpls_path = "../tests/BadSamples"

        def find_error_type_in_file(code, lineno):
            lines = code.split('\n')
            if lineno is None:
                return 'endOfFile'
            if lineno > len(lines):
                print("Wrong lineno : got ", lineno, end =" ")
                return None
            line = lines[lineno]
            if "HERE" not in line:
                print("!!! No error specifyed !!!", end=" ")
                return None
            return line[line.index("HERE") + 5:].strip()


        good_files = sorted(os.listdir(exmpls_path))

        for idx, file in enumerate(good_files):
            print("{} out of {} Parsing {} ...".format(idx + 1,len(good_files), file), end=" ")
            
            file_path = os.path.join(exmpls_path, file) 
            code = utils.read_file(file_path)
            
            try:
                prog_ast = mpj.get_AST(code, lexer=mjl.lexer, debug=False)
                symbol_table = build_symbol_table(prog_ast)
                typecheck(prog_ast, symbol_table)
                print("!!! No error, but should be !!!", end=" ")
            except CompilationError as e:
                error_type = find_error_type_in_file(code, e.lineno)
                if error_type is not None and (len(error_type) == 0):
                    print("!!! No error, but should be !!!", end=" ")
                if error_type:
                    self.assertEqual(getattr(ErrorType, error_type), e.error_type)

            print("[done]")

        print("Success.")




if __name__ == '__main__':
    unittest.main()

            
