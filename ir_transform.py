import ir


def remove_noop_jumps(ir_list):
    new_list = []
    last_label = None
    for op in reversed(ir_list):
        if last_label is not None:
            if isinstance(op, ir.Jump) and op.label == last_label:
                op = None
            elif isinstance(op, (ir.CJumpLess, ir.CJumpBool)):
                if op.iftrue == last_label:
                    op.iftrue = None
                if op.iffalse == last_label:
                    op.iffalse = None
                if op.iftrue is None and op.iffalse is None:
                    op = None
        if isinstance(op, ir.Label):
            last_label = op.label_id
        else:
            last_label = None
        if op is not None:
            new_list.append(op)
    return new_list[::-1]


def remove_unused_labels(ir_list):
    used = set()
    for op in ir_list:
        if isinstance(op, ir.Jump):
            used.add(op.label)
        elif isinstance(op, (ir.CJumpLess, ir.CJumpBool)):
            used.add(op.iftrue)
            used.add(op.iffalse)
    new_list = []
    for op in ir_list:
        if isinstance(op, ir.Label) and op.label_id not in used:
            continue
        new_list.append(op)
    return new_list


def squash_sequential_labels(ir_list):
    new_list = []
    last_label = None
    replacements = {}
    for op in ir_list:
        if isinstance(op, ir.Label):
            if last_label is not None:
                replacements[op.label_id] = last_label
                op = None
            else:
                last_label = op.label_id
        else:
            last_label = None
        if op is not None:
            new_list.append(op)
    for op in new_list:
        if isinstance(op, ir.Jump):
            if op.label in replacements:
                op.label = replacements[op.label]
        elif isinstance(op, (ir.CJumpLess, ir.CJumpBool)):
            if op.iftrue in replacements:
                op.iftrue = replacements[op.iftrue]
            if op.iffalse in replacements:
                op.iffalse = replacements[op.iffalse]
    return new_list


def remove_unused_locals(ir_list):
    used = set()
    for op in ir_list:
        if isinstance(op, (ir.Local, ir.Param)):
            used.add(op.name)
    new_list = []
    for op in ir_list:
        if isinstance(op, (ir.AssignLocal, ir.AssignParam)) and op.name not in used:
            continue
        new_list.append(op)
    return new_list


TRANSFORMATIONS = [remove_noop_jumps, remove_unused_labels, squash_sequential_labels, remove_unused_locals]


def transform(ir_list):
    while True:
        changed = False
        for t in TRANSFORMATIONS:
            new_list = t(ir_list)
            if new_list != ir_list:
                # TODO возвращать changed явно
                ir_list = new_list
                changed = True
        if not changed:
            return ir_list
