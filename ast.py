
class Node:

    lineno = None

    def __str__(self):
        return self.__class__.__name__


class BinOp(Node):

    def __init__(self, _op, lhs, rhs):
        self.left = lhs
        self.right = rhs
        self.op = _op

    def __str__(self):
        return str(self.op)


class UnOp(Node):

    def __init__(self, _op, child):
        self.child = child
        self.op = _op

    def __str__(self):
        return str(self.op)


class Goal(Node):

    def __init__(self, lhs, rhs):
        self.main = lhs
        self.classes = rhs


class ClassDeclaration(Node):

    def __init__(self, name, lhs, rhs, parent=None):
        self.vardecl = lhs
        self.methoddecl = rhs
        self.name = name
        self.parent = parent

    def __str__(self):
        return str(self.name)


class MainClass(Node):

    def __init__(self, name, statement):
        self.name = name
        self.statement = statement


class MethodDeclaration(Node):

    ret_lineno = None

    def __init__(self, is_public, return_type, name, argseq, vardecl, statement, retexpr):
        self.is_public = is_public
        self.return_type = return_type
        self.name = name
        self.argseq = argseq
        self.vardecl = vardecl
        self.statement = statement
        self.retexpr = retexpr

    def __str__(self):
        return str(self.name)


class VarDeclaration(Node):

    def __init__(self, vartype, varid):
        self.vartype = vartype
        self.varid = varid

    def __str__(self):
        return str(self.varid)


class MethodParameter(Node):

    def __init__(self, cur_type, cur_id):
        self.cur_id = cur_id
        self.cur_type = cur_type

    def __str__(self):
        return self.cur_id


class Literal(Node):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class BoolLiteral(Literal):
    pass


class IntLiteral(Literal):
    pass


class Identifier(Node):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)


class NewExpression(Node):

    def __init__(self, t):
        self.type = t

    def __str__(self):
        return 'new ' + self.type


class NewArrayExpression(Node):

    def __init__(self, size):
        self.size = size

    def __str__(self):
        return 'new int[]'


class IndexExpression(Node):

    def __init__(self, obj, idx):
        self.obj = obj
        self.idx = idx


class LengthExpression(Node):

    def __init__(self, obj):
        self.obj = obj


class CallExpression(Node):

    def __init__(self, obj, method, args):
        self.obj = obj
        self.method = method
        self.args = args

    def __str__(self):
        return str(self.method)


class AssignStatement(Node):

    def __init__(self, obj, value):
        self.obj = obj
        self.value = value

    def __str__(self):
        return str(self.obj)


class ArrayAssignStatement(Node):

    def __init__(self, obj, index, value):
        self.obj = obj
        self.index = index
        self.value = value

    def __str__(self):
        return str(self.obj)


class PrintStatement(Node):

    def __init__(self, value):
        self.value = value


class IfStatement(Node):

    def __init__(self, cond, stmt_then, stmt_else):
        self.condition = cond
        self.stmt_then = stmt_then
        self.stmt_else = stmt_else


class WhileStatement(Node):

    def __init__(self, cond, stmt):
        self.condition = cond
        self.stmt = stmt
