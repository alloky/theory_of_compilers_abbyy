import constexpr_eval

EXPR = 0
COND = 1


def to_printable(node):
    return node.__class__.__name__ + ' ' + ' '.join(f'{k}={v}' for k, v in node.__dict__.items())


class Method:
    def __init__(self, statements):
        self.statements = statements

    def to_printable(self):
        return '\n'.join(map(to_printable, self.statements))


class Constexpr:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'Constexpr({self.value})'


class IROp:
    complexity = 0
    local = True
    reorderable = True
    side_effect_free = True

    def sources(self):
        return []

    def set_sources(self, sources):
        return self

    def targets(self):
        return []

    def set_targets(self, targets):
        return self

    def modify(self, **kwargs):
        assert set(kwargs) <= set(self.__dict__)
        args = {**self.__dict__, **kwargs}
        return type(self)(**args)

    def eval_constexpr(self):
        return self


class Const(IROp):
    def __init__(self, value, trg):
        self.value = value
        self.trg = trg

    def targets(self):
        return [self.trg]

    def set_targets(self, targets):
        return self.modify(trg=targets[0])


class BinOp(IROp):
    def __init__(self, op, lhs, rhs, trg):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
        self.trg = trg

    def sources(self):
        return [self.lhs, self.rhs]

    def set_sources(self, sources):
        if isinstance(sources[0], Constexpr) and isinstance(sources[1], Constexpr):
            evaluated = constexpr_eval.eval_binop(self.op, sources[0].value, sources[1].value)
            if evaluated is not None:
                return Const(evaluated, self.trg)
        return self.modify(lhs=sources[0], rhs=sources[1])

    def targets(self):
        return [self.trg]

    def set_targets(self, targets):
        return self.modify(trg=targets[0])

    complexity = 1


class Not(IROp):
    def __init__(self, arg, trg):
        self.arg = arg
        self.trg = trg

    def sources(self):
        return [self.arg]

    def set_sources(self, sources):
        if isinstance(sources[0], Constexpr):
            return Const(constexpr_eval.eval_not(sources[0].value), self.trg)
        return self.modify(arg=sources[0])

    def targets(self):
        return [self.trg]

    def set_targets(self, targets):
        return self.modify(trg=targets[0])


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

    def set_sources(self, sources):
        if isinstance(sources[0], Constexpr) and isinstance(sources[1], Constexpr):
            return Jump(self.iftrue if constexpr_eval.eval_less(sources[0].value, sources[1].value) else self.iffalse)
        return self.modify(lhs=sources[0], rhs=sources[1])

    side_effect_free = False


class CJumpBool(IROp):
    def __init__(self, val, iftrue, iffalse):
        self.val = val
        self.iftrue = iftrue
        self.iffalse = iffalse

    def sources(self):
        return [self.val]

    def set_sources(self, sources):
        if isinstance(sources[0], Constexpr):
            return Jump(self.iftrue if constexpr_eval.eval_bool(sources[0].value) else self.iffalse)
        return self.modify(val=sources[0])

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

    def set_targets(self, targets):
        return self.modify(trg=targets[0])

    complexity = 100


class NewArray(IROp):
    def __init__(self, size, trg):
        self.size = size
        self.trg = trg

    def sources(self):
        return [self.size]

    def set_sources(self, sources):
        return self.modify(size=sources[0])

    def targets(self):
        return [self.trg]

    def set_targets(self, targets):
        return self.modify(trg=targets[0])

    complexity = 100


class Index(IROp):
    def __init__(self, obj, idx, trg):
        self.obj = obj
        self.idx = idx
        self.trg = trg

    def sources(self):
        return [self.obj, self.idx]

    def set_sources(self, sources):
        return self.modify(obj=sources[0], idx=sources[1])

    def targets(self):
        return [self.trg]

    def set_targets(self, targets):
        return self.modify(trg=targets[0])

    local = False
    complexity = 1


class Length(IROp):
    def __init__(self, obj, trg):
        self.obj = obj
        self.trg = trg

    def sources(self):
        return [self.obj]

    def set_sources(self, sources):
        return self.modify(obj=sources[0])

    def targets(self):
        return [self.trg]

    def set_targets(self, targets):
        return self.modify(trg=targets[0])


class Call(IROp):
    def __init__(self, method, args, trg):
        self.method = method
        self.args = args
        self.trg = trg

    def sources(self):
        return self.args

    def set_sources(self, sources):
        return self.modify(args=sources)

    def targets(self):
        return [self.trg]

    def set_targets(self, targets):
        return self.modify(trg=targets[0])

    local = False
    side_effect_free = False
    complexity = 100


class Param(IROp):
    def __init__(self, name, trg):
        self.name = name
        self.trg = trg

    def targets(self):
        return [self.trg]

    def set_targets(self, targets):
        return self.modify(trg=targets[0])


class Local(IROp):
    def __init__(self, name, trg):
        self.name = name
        self.trg = trg

    def targets(self):
        return [self.trg]

    def set_targets(self, targets):
        return self.modify(trg=targets[0])


class Field(IROp):
    def __init__(self, cls, name, trg):
        self.cls = cls
        self.name = name
        self.trg = trg

    def targets(self):
        return [self.trg]

    def set_targets(self, targets):
        return self.modify(trg=targets[0])

    local = False


class AssignParam(IROp):
    def __init__(self, name, src):
        self.name = name
        self.src = src

    def sources(self):
        return [self.src]

    def set_sources(self, sources):
        return self.modify(src=sources[0])

    reorderable = False
    side_effect_free = False


class AssignLocal(IROp):
    def __init__(self, name, src):
        self.name = name
        self.src = src

    def sources(self):
        return [self.src]

    def set_sources(self, sources):
        return self.modify(src=sources[0])

    reorderable = False
    side_effect_free = False


class AssignField(IROp):
    def __init__(self, cls, name, src):
        self.cls = cls
        self.name = name
        self.src = src

    def sources(self):
        return [self.src]

    def set_sources(self, sources):
        return self.modify(src=sources[0])

    reorderable = False
    side_effect_free = False


class ArrayAssign(IROp):
    def __init__(self, arr, idx, src):
        self.arr = arr
        self.idx = idx
        self.src = src

    def sources(self):
        return [self.arr, self.idx, self.src]

    def set_sources(self, sources):
        return self.modify(arr=sources[0], idx=sources[1], src=sources[2])

    reorderable = False
    side_effect_free = False


class Print(IROp):
    def __init__(self, src):
        self.src = src

    def sources(self):
        return [self.src]

    def set_sources(self, sources):
        return self.modify(src=sources[0])

    reorderable = False
    side_effect_free = False


class Return(IROp):
    def __init__(self, src):
        self.src = src

    def sources(self):
        return [self.src]

    def set_sources(self, sources):
        return self.modify(src=sources[0])

    reorderable = False
    side_effect_free = False
