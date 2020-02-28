from collections import deque
import ir


def _replace_labels(ir_list, replacements):
    assert None not in replacements
    visited = {}

    def dfs(v):
        visited[v] = 1
        if replacements[v] not in replacements or visited.get(replacements[v]) == 2:
            visited[v] = 2
            return False
        if visited.get(replacements[v]) == 1 or dfs(replacements[v]):
            del replacements[v]
            visited[v] = 2
            return True
        visited[v] = 2
        return False

    for i in list(replacements):
        if i in visited or i not in replacements:
            continue
        dfs(i)
    new_list = []
    for op in ir_list:
        if isinstance(op, ir.Jump):
            if op.label in replacements:
                op = op.modify(label=replacements[op.label])
            if op.label is None:
                op = None
        elif isinstance(op, (ir.CJumpLess, ir.CJumpBool)):
            if op.iftrue in replacements:
                op = op.modify(iftrue=replacements[op.iftrue])
            if op.iffalse in replacements:
                op = op.modify(iffalse=replacements[op.iffalse])
            if op.iftrue is None and op.iffalse is None:
                op = None
        if op is not None:
            new_list.append(op)
    return new_list


def _next_step_list(ir_list):
    label_pos = {l.label_id: i for i, l in enumerate(ir_list) if isinstance(l, ir.Label)}
    res = []
    for i, l in enumerate(ir_list):
        if isinstance(l, ir.Return):
            res.append(())
            continue
        if isinstance(l, ir.Jump):
            if l.label is None:
                res.append((i + 1,))
            else:
                res.append((label_pos[l.label],))
            continue
        if isinstance(l, (ir.CJumpLess, ir.CJumpBool)):
            if l.iftrue is None:
                t = {i + 1}
            else:
                t = {label_pos[l.iftrue]}
            if l.iffalse is None:
                t.add(i + 1)
            else:
                t.add(label_pos[l.iffalse])
            res.append(tuple(t))
            continue
        res.append((i + 1,))
    return res


def _is_op_consumed(source, target):
    if isinstance(source, ir.AssignLocal):
        return isinstance(target, (ir.AssignLocal, ir.Local)) and source.name == target.name
    if isinstance(source, ir.AssignParam):
        return isinstance(target, (ir.AssignParam, ir.Param)) and source.name == target.name
    return False


def _get_op_source(source, target):
    if isinstance(target, ir.Local):
        if isinstance(source, ir.AssignLocal) and source.name == target.name:
            return source.src
    if isinstance(target, ir.Param):
        if isinstance(source, ir.AssignParam) and source.name == target.name:
            return source.src
    assert False


def remove_noop_jumps(ir_list):
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
    return _replace_labels(new_list, replacements)


def remove_unused_instructions(ir_list):
    used = set()
    for op in ir_list:
        used |= {i for i in op.sources() if isinstance(i, int)}
    new_list = []
    for op in ir_list:
        if op.side_effect_free and not (set(op.targets()) & set(used)):
            continue
        new_list.append(op)
    return new_list


def remove_immediate_jumps(ir_list):
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


def remove_unreachable_code(ir_list):
    next_step = _next_step_list(ir_list)
    q = deque([0])
    reachable = {0}
    while q:
        x = q.popleft()
        for n in next_step[x]:
            if n not in reachable:
                reachable.add(n)
                q.append(n)
    return [l for i, l in enumerate(ir_list) if i in reachable]


def fold_constants(ir_list):
    new_list = []
    consts = {}
    for op in ir_list:
        if isinstance(op, ir.Const):
            consts[op.trg] = ir.Constexpr(op.value)
            new_list.append(op)
            continue
        sources = op.sources()
        new_sources = [consts.get(i, i) for i in sources]
        if sources != new_sources:
            op = op.set_sources(new_sources)
            if isinstance(op, ir.Const):
                consts[op.trg] = ir.Constexpr(op.value)
        new_list.append(op)
    return new_list


