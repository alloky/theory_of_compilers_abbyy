import ast
from collections import OrderedDict

from visitor import BaseVisitor


class ClassSymbolTable:

    def __init__(self, parent):
        self.parent = parent
        self.fields = {}
        self.methods = {}


class MethodSymbolTable:

    def __init__(self, is_public, return_type):
        self.is_public = is_public
        self.return_type = return_type
        self.params = OrderedDict()
        self.vars = {}


class SymbolTableBuilderVisitor(BaseVisitor):

    def __init__(self):
        self.table = {}

    def visit_goal(self, node, *args):
        self.visit(node.main)
        for n in node.classes:
            self.visit(n)

    def visit_main_class(self, node, *args):
        self.table[node.name] = ClassSymbolTable(None)

    def visit_class_declaration(self, node, *args):
        assert node.name not in self.table
        self.table[node.name] = class_table = ClassSymbolTable(node.parent)
        for var in node.vardecl:
            self.visit(var, class_table.fields)
        for method in node.methoddecl:
            self.visit(method, class_table.methods)

    def visit_var_declaration(self, node, table, *args):
        assert node.varid != 'this' and node.varid not in table
        table[node.varid] = node.vartype

    def visit_method_declaration(self, node, table, *args):
        assert node.name not in table
        table[node.name] = method_table = MethodSymbolTable(node.is_public, node.return_type)
        for param in node.argseq:
            self.visit(param, method_table.params)
        for var in node.vardecl:
            self.visit(var, method_table.vars)
        assert not set(method_table.params).intersection(method_table.vars)

    def visit_method_parameter(self, node, table, *args):
        assert node.cur_id != 'this' and node.cur_id not in table
        table[node.cur_id] = node.cur_type


def check_inheritance_loops(table):
    visited = set()
    finalized = set()

    def dfs(c):
        if c in visited and c not in finalized:
            assert False
        visited.add(c)
        if table[c].parent:
            dfs(table[c].parent)
        finalized.add(c)

    for c in table:
        if table[c].parent:
            assert table[c].parent in table
        if c in finalized:
            continue
        dfs(c)


def check_overridden_signatures(table):
    for c in table:
        if table[c].parent is None:
            continue
        for field in table[c].fields:
            cur = table[c].parent
            while cur is not None:
                if field in table[cur].fields:
                    assert False
                cur = table[cur].parent
        for method in table[c].methods:
            method_params = list(table[c].methods[method].params.items())
            method_ret = table[c].methods[method].return_type
            cur = table[c].parent
            while cur is not None:
                if method in table[cur].methods:
                    assert method_params == list(table[cur].methods[method].params.items())
                    assert method_ret == table[cur].methods[method].return_type
                cur = table[cur].parent


def build_symbol_table(node: ast.Goal):
    visitor = SymbolTableBuilderVisitor()
    visitor.visit(node)
    check_inheritance_loops(visitor.table)
    check_overridden_signatures(visitor.table)
    return visitor.table
