EXPR = 0
COND = 1


class Method:
    def __init__(self, statements, ret):
        self.statements = statements
        self.ret = ret


class Const:
    def __init__(self, rid, value):
        self.rid = rid
        self.value = value


class BinOp:
    def __init__(self, op, lhs, rhs, ret):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
        self.ret = ret


class Not:
    def __init__(self, arg, ret):
        self.arg = arg
        self.ret = ret


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
    def __init__(self, obj_type, ret):
        self.obj_type = obj_type
        self.ret = ret


class NewArray:
    def __init__(self, size, ret):
        self.size = size
        self.ret = ret


class Index:
    def __init__(self, obj, idx, ret):
        self.obj = obj
        self.idx = idx
        self.ret = ret


class Length:
    def __init__(self, obj, ret):
        self.obj = obj
        self.ret = ret


class Call:
    def __init__(self, method, args, ret):
        self.method = method
        self.args = args
        self.ret = ret
