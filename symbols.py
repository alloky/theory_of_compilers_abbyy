import mj_ast
from collections import OrderedDict

from compilation_error import CompilationError, ErrorType
from visitor import BaseVisitor


class ClassSymbolTable:

    def __init__(self, parent, lineno):
        self.parent = parent
        self.lineno = lineno
        self.fields = {}
        self.methods = {}


class MethodSymbolTable:

    def __init__(self, is_public, return_type, lineno):
        self.is_public = is_public
        self.return_type = return_type
        self.lineno = lineno
        self.params = OrderedDict()
        self.vars = {}
        self.is_virtual = False


class SymbolTableBuilderVisitor(BaseVisitor):

    def __init__(self):
        self.table = {}

    def visit_goal(self, node, *args):
        self.visit(node.main)
        for n in node.classes:
            self.visit(n)

    def visit_main_class(self, node, *args):
        self.table[node.name] = ClassSymbolTable(None, node.lineno)

    def visit_class_declaration(self, node, *args):
        if node.name in self.table:
            raise CompilationError(ErrorType.dublicatedClass, 'Duplicate class: ' + node.name, node.lineno)
        self.table[node.name] = class_table = ClassSymbolTable(node.parent, node.lineno)
        for var in node.vardecl:
            self.visit(var, class_table.fields)
        for method in node.methoddecl:
            self.visit(method, class_table.methods)

    def visit_var_declaration(self, node, table, check_table=None, *args):
        if node.varid == 'this':
            raise CompilationError(ErrorType.invalidVariableName, '"this" is not a valid variable name', node.lineno)
        if node.varid in table or (check_table and node.varid in check_table):
            raise CompilationError(ErrorType.dublicatedVariable, 'Duplicate variable name: ' + node.varid, node.lineno)
        table[node.varid] = node.vartype

    def visit_method_declaration(self, node, table, *args):
        if node.name in table:
            raise CompilationError(ErrorType.dublicatedMethod, 'Duplicate method name: ' + node.name, node.lineno)
        table[node.name] = method_table = MethodSymbolTable(node.is_public, node.return_type, node.lineno)
        for param in node.argseq:
            self.visit(param, method_table.params)
        for var in node.vardecl:
            self.visit(var, method_table.vars, method_table.params)

    def visit_method_parameter(self, node, table, *args):
        if node.cur_id == 'this':
            raise CompilationError(ErrorType.invalidName, '"this" is not a valid parameter name', node.lineno)
        if node.cur_id in table:
            raise CompilationError(ErrorType.dublicatedParam, 'Duplicate parameter name: ' + node.cur_id, node.lineno)
        table[node.cur_id] = node.cur_type


def check_inheritance_loops(table):
    visited = set()
    finalized = set()

    def dfs(c):
        if c in visited and c not in finalized:
            raise CompilationError(ErrorType.cycleInheritance , 'Inheritance loop in class ' + c, table[c].lineno)
        visited.add(c)
        if table[c].parent:
            dfs(table[c].parent)
        finalized.add(c)

    for c in table:
        if table[c].parent:
            if table[c].parent not in table:
                raise CompilationError(ErrorType.classNotFound, 'No such class: ' + table[c].parent, table[c].lineno)
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
                    raise CompilationError(
                            ErrorType.variableOverloading, 
                            f'Field with name "{field}" already exists in the superclass',
                            table[c].lineno)
                cur = table[cur].parent
        for method in table[c].methods:
            method_params = list(table[c].methods[method].params.items())
            method_ret = table[c].methods[method].return_type
            method_is_public = table[c].methods[method].is_public
            cur = table[c].parent
            while cur is not None:
                if method in table[cur].methods:
                    if (method_params != list(table[cur].methods[method].params.items()) or
                            method_ret != table[cur].methods[method].return_type or
                            method_is_public != table[cur].methods[method].is_public):
                        raise CompilationError(ErrorType.methodInBaseWithDifferentSignature,
                                              f'Method with name "{method}" already exists in the superclass ',
                                               'with a different signature', table[c].methods[method].lineno)
                    table[cur].methods[method].is_virtual = True
                cur = table[cur].parent


def build_symbol_table(node: mj_ast.Goal):
    visitor = SymbolTableBuilderVisitor()
    visitor.visit(node)
    check_inheritance_loops(visitor.table)
    check_overridden_signatures(visitor.table)
    return visitor.table
