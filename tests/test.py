#!/usr/bin/env python3

import unittest
import os
import sys
import inspect

currentdir = os.path.dirname(
    os.path.abspath(
        inspect.getfile(
            inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import utils
from lexer import MiniJavaLexer

class TestLexer(unittest.TestCase):
    def test_file(self):
        code_file_path = 'tests/codeExamples/miniJavaExmpl.java'
        lex_file_path = 'tests/lexes/miniJavaExmpl.lex'

        mjLexer = MiniJavaLexer()
        mjLexer.build()

        code = utils.read_file(code_file_path)

        if len(code) == 0:
            print("Example file is empty or error while read")
            self.assertFalse(True)
            return

        lex = utils.read_file(lex_file_path)

        if len(lex) == 0:
            print("Lexical file is empty or error while read")
            self.assertFalse(True)
            return

        tokens = mjLexer.get_tokens(code)

        true_tok_arr = [x.strip() for x in lex.split('\n') if len(x) > 0]
        lexed_tok_arr = ["{} {}".format(tok.type, tok.value) for tok in tokens]

        # print(true_tok_arr)
        # print("----------------")
        # print(lexed_tok_arr)
        self.assertCountEqual(true_tok_arr, lexed_tok_arr)


if __name__ == '__main__':
    unittest.main()
