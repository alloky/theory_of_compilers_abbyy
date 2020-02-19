EXPR = 0
COND = 1


def to_printable(node):
    return node.__class__.__name__ + ' ' + ' '.join(f'{k}={v}' for k, v in node.__dict__.items())


class Method:
    def __init__(self, statements, return_location):
        self.statements = statements
        self.return_location = return_location

    def to_printable(self):
        return ('\n'.join(map(to_printable, self.statements))
                + ('\nRETURN ' + str(self.return_location) if self.return_location else ''))


class IROp:
    complexity = 0
    local = True
    reorderable = True


class Const(IROp):
    def __init__(self, value, trg):
        self.value = value
        self.trg = trg


class BinOp(IROp):
    def __init__(self, op, lhs, rhs, trg):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
        self.trg = trg

    complexity = 1


class Not(IROp):
    def __init__(self, arg, trg):
        self.arg = arg
        self.trg = trg


class Jump(IROp):
    def __init__(self, label):
        self.label = label


class CJumpLess(IROp):
    def __init__(self, lhs, rhs, iftrue, iffalse):
        self.lhs = lhs
        self.rhs = rhs
        self.iftrue = iftrue
        self.iffalse = iffalse


class CJumpBool(IROp):
    def __init__(self, val, iftrue, iffalse):
        self.val = val
        self.iftrue = iftrue
        self.iffalse = iffalse


class Label(IROp):
    def __init__(self, label_id):
        self.label_id = label_id


class New(IROp):
    def __init__(self, obj_type, trg):
        self.obj_type = obj_type
        self.trg = trg

    complexity = 100


class NewArray(IROp):
    def __init__(self, size, trg):
        self.size = size
        self.trg = trg

    complexity = 100


class Index(IROp):
    def __init__(self, obj, idx, trg):
        self.obj = obj
        self.idx = idx
        self.trg = trg

    local = False
    complexity = 1


class Length(IROp):
    def __init__(self, obj, trg):
        self.obj = obj
        self.trg = trg


class Call(IROp):
    def __init__(self, method, args, trg):
        self.method = method
        self.args = args
        self.trg = trg

    local = False
    complexity = 100


class Param(IROp):
    def __init__(self, name, trg):
        self.name = name
        self.trg = trg


class Local(IROp):
    def __init__(self, name, trg):
        self.name = name
        self.trg = trg


class Field(IROp):
    def __init__(self, cls, name, trg):
        self.cls = cls
        self.name = name
        self.trg = trg

    local = False


class AssignParam(IROp):
    def __init__(self, name, src):
        self.name = name
        self.src = src

    reorderable = False


class AssignLocal(IROp):
    def __init__(self, name, src):
        self.name = name
        self.src = src

    reorderable = False


class AssignField(IROp):
    def __init__(self, cls, name, src):
        self.cls = cls
        self.name = name
        self.src = src

    reorderable = False


class ArrayAssign(IROp):
    def __init__(self, arr, idx, src):
        self.arr = arr
        self.idx = idx
        self.src = src

    reorderable = False


class Print(IROp):
    def __init__(self, src):
        self.src = src

    reorderable = False
