from compilation_error import CompilationError, ErrorType
from visitor import BaseVisitor


class TypeInferenceVisitor(BaseVisitor):

    ATOMS = ['int', 'int[]', 'boolean']

    def __init__(self, symbol_table):
        self.table = symbol_table
        self.class_name = None
        self.method_name = None

    def assert_type_exists(self, node_type, lineno):
        if node_type not in self.ATOMS and node_type not in self.table:
            raise CompilationError(ErrorType.nonexistentType, f'Type "{node_type}" does not exist', lineno)

    def assert_is_subclass(self, node_type, expected_type, lineno):
        if expected_type in self.ATOMS or node_type in self.ATOMS:
            if node_type != expected_type:
                raise CompilationError(ErrorType.wrongType, f'Expected type "{expected_type}", got "{node_type}"', lineno)
        t = node_type
        while True:
            if t == expected_type:
                return
            t = self.table[t].parent
            if t is None:
                raise CompilationError(ErrorType.wrongType, f'Expected type "{expected_type}", got "{node_type}"', lineno)

    def resolve_id(self, name, lineno):
        if not self.class_name or not self.method_name:
            raise CompilationError(ErrorType.undefinedVar, 'Undefined variable: ' + name, lineno)
        if name == 'this':
            return self.class_name
        class_table = self.table[self.class_name]
        if name in class_table.methods[self.method_name].vars:
            return class_table.methods[self.method_name].vars[name]
        if name in class_table.methods[self.method_name].params:
            return class_table.methods[self.method_name].params[name]
        while True:
            if name in class_table.fields:
                return class_table.fields[name]
            class_table = self.table.get(class_table.parent)
            if class_table is None:
                raise CompilationError(ErrorType.undefinedVar, 'Undefined variable: ' + name, lineno)

    def resolve_method(self, class_name, method_name, lineno):
        if class_name not in self.table:
            raise CompilationError(ErrorType.noMethodsExist, f'Type "{class_name}" has no methods', lineno)
        class_table = self.table[class_name]
        current = class_name
        while True:
            if method_name in class_table.methods:
                return (class_table.methods[method_name], current)
            current = class_table.parent
            class_table = self.table.get(current)
            if class_table is None:
                raise CompilationError(ErrorType.undefinedMethod, f'Undefined method: {class_name}.{method_name}', lineno)

    def visit_goal(self, node, *args):
        self.visit(node.main)
        for n in node.classes:
            self.visit(n)

    def visit_main_class(self, node, *args):
        self.visit(node.statement)

    def visit_class_declaration(self, node, *args):
        self.class_name = node.name
        for var in node.vardecl:
            self.visit(var)
        for method in node.methoddecl:
            self.visit(method)
        self.class_name = None

    def visit_method_declaration(self, node, *args):
        self.assert_type_exists(node.return_type, node.lineno)
        self.method_name = node.name
        for param in node.argseq:
            self.visit(param)
        for var in node.vardecl:
            self.visit(var)
        for stmt in node.statement:
            self.visit(stmt)
        self.assert_is_subclass(self.visit(node.retexpr), self.table[self.class_name].methods[node.name].return_type,
                                node.ret_lineno)
        self.method_name = None

    def visit_method_parameter(self, node, *args):
        self.assert_type_exists(node.cur_type, node.lineno)

    def visit_var_declaration(self, node, *args):
        self.assert_type_exists(node.vartype, node.lineno)

    def visit_bool_literal(self, node, *args):
        return 'boolean'

    def visit_int_literal(self, node, *args):
        return 'int'

    def visit_identifier(self, node,  *args):
        return self.resolve_id(node.name, node.lineno)

    def visit_bin_op(self, node, *args):
        l = self.visit(node.left)
        r = self.visit(node.right)
        if node.op in ['+', '-', '*', '%']:
            self.assert_is_subclass(l, 'int', node.lineno)
            self.assert_is_subclass(r, 'int', node.lineno)
            return 'int'
        if node.op in ['&&', '||']:
            self.assert_is_subclass(l, 'boolean', node.lineno)
            self.assert_is_subclass(r, 'boolean', node.lineno)
            return 'boolean'
        if node.op == '<':
            self.assert_is_subclass(l, 'int', node.lineno)
            self.assert_is_subclass(r, 'int', node.lineno)
            return 'boolean'
        assert False

    def visit_un_op(self, node, *args):
        c = self.visit(node.child)
        assert node.op == '!'
        self.assert_is_subclass(c, 'boolean', node.lineno)
        return 'boolean'

    def visit_new_expression(self, node, *args):
        self.assert_type_exists(node.type, node.lineno)
        return node.type

    def visit_new_array_expression(self, node, *args):
        size = self.visit(node.size)
        self.assert_is_subclass(size, 'int', node.lineno)
        return 'int[]'

    def visit_index_expression(self, node, *args):
        obj = self.visit(node.obj)
        idx = self.visit(node.idx)
        self.assert_is_subclass(obj, 'int[]', node.lineno)
        self.assert_is_subclass(idx, 'int', node.lineno)
        return 'int'

    def visit_length_expression(self, node, *args):
        obj = self.visit(node.obj)
        self.assert_is_subclass(obj, 'int[]', node.lineno)
        return 'int'

    def visit_call_expression(self, node, *args):
        obj = self.visit(node.obj)
        method, method_owner = self.resolve_method(obj, node.method, node.lineno)
        if not method.is_public and method_owner != self.class_name:
            raise CompilationError(ErrorType.privateMethod, f'Method {method_owner}.{node.method} is private', node.lineno)
        if len(method.params) != len(node.args):
            raise CompilationError(ErrorType.wrongArgument, f'Expected {len(method.params)} argument{"s" if len(method.params) != 1 else ""} '
                                   f'for {obj}.{node.method}', node.lineno)
        for arg, param in zip(node.args, method.params.values()):
            arg = self.visit(arg)
            self.assert_is_subclass(arg, param, node.lineno)
        return method.return_type

    def visit_assign_statement(self, node, *args):
        obj = self.resolve_id(node.obj, node.lineno)
        val = self.visit(node.value)
        self.assert_is_subclass(val, obj, node.lineno)

    def visit_array_assign_statement(self, node, *args):
        obj = self.resolve_id(node.obj, node.lineno)
        idx = self.visit(node.index)
        val = self.visit(node.value)
        self.assert_is_subclass(obj, 'int[]', node.lineno)
        self.assert_is_subclass(idx, 'int', node.lineno)
        self.assert_is_subclass(val, 'int', node.lineno)

    def visit_print_statement(self, node, *args):
        val = self.visit(node.value)
        self.assert_is_subclass(val, 'int', node.lineno)

    def visit_if_statement(self, node, *args):
        cond = self.visit(node.condition)
        self.assert_is_subclass(cond, 'boolean', node.lineno)
        for stmt in node.stmt_then:
            self.visit(stmt)
        for stmt in node.stmt_else:
            self.visit(stmt)

    def visit_while_statement(self, node, *args):
        cond = self.visit(node.condition)
        self.assert_is_subclass(cond, 'boolean', node.lineno)
        for stmt in node.stmt:
            self.visit(stmt)


def typecheck(node, symbol_table):
    visitor = TypeInferenceVisitor(symbol_table)
    visitor.visit(node)
