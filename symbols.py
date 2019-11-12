import ast
from collections import OrderedDict

from visitor import BaseVisitor


class SymbolTableBuilderVisitor(BaseVisitor):

    def __init__(self):
        self.table = {}

    def visit_goal(self, node, *args):
        for n in node.classes:
            self.visit(n)

    def visit_class_declaration(self, node, *args):
        assert node.name != 'Main' and node.name not in self.table
        self.table[node.name] = {'fields': {}, 'methods': {}}
        for var in node.vardecl:
            self.visit(var, self.table[node.name]['fields'])
        for method in node.methoddecl:
            self.visit(method, self.table[node.name]['methods'])

    def visit_var_declaration(self, node, table, *args):
        assert node.varid != 'this' and node.varid not in table
        table[node.varid] = node.vartype

    def visit_method_declaration(self, node, table, *args):
        assert node.name not in table
        table[node.name] = {'return': node.return_type, 'params': OrderedDict(), 'vars': {}}
        for param in node.argseq:
            self.visit(param, table[node.name]['params'])
        for var in node.vardecl:
            self.visit(var, table[node.name]['vars'])
        assert not set(table[node.name]['params']).intersection(set(table[node.name]['vars']))

    def visit_method_parameter(self, node, table, *args):
        assert node.cur_id != 'this' and node.cur_id not in table
        # TODO проверить, что нет такой локальной переменной
        table[node.cur_id] = node.cur_type


def build_symbol_table(node: ast.Goal):
    visitor = SymbolTableBuilderVisitor()
    visitor.visit(node)
    return visitor.table
