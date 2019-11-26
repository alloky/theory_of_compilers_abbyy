import ir
from visitor import BaseVisitor


class IRTreeGenerator(BaseVisitor):

    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.class_name = None
        self.method_name = None
        self._counter = 0

    def get_id(self):
        self._counter += 1
        return self._counter

    def visit_goal(self, node, *args):
        tree = self.visit(node.main)
        for n in node.classes:
            tree.update(self.visit(n))
        return tree

    def visit_main_class(self, node, *args):
        return {'main': ir.Method([], self.visit(node))}

    def visit_class_declaration(self, node, *args):
        self.class_name = node.name
        table = {}
        for method in node.methoddecl:
            table.update(self.visit(method))
        self.class_name = None
        return table

    def visit_method_declaration(self, node, *args):
        self.method_name = node.name
        table = []
        for stmt in node.statement:
            table.append(self.visit(stmt))
        table = {(self.class_name + '.' + node.name): ir.Method(table, self.visit(node.retexpr))}
        self.method_name = None
        return table

    def visit_bool_literal(self, node, *args):
        return ir.Const(args[0], int(node.value))

    def visit_int_literal(self, node, *args):
        return ir.Const(args[0], node.value)

    def visit_identifier(self, node, *args):
        raise NotImplementedError

    def visit_bin_op(self, node, target, *args):
        if node.op in ['+', '-', '*', '%'] or (node.op == '<' and target == ir.EXPR):
            assert target == ir.EXPR
            lhs = self.get_id()
            rhs = self.get_id()
            return [
                self.visit(node.left, ir.EXPR, lhs),
                self.visit(node.right, ir.EXPR, rhs),
                ir.BinOp(node.op, lhs, rhs, args[0]),
            ]
        if node.op == '<':
            assert target == ir.COND
            lhs = self.get_id()
            rhs = self.get_id()
            return [
                self.visit(node.left, ir.EXPR, lhs),
                self.visit(node.right, ir.EXPR, rhs),
                ir.CJumpLess(lhs, rhs, args[0], args[1]),
            ]
        if node.op == '&&':
            if target == ir.COND:
                lbl_second_arg = self.get_id()
                return [
                    self.visit(node.left, ir.COND, lbl_second_arg, args[1]),
                    ir.Label(lbl_second_arg),
                    self.visit(node.right, ir.COND, args[0], args[1]),
                ]
            else:
                lbl_second_arg = self.get_id()
                lbl_false = self.get_id()
                lbl_true = self.get_id()
                lbl_end = self.get_id()
                return [
                    self.visit(node.left, ir.COND, lbl_second_arg, lbl_false),
                    ir.Label(lbl_second_arg),
                    self.visit(node.right, ir.COND, lbl_true, lbl_false),
                    ir.Label(lbl_true),
                    ir.Const(args[0], 1),
                    ir.Jump(lbl_end),
                    ir.Label(lbl_false),
                    ir.Const(args[0], 0),
                    ir.Label(lbl_end),
                ]
        if node == '||':
            if target == ir.COND:
                lbl_second_arg = self.get_id()
                return [
                    self.visit(node.left, ir.COND, args[0], lbl_second_arg),
                    ir.Label(lbl_second_arg),
                    self.visit(node.right, ir.COND, args[0], args[1]),
                ]
            else:
                lbl_second_arg = self.get_id()
                lbl_false = self.get_id()
                lbl_true = self.get_id()
                lbl_end = self.get_id()
                return [
                    self.visit(node.left, ir.COND, lbl_true, lbl_second_arg),
                    ir.Label(lbl_second_arg),
                    self.visit(node.right, ir.COND, lbl_true, lbl_false),
                    ir.Label(lbl_false),
                    ir.Const(args[0], 0),
                    ir.Jump(lbl_end),
                    ir.Label(lbl_true),
                    ir.Const(args[0], 1),
                    ir.Label(lbl_end),
                ]

    def visit_un_op(self, node, target, *args):
        if target == ir.COND:
            return self.visit(node.child, ir.COND, args[1], args[0])
        else:
            arg = self.get_id()
            return [
                self.visit(node.child, ir.EXPR, arg),
                ir.Not(arg, args[0]),
            ]

    def visit_new_expression(self, node, *args):
        return ir.New(node.type, args[0])

    def visit_new_array_expression(self, node, *args):
        size = self.get_id()
        return [
            self.visit(node.size, ir.EXPR, size),
            ir.NewArray(size, args[0]),
        ]

    def visit_index_expression(self, node, *args):
        obj = self.get_id()
        idx = self.get_id()
        return [
            self.visit(node.idx, ir.EXPR, idx),
            self.visit(node.obj, ir.EXPR, obj),
            ir.Index(obj, idx, args[0]),
        ]

    def visit_length_expression(self, node, *args):
        obj = self.get_id()
        return [
            self.visit(node.obj, ir.EXPR, obj),
            ir.Length(obj, args[0]),
        ]

    def visit_call_expression(self, node, *args):
        arg_ids = [self.get_id() for _ in node.args]
        compute_args = [self.visit(arg, ir.EXPR, trg) for arg, trg in zip(node.args, arg_ids)]
        this = self.get_id()
        return compute_args + [
            self.visit(node.obj, ir.EXPR, this),
            ir.Call(node.method, [this] + arg_ids, args[0]),
        ]
