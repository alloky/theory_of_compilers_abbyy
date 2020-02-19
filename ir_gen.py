import ir
import mj_ast
from ir_transform import transform
from visitor import BaseVisitor


def resolve_identifier(node_type, name, ret):
    if node_type == mj_ast.PARAM:
        return ir.Param(name, ret)
    if node_type == mj_ast.LOCAL:
        return ir.Local(name, ret)
    assert node_type[0] == mj_ast.FIELD
    return ir.Field(node_type[1], name, ret)


def linearize(lst):
    res = []
    for i in lst:
        if isinstance(i, list):
            res.extend(linearize(i))
        else:
            res.append(i)
    return res


def postprocess_ir(lst):
    return transform(linearize(lst))


def total_complexity(lst):
    return max(i.complexity for i in lst)


def all_local(lst):
    return all(i.local for i in lst)


class IRTreeGenerator(BaseVisitor):

    def __init__(self):
        self.class_name = None
        self.method_name = None
        self._counter = 0

    def get_id(self):
        self._counter += 1
        return self._counter

    def clear_counter(self):
        self._counter = 0

    def reorder_for_bin_op(self, left, right, lhs, rhs):
        arg1 = linearize([self.visit(left, ir.EXPR, lhs)])
        arg2 = linearize([self.visit(right, ir.EXPR, rhs)])
        if total_complexity(arg1) < total_complexity(arg2) and (all_local(arg1) or all_local(arg2)):
            arg1, arg2 = arg2, arg1
        return arg1, arg2

    def visit_goal(self, node, *args):
        tree = self.visit(node.main)
        for n in node.classes:
            tree.update(self.visit(n))
        return tree

    def visit_main_class(self, node, *args):
        return {'main': ir.Method(postprocess_ir([self.visit(node.statement)]), None)}

    def visit_class_declaration(self, node, *args):
        self.class_name = node.name
        table = {}
        for method in node.methoddecl:
            table.update(self.visit(method))
        self.class_name = None
        return table

    def visit_method_declaration(self, node, *args):
        self.clear_counter()
        self.method_name = node.name
        table = []
        for stmt in node.statement:
            table.append(self.visit(stmt))
        ret = self.get_id()
        table = {(self.class_name + '.' + node.name): ir.Method(postprocess_ir(table + [self.visit(node.retexpr, ir.EXPR, ret)]), ret)}
        self.method_name = None
        return table

    def visit_bool_literal(self, node, target, *args):
        if target == ir.EXPR:
            return ir.Const(int(node.value), args[0])
        else:
            if node.value:
                return ir.Jump(args[0])
            else:
                return ir.Jump(args[1])

    def visit_int_literal(self, node, target, *args):
        assert target == ir.EXPR
        return ir.Const(node.value, args[0])

    def visit_identifier(self, node, target, *args):
        if target == ir.EXPR:
            return resolve_identifier(node.type, node.name, args[0])
        else:
            val = self.get_id()
            return [
                resolve_identifier(node.type, node.name, val),
                ir.CJumpBool(val, args[0], args[1]),
            ]

    def visit_bin_op(self, node, target, *args):
        if node.op in ['+', '-', '*', '%'] or (node.op == '<' and target == ir.EXPR):
            assert target == ir.EXPR
            lhs = self.get_id()
            rhs = self.get_id()
            arg1, arg2 = self.reorder_for_bin_op(node.left, node.right, lhs, rhs)
            return [
                arg1,
                arg2,
                ir.BinOp(node.op, lhs, rhs, args[0]),
            ]
        if node.op == '<':
            assert target == ir.COND
            lhs = self.get_id()
            rhs = self.get_id()
            arg1, arg2 = self.reorder_for_bin_op(node.left, node.right, lhs, rhs)
            return [
                arg1,
                arg2,
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
                    ir.Const(1, args[0]),
                    ir.Jump(lbl_end),
                    ir.Label(lbl_false),
                    ir.Const(0, args[0]),
                    ir.Label(lbl_end),
                ]
        if node.op == '||':
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
                    ir.Const(0, args[0]),
                    ir.Jump(lbl_end),
                    ir.Label(lbl_true),
                    ir.Const(1, args[0]),
                    ir.Label(lbl_end),
                ]
        assert False

    def visit_un_op(self, node, target, *args):
        if target == ir.COND:
            return self.visit(node.child, ir.COND, args[1], args[0])
        else:
            arg = self.get_id()
            return [
                self.visit(node.child, ir.EXPR, arg),
                ir.Not(arg, args[0]),
            ]

    def visit_new_expression(self, node, target, *args):
        assert target == ir.EXPR
        return ir.New(node.type, args[0])

    def visit_new_array_expression(self, node, target, *args):
        assert target == ir.EXPR
        size = self.get_id()
        return [
            self.visit(node.size, ir.EXPR, size),
            ir.NewArray(size, args[0]),
        ]

    def visit_index_expression(self, node, target, *args):
        assert target == ir.EXPR
        obj = self.get_id()
        idx = self.get_id()
        arg1, arg2 = self.reorder_for_bin_op(node.obj, node.idx, obj, idx)
        return [
            arg1,
            arg2,
            ir.Index(obj, idx, args[0]),
        ]

    def visit_length_expression(self, node, target, *args):
        assert target == ir.EXPR
        obj = self.get_id()
        return [
            self.visit(node.obj, ir.EXPR, obj),
            ir.Length(obj, args[0]),
        ]

    def visit_call_expression(self, node, target, *args):
        this = self.get_id()
        arg_ids = [self.get_id() for _ in node.args]
        compute_this = linearize([self.visit(node.obj, ir.EXPR, this)])
        compute_args = [linearize([self.visit(arg, ir.EXPR, trg)]) for arg, trg in zip(node.args, arg_ids)]
        if all_local(compute_this):
            compute_args = [compute_this] + compute_args
            compute_this = []
        compute_args.sort(key=total_complexity, reverse=True)
        if target == ir.EXPR:
            return compute_this + compute_args + [
                ir.Call(node.method_owner + '.' + node.method, [this] + arg_ids, args[0]),
            ]
        else:
            val = self.get_id()
            return compute_this + compute_args + [
                ir.Call(node.method_owner + '.' + node.method, [this] + arg_ids, val),
                ir.CJumpBool(val, args[0], args[1]),
            ]

    def visit_assign_statement(self, node, *args):
        tmp = self.get_id()
        compute_val = self.visit(node.value, ir.EXPR, tmp)
        if node.type == mj_ast.PARAM:
            return [compute_val, ir.AssignParam(node.obj, tmp)]
        if node.type == mj_ast.LOCAL:
            return [compute_val, ir.AssignLocal(node.obj, tmp)]
        assert node.type[0] == mj_ast.FIELD
        return [compute_val, ir.AssignField(node.type[1], node.obj, tmp)]

    def visit_array_assign_statement(self, node, *args):
        val = self.get_id()
        idx = self.get_id()
        arr = self.get_id()
        compute_arr = linearize([resolve_identifier(node.type, node.obj, arr)])
        compute_args = [linearize([self.visit(node.index, ir.EXPR, idx)]),
                        linearize([self.visit(node.value, ir.EXPR, val)])]
        if all_local(compute_arr) or all(all_local(i) for i in compute_args):
            compute_args = [compute_arr] + compute_args
            compute_arr = []
        compute_args.sort(key=total_complexity, reverse=True)
        return [
            compute_arr,
            *compute_args,
            ir.ArrayAssign(arr, idx, val),
        ]

    def visit_print_statement(self, node, *args):
        val = self.get_id()
        return [
            self.visit(node.value, ir.EXPR, val),
            ir.Print(val),
        ]

    def visit_if_statement(self, node, *args):
        lbl_then = self.get_id()
        lbl_else = self.get_id()
        lbl_end = self.get_id()
        return [
            self.visit(node.condition, ir.COND, lbl_then, lbl_else),
            ir.Label(lbl_then),
            list(map(self.visit, node.stmt_then)),
            ir.Jump(lbl_end),
            ir.Label(lbl_else),
            list(map(self.visit, node.stmt_else)),
            ir.Label(lbl_end),
        ]

    def visit_while_statement(self, node, *args):
        lbl_start = self.get_id()
        lbl_body = self.get_id()
        lbl_end = self.get_id()
        return [
            ir.Label(lbl_start),
            self.visit(node.condition, ir.COND, lbl_body, lbl_end),
            ir.Label(lbl_body),
            list(map(self.visit, node.stmt)),
            ir.Jump(lbl_start),
            ir.Label(lbl_end),
        ]


def build_ir(node):
    visitor = IRTreeGenerator()
    return visitor.visit(node)
