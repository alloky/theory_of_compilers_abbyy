EXPR = 0
COND = 1


def linearize(lst):
    res = []
    for i in lst:
        if isinstance(i, list):
            res.extend(linearize(i))
        else:
            res.append(i)
    return res


def to_printable(node):
    return node.__class__.__name__ + ' ' + ' '.join(f'{k}={v}' for k, v in node.__dict__.items())


class Method:
    def __init__(self, statements, ret, return_location):
        self.statements = linearize(statements)
        self.ret = linearize([ret])
        self.return_location = return_location

    def to_printable(self):
        return ('\n'.join(map(to_printable, self.statements)) + '\n' + '\n'.join(map(to_printable, self.ret))
                + ('\nRETURN ' + str(self.return_location) if self.return_location else ''))


class Const:
    def __init__(self, value, trg):
        self.value = value
        self.trg = trg


class BinOp:
    def __init__(self, op, lhs, rhs, trg):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
        self.trg = trg


class Not:
    def __init__(self, arg, trg):
        self.arg = arg
        self.trg = trg


class Jump:
    def __init__(self, label):
        self.label = label


class CJumpLess:
    def __init__(self, lhs, rhs, iftrue, iffalse):
        self.lhs = lhs
        self.rhs = rhs
        self.iftrue = iftrue
        self.iffalse = iffalse


class Label:
    def __init__(self, label_id):
        self.label_id = label_id


class New:
    def __init__(self, obj_type, trg):
        self.obj_type = obj_type
        self.trg = trg


class NewArray:
    def __init__(self, size, trg):
        self.size = size
        self.trg = trg


class Index:
    def __init__(self, obj, idx, trg):
        self.obj = obj
        self.idx = idx
        self.trg = trg


class Length:
    def __init__(self, obj, trg):
        self.obj = obj
        self.trg = trg


class Call:
    def __init__(self, method, args, trg):
        self.method = method
        self.args = args
        self.trg = trg


class Param:
    def __init__(self, name, trg):
        self.name = name
        self.trg = trg


class Local:
    def __init__(self, name, trg):
        self.name = name
        self.trg = trg


class Field:
    def __init__(self, cls, name, trg):
        self.cls = cls
        self.name = name
        self.trg = trg


class AssignParam:
    def __init__(self, name, src):
        self.name = name
        self.src = src


class AssignLocal:
    def __init__(self, name, src):
        self.name = name
        self.src = src


class AssignField:
    def __init__(self, cls, name, src):
        self.cls = cls
        self.name = name
        self.src = src


class ArrayAssign:
    def __init__(self, arr, idx, src):
        self.arr = arr
        self.idx = idx
        self.src = src


class Print:
    def __init__(self, src):
        self.src = src