def remove_useless_writes(ir_list):
    next_step = _next_step_list(ir_list)
    new_list = []
    for i, op in enumerate(ir_list):
        if not isinstance(op, (ir.AssignParam, ir.AssignLocal)):
            new_list.append(op)
            continue
        q = deque([i])
        reachable = {i}
        found = False
        while q:
            x = q.popleft()
            for n in next_step[x]:
                if n not in reachable:
                    reachable.add(n)
                    if _is_op_consumed(op, ir_list[n]):
                        if not isinstance(ir_list[n], (ir.AssignParam, ir.AssignLocal)):
                            found = True
                            q.clear()
                            break
                    else:
                        q.append(n)
        if found:
            new_list.append(op)
    return new_list


def remove_constant_reads(ir_list):
    next_step = _next_step_list(ir_list)
    prev_step = [[] for i in ir_list]
    for i, n in enumerate(next_step):
        for j in n:
            prev_step[j].append(i)
    prev_step[0].append(-1)
    new_list = []
    for i, op in enumerate(ir_list):
        if not isinstance(op, (ir.Local, ir.Param)):
            new_list.append(op)
            continue
        q = deque([i])
        reachable = {i}
        sources = []
        while q:
            x = q.popleft()
            for n in prev_step[x]:
                if n not in reachable:
                    reachable.add(n)
                    if n == -1:
                        if isinstance(op, ir.Param):
                            src = 0
                        else:
                            continue  # uninitialized locals are UB
                    else:
                        src = _get_op_source(ir_list[n], op)

                    if src is not None:
                        sources.append(src)
                        if isinstance(src, int):
                            q.clear()
                            break
                    else:
                        q.append(n)
        if any(isinstance(i, int) for i in sources) or len({i.value for i in sources}) > 1:
            new_list.append(op)
        elif sources:
            new_list.append(ir.Const(sources.pop().value, op.trg))
        else:
            # uninitialized locals are UB
            new_list.append(ir.Const(0, op.trg))
    return new_list


def remove_reads_after_writes(ir_list):
    next_step = _next_step_list(ir_list)
    new_list = []
    skip = set()
    replacements = {}
    for i, op in enumerate(ir_list):
        if i in skip:
            continue
        sources = op.sources()
        if set(sources) & set(replacements):
            sources = [replacements.get(i, i) for i in sources]
            new_list.append(op.set_sources(sources))
            continue
        if not isinstance(op, (ir.AssignLocal, ir.AssignParam)):
            new_list.append(op)
            continue
        for j in range(i + 1, len(ir_list)):
            op2 = ir_list[j]
            if isinstance(op2, (ir.Jump, ir.CJumpLess, ir.CJumpBool, ir.Label, ir.New,
                                ir.NewArray, ir.Call, ir.Print, ir.Return)):
                new_list.append(op)
                break
            if type(op) is type(op2) and op.name == op2.name:
                new_list.append(op)
                break
            if not _is_op_consumed(op, op2):
                continue
            q = deque([j])
            reachable = {j}
            found = False
            while q:
                x = q.popleft()
                for n in next_step[x]:
                    if n not in reachable:
                        reachable.add(n)
                        if _is_op_consumed(op, ir_list[n]):
                            if not isinstance(ir_list[n], (ir.AssignParam, ir.AssignLocal)):
                                found = True
                                q.clear()
                                break
                        else:
                            q.append(n)
            if found:
                new_list.append(op)
                break
            skip.add(j)
            replacements[op2.trg] = op.src
            break
    return new_list


TRANSFORMATIONS = [remove_noop_jumps, remove_unused_labels, squash_sequential_labels, remove_immediate_jumps,
                   remove_unused_instructions, remove_unreachable_code, fold_constants,
                   remove_useless_writes, remove_constant_reads, remove_reads_after_writes]


def transform(ir_list):
    while True:
        changed = False
        for t in TRANSFORMATIONS:
            new_list = t(ir_list)
            if ir_list != new_list:
                ir_list = new_list
                changed = True
        if not changed:
            return ir_list
