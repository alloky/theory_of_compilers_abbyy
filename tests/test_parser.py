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

from parser import MiniJavaParser
from lexer import MiniJavaLexer
from symbols import build_symbol_table

class TestParser(unittest.TestCase):
    def test_good_examples(self):
        mjl = MiniJavaLexer()
        mjl.build()
        mpj = MiniJavaParser()
        mpj.build()

        exmpls_path = "tests/codeExamples"

        good_files = os.listdir(exmpls_path)

        for idx, file in enumerate(good_files):
            print("{} out of {} Parsing {} ...".format(idx + 1,len(good_files), file), end=" ")
            
            file_path = os.path.join(exmpls_path, file) 
            code = utils.read_file(file_path)
            
            prog_ast = mpj.get_AST(code, lexer=mjl.lexer, debug=False)
            symbol_table = build_symbol_table(prog_ast)

            print("[done]")

        print("Success.")


if __name__ == '__main__':
    unittest.main()

            
