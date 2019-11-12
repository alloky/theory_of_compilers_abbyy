from functools import lru_cache

import ast


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

    def visit(self, node: ast.Node):
        return getattr(self, 'visit_' + to_snake_case(node.__class__.__name__), self.visit_unknown)(node)

    def visit_unknown(self, node):
        raise TypeError('Unhandled node type: ' + node.__class__.__name__)

    def visit_goal(self, node: ast.Goal):
        pass

    def visit_main_class(self, node: ast.MainClass):
        pass

    def visit_class_declaration(self, node: ast.ClassDeclaration):
        pass

    def visit_method_declaration(self, node: ast.MethodDeclaration):
        pass

    def visit_method_parameter(self, node: ast.MethodParameter):
        pass

    def visit_var_declaration(self, node: ast.VarDeclaration):
        pass

    def visit_bool_literal(self, node: ast.BoolLiteral):
        pass

    def visit_int_literal(self, node: ast.IntLiteral):
        pass

    def visit_identifier(self, node: ast.Identifier):
        pass

    def visit_bin_op(self, node: ast.BinOp):
        pass

    def visit_un_op(self, node: ast.UnOp):
        pass

    def visit_new_expression(self, node: ast.NewExpression):
        pass

    def visit_new_array_expression(self, node: ast.NewArrayExpression):
        pass

    def visit_index_expression(self, node: ast.IndexExpression):
        pass

    def visit_length_expression(self, node: ast.LengthExpression):
        pass

    def visit_call_expression(self, node: ast.CallExpression):
        pass

    def visit_assign_statement(self, node: ast.AssignStatement):
        pass

    def visit_array_assign_statement(self, node: ast.ArrayAssignStatement):
        pass

    def visit_print_statement(self, node: ast.PrintStatement):
        pass

    def visit_if_statement(self, node: ast.IfStatement):
        pass

    def visit_while_statement(self, node: ast.WhileStatement):
        pass
