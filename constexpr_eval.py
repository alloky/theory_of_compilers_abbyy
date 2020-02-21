INT_BITS = 32

def is_mj_int(arg):
    return (-2 ** (INT_BITS - 1)) <= arg <= (2 ** (INT_BITS - 1) - 1)


def to_mj_int(arg):
    arg &= (2 ** INT_BITS - 1)
    if arg >= 2 ** (INT_BITS - 1):
        arg -= 2 ** INT_BITS
    return arg


def eval_binop(op, lhs, rhs):
    # signed overflow is UB, so we don't care much
    if op == '+':
        return to_mj_int(lhs + rhs)
    if op == '-':
        return to_mj_int(lhs - rhs)
    if op == '*':
        return to_mj_int(lhs * rhs)
    if op == '%':
        if lhs < 0 or rhs <= 0:
            return None  # let's do it in runtime
        return to_mj_int(lhs % rhs)
    if op == '<':
        return int(lhs < rhs)
    assert False

def eval_not(arg):
    return int(not arg)


def eval_less(lhs, rhs):
    return lhs < rhs


def eval_bool(arg):
    return arg != 0
