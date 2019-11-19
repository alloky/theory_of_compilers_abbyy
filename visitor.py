from functools import lru_cache

import mj_ast


@lru_cache(0)
def to_snake_case(s):
    res = []
    word = []
    for c in s:
        if c.isupper():
            if word:
                res.append(''.join(word).lower())
            word = [c]
        else:
            word.append(c)
    res.append(''.join(word).lower())
    return '_'.join(res)


class BaseVisitor:

    def visit(self, node: mj_ast.Node, *args):
        return getattr(self, 'visit_' + to_snake_case(node.__class__.__name__), self.visit_unknown)(node, *args)

    def visit_unknown(self, node, *args):
        raise TypeError('Unhandled node type: ' + node.__class__.__name__)

    def visit_goal(self, node: mj_ast.Goal, *args):
        pass

    def visit_main_class(self, node: mj_ast.MainClass, *args):
        pass

    def visit_class_declaration(self, node: mj_ast.ClassDeclaration, *args):
        pass

    def visit_method_declaration(self, node: mj_ast.MethodDeclaration, *args):
        pass

    def visit_method_parameter(self, node: mj_ast.MethodParameter, *args):
        pass

    def visit_var_declaration(self, node: mj_ast.VarDeclaration, *args):
        pass

    def visit_bool_literal(self, node: mj_ast.BoolLiteral, *args):
        pass

    def visit_int_literal(self, node: mj_ast.IntLiteral, *args):
        pass

    def visit_identifier(self, node: mj_ast.Identifier, *args):
        pass

    def visit_bin_op(self, node: mj_ast.BinOp, *args):
        pass

    def visit_un_op(self, node: mj_ast.UnOp, *args):
        pass

    def visit_new_expression(self, node: mj_ast.NewExpression, *args):
        pass

    def visit_new_array_expression(self, node: mj_ast.NewArrayExpression, *args):
        pass

    def visit_index_expression(self, node: mj_ast.IndexExpression, *args):
        pass

    def visit_length_expression(self, node: mj_ast.LengthExpression, *args):
        pass

    def visit_call_expression(self, node: mj_ast.CallExpression, *args):
        pass

    def visit_assign_statement(self, node: mj_ast.AssignStatement, *args):
        pass

    def visit_array_assign_statement(self, node: mj_ast.ArrayAssignStatement, *args):
        pass

    def visit_print_statement(self, node: mj_ast.PrintStatement, *args):
        pass

    def visit_if_statement(self, node: mj_ast.IfStatement, *args):
        pass

    def visit_while_statement(self, node: mj_ast.WhileStatement, *args):
        pass
