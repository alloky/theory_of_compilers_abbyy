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
    side_effect_free = True

    def sources(self):
        return []

    def targets(self):
        return []


class Const(IROp):
    def __init__(self, value, trg):
        self.value = value
        self.trg = trg

    def targets(self):
        return [self.trg]


class BinOp(IROp):
    def __init__(self, op, lhs, rhs, trg):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
        self.trg = trg

    def sources(self):
        return [self.lhs, self.rhs]

    def targets(self):
        return [self.trg]

    complexity = 1


class Not(IROp):
    def __init__(self, arg, trg):
        self.arg = arg
        self.trg = trg

    def sources(self):
        return [self.arg]

    def targets(self):
        return [self.trg]


class Jump(IROp):
    def __init__(self, label):
        self.label = label

    side_effect_free = False


class CJumpLess(IROp):
    def __init__(self, lhs, rhs, iftrue, iffalse):
        self.lhs = lhs
        self.rhs = rhs
        self.iftrue = iftrue
        self.iffalse = iffalse

    def sources(self):
        return [self.lhs, self.rhs]

    side_effect_free = False


class CJumpBool(IROp):
    def __init__(self, val, iftrue, iffalse):
        self.val = val
        self.iftrue = iftrue
        self.iffalse = iffalse

    def sources(self):
        return [self.val]

    side_effect_free = False


class Label(IROp):
    def __init__(self, label_id):
        self.label_id = label_id

    side_effect_free = False


class New(IROp):
    def __init__(self, obj_type, trg):
        self.obj_type = obj_type
        self.trg = trg

    def targets(self):
        return [self.trg]

    complexity = 100


class NewArray(IROp):
    def __init__(self, size, trg):
        self.size = size
        self.trg = trg

    def sources(self):
        return [self.size]

    def targets(self):
        return [self.trg]

    complexity = 100


class Index(IROp):
    def __init__(self, obj, idx, trg):
        self.obj = obj
        self.idx = idx
        self.trg = trg

    def sources(self):
        return [self.obj, self.idx]

    def targets(self):
        return [self.trg]

    local = False
    complexity = 1


class Length(IROp):
    def __init__(self, obj, trg):
        self.obj = obj
        self.trg = trg

    def sources(self):
        return [self.obj]

    def targets(self):
        return [self.trg]


class Call(IROp):
    def __init__(self, method, args, trg):
        self.method = method
        self.args = args
        self.trg = trg

    def sources(self):
        return self.args

    def targets(self):
        return [self.trg]

    local = False
    side_effect_free = False
    complexity = 100


class Param(IROp):
    def __init__(self, name, trg):
        self.name = name
        self.trg = trg

    def targets(self):
        return [self.trg]


class Local(IROp):
    def __init__(self, name, trg):
        self.name = name
        self.trg = trg

    def targets(self):
        return [self.trg]


class Field(IROp):
    def __init__(self, cls, name, trg):
        self.cls = cls
        self.name = name
        self.trg = trg

    def targets(self):
        return [self.trg]

    local = False


class AssignParam(IROp):
    def __init__(self, name, src):
        self.name = name
        self.src = src

    def sources(self):
        return [self.src]

    reorderable = False
    side_effect_free = False


class AssignLocal(IROp):
    def __init__(self, name, src):
        self.name = name
        self.src = src

    def sources(self):
        return [self.src]

    reorderable = False
    side_effect_free = False


class AssignField(IROp):
    def __init__(self, cls, name, src):
        self.cls = cls
        self.name = name
        self.src = src

    def sources(self):
        return [self.src]

    reorderable = False
    side_effect_free = False


class ArrayAssign(IROp):
    def __init__(self, arr, idx, src):
        self.arr = arr
        self.idx = idx
        self.src = src

    def sources(self):
        return [self.arr, self.idx, self.src]

    reorderable = False
    side_effect_free = False


class Print(IROp):
    def __init__(self, src):
        self.src = src

    def sources(self):
        return [self.src]

    reorderable = False
    side_effect_free = False
