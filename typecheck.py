from visitor import BaseVisitor


class TypeInferenceVisitor(BaseVisitor):

    ATOMS = ['int', 'int[]', 'boolean']

    def __init__(self, symbol_table):
        self.table = symbol_table
        self.class_name = None
        self.method_name = None

    def assert_type_exists(self, node_type):
        assert node_type in self.ATOMS or node_type in self.table

    def assert_is_subclass(self, node_type, expected_type):
        if expected_type in self.ATOMS or node_type in self.ATOMS:
            assert node_type == expected_type
        while True:
            if node_type == expected_type:
                return
            node_type = self.table[node_type].parent
            assert node_type is not None

    def resolve_id(self, name):
        assert self.class_name and self.method_name
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
            class_table = self.table[class_table.parent]
            if class_table is None:
                assert False

    def resolve_method(self, class_name, method_name):
        class_table = self.table[class_name]
        while True:
            if method_name in class_table.methods:
                return class_table.methods[method_name]
            class_table = self.table[class_table.parent]
            if class_table is None:
                assert False

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
        self.method_name = node.name
        for param in node.argseq:
            self.visit(param)
        for var in node.vardecl:
            self.visit(var)
        for stmt in node.statement:
            self.visit(stmt)
        assert self.visit(node.retexpr) == self.table[self.class_name].methods[node.name].return_type
        self.method_name = None

    def visit_method_parameter(self, node, *args):
        self.assert_type_exists(node.cur_type)

    def visit_var_declaration(self, node, *args):
        self.assert_type_exists(node.vartype)

    def visit_bool_literal(self, node, *args):
        return 'boolean'

    def visit_int_literal(self, node, *args):
        return 'int'

    def visit_identifier(self, node,  *args):
        return self.resolve_id(node.name)

    def visit_bin_op(self, node, *args):
        l = self.visit(node.left)
        r = self.visit(node.right)
        if node.op in ['+', '-', '*', '%']:
            assert l == 'int' and r == 'int'
            return 'int'
        if node.op in ['&&', '||']:
            assert l == 'boolean' and r == 'boolean'
            return 'boolean'
        if node.op == '<':
            assert l == 'int' and r == 'int'
            return 'boolean'
        assert False

    def visit_un_op(self, node, *args):
        c = self.visit(node.child)
        assert node.op == '!'
        assert c == 'boolean'
        return 'boolean'

    def visit_new_expression(self, node, *args):
        return node.type

    def visit_new_array_expression(self, node, *args):
        size = self.visit(node.size)
        assert size == 'int'
        return 'int[]'

    def visit_index_expression(self, node, *args):
        obj = self.visit(node.obj)
        idx = self.visit(node.idx)
        assert obj == 'int[]'
        assert idx == 'int'
        return 'int'

    def visit_length_expression(self, node, *args):
        obj = self.visit(node.obj)
        assert obj == 'int[]'
        return 'int'

    def visit_call_expression(self, node, *args):
        obj = self.visit(node.obj)
        assert obj in self.table
        method = self.resolve_method(obj, node.method)
        assert len(method.params) == len(node.args)
        for arg, param in zip(node.args, method.params.values()):
            arg = self.visit(arg)
            self.assert_is_subclass(arg, param)
        return method.return_type

    def visit_assign_statement(self, node, *args):
        obj = self.resolve_id(node.obj)
        val = self.visit(node.value)
        self.assert_is_subclass(val, obj)

    def visit_array_assign_statement(self, node, *args):
        obj = self.resolve_id(node.obj)
        idx = self.visit(node.index)
        val = self.visit(node.value)
        assert obj == 'int[]'
        assert idx == 'int'
        assert val == 'int'

    def visit_print_statement(self, node, *args):
        val = self.visit(node.value)
        assert val == 'int'

    def visit_if_statement(self, node, *args):
        cond = self.visit(node.condition)
        assert cond == 'boolean'
        for stmt in node.stmt_then:
            self.visit(stmt)
        for stmt in node.stmt_else:
            self.visit(stmt)

    def visit_while_statement(self, node, *args):
        cond = self.visit(node.condition)
        assert cond == 'boolean'
        for stmt in node.stmt:
            self.visit(stmt)


def typecheck(node, symbol_table):
    visitor = TypeInferenceVisitor(symbol_table)
    visitor.visit(node)
