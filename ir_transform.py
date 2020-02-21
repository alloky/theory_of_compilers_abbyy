import ir


def _replace_labels(ir_list, replacements):
    assert None not in replacements
    new_list = []
    for op in ir_list:
        if isinstance(op, ir.Jump):
            if op.label in replacements:
                op = op.modify(label=replacements[op.label])
        elif isinstance(op, (ir.CJumpLess, ir.CJumpBool)):
            if op.iftrue in replacements:
                op = op.modify(iftrue=replacements[op.iftrue])
            if op.iffalse in replacements:
                op = op.modify(iffalse=replacements[op.iffalse])
        new_list.append(op)
    return new_list


def remove_noop_jumps(ir_list, _):
    new_list = []
    last_label = None
    for op in reversed(ir_list):
        if last_label is not None:
            if isinstance(op, ir.Jump) and op.label == last_label:
                op = None
            elif isinstance(op, (ir.CJumpLess, ir.CJumpBool)):
                if op.iftrue == last_label:
                    op = op.modify(iftrue=None)
                if op.iffalse == last_label:
                    op = op.modify(iffalse=None)
                if op.iftrue is None and op.iffalse is None:
                    op = None
        if isinstance(op, ir.Label):
            last_label = op.label_id
        else:
            last_label = None
        if op is not None:
            new_list.append(op)
    return new_list[::-1]


def remove_unused_labels(ir_list, _):
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


def squash_sequential_labels(ir_list, _):
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
    return _replace_labels(new_list, replacements)


def remove_unused_locals(ir_list, _):
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


def remove_unused_instructions(ir_list, return_reg):
    used = {return_reg}
    for op in ir_list:
        used |= set(op.sources())
    new_list = []
    for op in ir_list:
        if op.side_effect_free and not (set(op.targets()) & set(used)):
            continue
        new_list.append(op)
    return new_list


def remove_immediate_jumps(ir_list, _):
    replacements = {}
    last_label = None
    for op in ir_list:
        if isinstance(op, ir.Jump):
            if last_label is not None:
                replacements[last_label] = op.label
        if isinstance(op, ir.Label):
            last_label = op.label_id
        else:
            last_label = None
    return _replace_labels(ir_list, replacements)


def remove_unreachable_code(ir_list, _):
    new_list = []
    reachable = True
    for op in ir_list:
        if isinstance(op, ir.Label):
            reachable = True
        if reachable:
            new_list.append(op)
        if isinstance(op, ir.Jump):
            reachable = False
    return new_list


TRANSFORMATIONS = [remove_noop_jumps, remove_unused_labels, squash_sequential_labels, remove_immediate_jumps,
                   remove_unused_locals, remove_unused_instructions, remove_unreachable_code]


def transform(ir_list, return_reg):
    while True:
        changed = False
        for t in TRANSFORMATIONS:
            new_list = t(ir_list, return_reg)
            if ir_list != new_list:
                ir_list = new_list
                changed = True
        if not changed:
            return ir_list
