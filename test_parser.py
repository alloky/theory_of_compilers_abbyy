#!/usr/bin/env python3
import json

from parser import MiniJavaParser
from lexer import MiniJavaLexer
from dotlib import Graph, to_dot
from symbols import build_symbol_table
from utils import read_file
import subprocess
import sys

from visitor import BaseVisitor


class BuildGraphVisitor(BaseVisitor):

    def __init__(self):
        self.graph = Graph()

    def visit_goal(self, node, *args):
        v = self.graph.nodes.add('Program')
        v.add_edge_to(self.visit(node.main))
        for n in node.classes:
            v.add_edge_to(self.visit(n))
        return v

    def visit_main_class(self, node, *args):
        v = self.graph.nodes.add('main')
        v.add_edge_to(self.visit(node.statement))
        return v

    def visit_class_declaration(self, node, *args):
        v = self.graph.nodes.add('class ' + node.name + (': ' + node.parent if node.parent else ''))
        for var in node.vardecl:
            v.add_edge_to(self.visit(var))
        for method in node.methoddecl:
            v.add_edge_to(self.visit(method))
        return v

    def visit_method_declaration(self, node, *args):
        v = self.graph.nodes.add(('public ' if node.is_public else 'private ') +
                                 node.return_type + ' ' + node.name + '()')
        for arg in node.argseq:
            v.add_edge_to(self.visit(arg), 'param')
        for var in node.vardecl:
            v.add_edge_to(self.visit(var))
        for stmt in node.statement:
            v.add_edge_to(self.visit(stmt))
        v.add_edge_to(self.visit(node.retexpr), 'return')
        return v

    def visit_method_parameter(self, node, *args):
        v = self.graph.nodes.add(node.cur_type + ' ' + node.cur_id)
        return v

    def visit_var_declaration(self, node, *args):
        v = self.graph.nodes.add(node.vartype + ' ' + node.varid)
        return v

    def visit_bool_literal(self, node, *args):
        v = self.graph.nodes.add(str(node.value))
        return v

    def visit_int_literal(self, node, *args):
        v = self.graph.nodes.add(str(node.value))
        return v

    def visit_identifier(self, node, *args):
        v = self.graph.nodes.add(node.name)
        return v

    def visit_bin_op(self, node, *args):
        v = self.graph.nodes.add(node.op)
        v.add_edge_to(self.visit(node.left))
        v.add_edge_to(self.visit(node.right))
        return v

    def visit_un_op(self, node, *args):
        v = self.graph.nodes.add(node.op)
        v.add_edge_to(self.visit(node.child))
        return v

    def visit_new_expression(self, node, *args):
        v = self.graph.nodes.add('new ' + node.type + '()')
        return v

    def visit_new_array_expression(self, node, *args):
        v = self.graph.nodes.add('new int[]')
        v.add_edge_to(self.visit(node.size))
        return v

    def visit_index_expression(self, node, *args):
        v = self.graph.nodes.add('[]')
        v.add_edge_to(self.visit(node.obj))
        v.add_edge_to(self.visit(node.idx), 'index')
        return v

    def visit_length_expression(self, node, *args):
        v = self.graph.nodes.add('.length')
        v.add_edge_to(self.visit(node.obj))
        return v

    def visit_call_expression(self, node, *args):
        v = self.graph.nodes.add('.' + node.method + '()')
        v.add_edge_to(self.visit(node.obj))
        for arg in node.args:
            v.add_edge_to(self.visit(arg), 'arg')
        return v

    def visit_assign_statement(self, node, *args):
        v = self.graph.nodes.add(node.obj + ' =')
        v.add_edge_to(self.visit(node.value))
        return v

    def visit_array_assign_statement(self, node, *args):
        v = self.graph.nodes.add(node.obj + '[] =')
        v.add_edge_to(self.visit(node.index), 'index')
        v.add_edge_to(self.visit(node.value))
        return v

    def visit_print_statement(self, node, *args):
        v = self.graph.nodes.add('System.out.println()')
        v.add_edge_to(self.visit(node.value))
        return v

    def visit_if_statement(self, node, *args):
        v = self.graph.nodes.add('if')
        v.add_edge_to(self.visit(node.condition), 'cond')
        for stmt in node.stmt_then:
            v.add_edge_to(self.visit(stmt), 'then')
        for stmt in node.stmt_else:
            v.add_edge_to(self.visit(stmt), 'else')
        return v

    def visit_while_statement(self, node, *args):
        v = self.graph.nodes.add('while')
        v.add_edge_to(self.visit(node.condition), 'cond')
        for stmt in node.stmt:
            v.add_edge_to(self.visit(stmt))
        return v



def ast_to_graph(ast_root):
    visitor = BuildGraphVisitor()
    visitor.visit(ast_root)
    return visitor.graph


def tree_to_svg(tree, filename):
    with open(filename + ".dot", "w+") as f:
        f.write(to_dot(ast_to_graph(tree)))
    subprocess.run([
        "dot", 
        "-Tsvg", 
        filename + ".dot",
        "-o",
        filename + ".svg" 
    ])


mjl = MiniJavaLexer()
mjl.build()
mpj = MiniJavaParser()
mpj.build()

if len(sys.argv) > 1:
    code = read_file(sys.argv[1])
else:
    code = """

class main {

    public static void main(String[] args) {
        System.out.println(2 + (2 * 2));
    }

}

class User {

    int somefield;

    public int getRand(int x, bool y) {
        bool b;
        b = y || true;
        return 2 < 3 + ! 4;
    }
    

}

    """

prog_ast = mpj.get_AST(code, lexer=mjl.lexer, debug=False)

tree_to_svg(prog_ast, "test_prog") 


symbol_table = build_symbol_table(prog_ast)
print('\n\nSYMBOL TABLE:')
print(json.dumps(symbol_table, indent=2))
