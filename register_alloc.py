from typing import List, Set, Any, Dict

import ir
from x86asm import AsmStatement2, AsmStatement3


class TimeGraphNode:

    def __init__(self):
        self.defs = set()
        self.uses = set()

        self.live_in = set()
        self.live_out = set()

        self.succ = list()
        self.pred = list()

    statement = None


def build_time_graph_from_method(method):
    start_node = None
    prev_node = None
    node_list = list()

    local_jump_table = dict()
    last_label = None
    defined = set()

    for statement in method.statements:
        cur_node = TimeGraphNode()
        cur_node.statement = statement
        if start_node is None:
            start_node = cur_node
        node_list.append(cur_node)
        cur_node.pred.append(prev_node)

        if isinstance(statement, str):
            if statement[0] != ";":
                local_jump_table[statement[:-1]] = None
                last_label = statement[:-1]
        else:
            if last_label is not None:
                local_jump_table[last_label] = cur_node
                last_label = None

        prev_node = cur_node

    for cur_node in node_list:
        statement = cur_node.statement
        if isinstance(statement, AsmStatement2):
            if statement.cmd == "jmp":
                cur_node.succ.append(local_jump_table[statement.src])
        if isinstance(statement, AsmStatement3):
            if statement.src not in defined:
                cur_node.defs.add(statement.src)
                defined.add(statement.src)
            else:
                cur_node.uses.add(statement.src)

            if statement.dst not in defined:
                cur_node.defs.add(statement.dst)
                defined.add(statement.dst)
            else:
                cur_node.uses.add(statement.dst)

            if statement.cmd == "mov":
                cur_node.is_move = True


    was_changes = True
    while was_changes:
        was_changes = False
        for node in node_list:
            new_live_in = set()
            new_live_in.union(node.uses)
            new_live_in.union({x for x in node.live_out if x not in node.defs})
            if node.live_in != new_live_in:
                was_changes = True
            node.live_in = new_live_in

            new_live_out = set()
            for s in node.succ:
                new_live_out.union(s.live_in)
            if node.live_out != new_live_out:
                was_changes = True
            node.live_out = new_live_out

    return node_list


def build_time_graph(asm_code):
    time_graph = dict()
    for method in asm_code.keys():
        local_graph = build_time_graph_from_method(asm_code[method])
        time_graph[method] = local_graph
    return time_graph

class DependecyNode:
    variable_name = ""

    def __init__(self):
        self.next = set()
        self.move_next = set()


def build_local_dependency_graph(local_time_graph: List[TimeGraphNode]):
    var_nodes = dict()
    for node in local_time_graph:
        for var in node.defs:
            if var not in var_nodes:
                var_nodes[var] = DependecyNode()

        if isinstance(node.statement, ir.Local):
            if node.statement.name not in var_nodes:
                var_nodes[node.statement.name] = DependecyNode()
            if node.statement.trg not in var_nodes:
                var_nodes[node.statement.trg] = DependecyNode()

            cur_node = var_nodes[node.statement.name]

            cur_node.move_next.add(node.statement.trg)
            var_nodes[node.statement.trg].move_next.add(node.statement.name)

            for n in node.live_out:
                if n != node.statement.trg:
                    if n != node.statement.name:
                        cur_node.next.add(n)
                        var_nodes[n].next.add(node.statement.name)

        elif isinstance(node.statement, ir.Local):
            if node.statement.name not in var_nodes:
                var_nodes[node.statement.name] = DependecyNode()
            if node.statement.trg not in var_nodes:
                var_nodes[node.statement.trg] = DependecyNode()

            cur_node = var_nodes[node.statement.name]

            cur_node.move_next.add(node.statement.trg)
            var_nodes[node.statement.trg].move_next.add(node.statement.name)

            for n in node.live_out:
                if n != node.statement.trg:
                    if n != node.statement.name:
                        cur_node.next.add(n)
                        var_nodes[n].next.add(node.statement.name)

        else:
            for cur_node in node.defs:
                for n in node.live_out:
                    if n != cur_node:
                        var_nodes[cur_node].next.add(n)
                        var_nodes[n].next.add(cur_node)

    return var_nodes


def build_dependency_graph(time_graph):
    dependency_graph = dict()
    for method in time_graph.keys():
        local_dependency_graph = build_local_dependency_graph(time_graph[method])
        dependency_graph[method] = local_dependency_graph
    return dependency_graph

def build_time_graph_from_ir_method(method):
    start_node = None
    prev_node = None
    node_list = list()

    local_jump_table = dict()
    last_label = None
    defined = set()

    for statement in method.statements:
        cur_node = TimeGraphNode()

        cur_node.statement = statement
        if start_node is None:
            start_node = cur_node
        node_list.append(cur_node)

        cur_node.pred.append(prev_node)
        if prev_node is not None:
            prev_node.succ.append(cur_node)

        if isinstance(statement, ir.Label):
            local_jump_table[statement.label_id] = None
            last_label = statement.label_id
        else:
            if last_label is not None:
                local_jump_table[last_label] = cur_node
                last_label = None

        prev_node = cur_node

    print()

    def is_not_const(x):
        return not (isinstance(x, ir.Const) or isinstance(x, ir.Constexpr) or x is None)

    for cur_node in node_list:
        statement = cur_node.statement
        if isinstance(statement, ir.Jump):
            cur_node.succ.append(local_jump_table[statement.label])
        if isinstance(statement, ir.CJumpLess) or isinstance(statement, ir.CJumpBool):
            if statement.iffalse is not None:
                cur_node.succ.append(local_jump_table[statement.iffalse])
            if statement.iftrue is not None:
                cur_node.succ.append(local_jump_table[statement.iftrue])

        if isinstance(statement, ir.CJumpLess):
            if is_not_const(statement.lhs):
                cur_node.uses.add(statement.lhs)
            if is_not_const(statement.rhs):
                cur_node.uses.add(statement.rhs)

        if isinstance(statement, ir.Local):
            cur_node.uses.add(statement.name)
            cur_node.defs.add(statement.trg)

        if isinstance(statement, ir.AssignLocal):
            if statement.name not in defined:
                cur_node.defs.add(statement.name)
                defined.add(statement.name)
            else:
                cur_node.uses.add(statement.name)

            if is_not_const(statement.src):
                cur_node.uses.add(statement.src)

        if isinstance(statement, ir.BinOp):
            if statement.trg not in defined:
                cur_node.defs.add(statement.trg)
                defined.add(statement.trg)
            else:
                cur_node.uses.add(statement.trg)

            if is_not_const(statement.lhs):
                cur_node.uses.add(statement.lhs)
            if is_not_const(statement.rhs):
                cur_node.uses.add(statement.rhs)

        if isinstance(statement, ir.Return):
            if is_not_const(statement.src):
                cur_node.uses.add(statement.src)

        if isinstance(statement, ir.Call):
            if is_not_const(statement.trg):
                cur_node.defs.add(statement.trg)

        if isinstance(statement, ir.Index):
            cur_node.defs.add(statement.trg)
            if is_not_const(statement.idx):
                cur_node.uses.add(statement.idx)

        if isinstance(statement, ir.Not):
            cur_node.defs.add(statement.trg)
            if is_not_const(statement.arg):
                cur_node.uses.add(statement.arg)

        if isinstance(statement, ir.New):
            cur_node.defs.add(statement.trg)

        if isinstance(statement, ir.AssignParam):
            if is_not_const(statement.src):
                cur_node.uses.add(statement.src)

        if isinstance(statement, ir.AssignField):
            cur_node.uses.add(statement.this)
            if is_not_const(statement.src):
                cur_node.uses.add(statement.src)

        if isinstance(statement, ir.ArrayAssign):
            if is_not_const(statement.src):
                cur_node.uses.add(statement.src)
            if is_not_const(statement.idx):
                cur_node.uses.add(statement.idx)
            cur_node.uses.add(statement.arr)

        if isinstance(statement, ir.Print):
            if is_not_const(statement.src):
                cur_node.uses.add(statement.src)

    was_changes = True
    while was_changes:
        was_changes = False
        for node in node_list:
            new_live_in = set()
            new_live_in = new_live_in.union(node.uses)
            new_live_in = new_live_in.union({x for x in node.live_out if x not in node.defs})
            if node.live_in != new_live_in:
                was_changes = True
            node.live_in = new_live_in

            new_live_out = set()
            for s in node.succ:
                new_live_out = new_live_out.union(s.live_in)
            if node.live_out != new_live_out:
                was_changes = True
            node.live_out = new_live_out

    return node_list


def build_time_graph_from_ir(ir_code):
    time_graph = dict()
    for method in ir_code.keys():
        local_time_graph = build_time_graph_from_ir_method(ir_code[method])
        time_graph[method] = local_time_graph
    return time_graph


class ColoringScope:
    spilledNodes: Set[str]
    coalescedNodes: Set[str]
    colored_nodes: Set[str]
    K = 6

    precolored = ["eax", "ebx", "ecx", "edx", "edi", "esi"]

    def __init__(self, dep_graph: Dict[str, DependecyNode]):
        self.coloring = dict()
        self.coloring["eax"] = 0
        self.coloring["ebx"] = 1
        self.coloring["ecx"] = 2
        self.coloring["edx"] = 3
        self.coloring["edi"] = 4
        self.coloring["esi"] = 5

        self.initial = set()

        self.simplifyList = list()
        self.moveList = dict()
        self.freezeList = list()
        self.spillList = list()

        self.wroklistMoves = list()
        self.activeMoves = list()
        self.coalescedMoves = list()
        self.frozenMoves = set()

        self.dep_graph = dep_graph
        self.virtual_var_cnt = len(dep_graph.keys())

        self.selectStack = list()
        self.coalescedNodes = set()
        self.spilledNodes = set()
        self.colored_nodes = set()

        self.adjSet = set()

        self.degree = dict()
        self.alias = dict()

        for n in dep_graph.keys():
            self.initial.add(n)
            self.degree[n] = len(dep_graph[n].next)

        self.make_lists()

    def has_actions(self):
        return (len(self.simplifyList) + len(self.moveList) + len(self.freezeList) + len(self.spillList)) > 0

    def not_colored(self):
        return not (len(self.coloring.keys()) == (self.virtual_var_cnt + 6))

    def make_lists(self):
        for n in self.initial:
            if self.degree[n] >= self.K:
                self.spillList.append(n)
            elif self.move_related(n):
                self.freezeList.append(n)
            else:
                self.simplifyList.append(n)
        self.initial = set()

    def add_edge(self, u, v):
        if (u, v) in self.adjSet and u != v:
            self.adjSet.add((u, v))
            self.adjSet.add((v, u))
            if u not in self.precolored:
                self.dep_graph[u].next.add(v)
                self.degree[u] += 1
            if v not in self.precolored:
                self.dep_graph[v].next.add(u)
                self.degree[v] += 1

    def adjacent(self, n):
        new_set = set(self.selectStack)
        new_set = new_set.union(self.coalescedNodes)
        new_set = {n for n in self.dep_graph[n].next if n not in new_set}
        return new_set

    def node_moves(self, n):
        return set(self.dep_graph[n].move_next).intersection(set(self.activeMoves).union(self.wroklistMoves))

    def move_related(self, n):
        return len(self.node_moves(n)) > 0

    def simplify(self):
        sim_candidate = self.simplifyList.pop()
        self.selectStack.append(sim_candidate)
        for n in self.dep_graph[sim_candidate].next:
            self.dec_degree(n)

    def dec_degree(self, n):
        self.degree[n] -= 1
        if self.degree[n] == self.K:
            self.enable_moves(set(n).union(self.adjacent(n)))
            self.simplifyList.remove(n)
            if self.move_related(n):
                self.freezeList.append(n)
            else:
                self.simplifyList.append(n)

    def enable_moves(self, nodes):
        for n in nodes:
            for m in self.node_moves(n):
                if m in self.activeMoves:
                    self.activeMoves.remove(m)
                    self.wroklistMoves.append(m)

    def add_worklist(self, n):
        if n not in self.precolored and not(self.move_related(n) and self.degree[n] < self.K):
            self.freezeList.remove(n)
            self.simplifyList.append(n)

    def is_ok(self, n, r):
        return (self.degree[n] < self.K) and (n, r) in self.adjSet

    def conservative(self, nodes):
        k = 0
        for n in nodes:
            if self.degree[n] >= self.K:
                k += 1
        return k < self.K

    def get_alias(self, n):
        if n in self.coalescedNodes:
            return self.get_alias(self.alias[n])
        else:
            return n

    def coalsese(self):
        x, y = self.wroklistMoves.pop()
        x_old, y_old = x, y
        x = self.get_alias(x)
        y = self.get_alias(y)
        u, v = x, y
        if y in self.precolored:
            u, v = y, x
        if u == v:
            self.coalescedMoves.append((x_old, y_old))
            self.add_worklist(u)
        elif v in self.precolored and (u, v) in self.adjSet:
            self.coalescedMoves.append((x_old, y_old))
            self.add_worklist(u)
            self.add_worklist(v)
        elif u in self.precolored and all([self.is_ok(t, u) for t in self.adjacent(v)]):
            self.coalescedMoves.append((x_old, y_old))
            self.combine(u, v)
            self.add_worklist(u)
        elif u not in self.precolored and self.conservative(set(self.adjacent(u)).union(set(self.adjacent(v)))):
            self.coalescedMoves.append((x_old, y_old))
            self.combine(u, v)
            self.add_worklist(u)
        else:
            self.activeMoves.append((x_old, y_old))

    def combine(self, u, v):
        if v in self.freezeList:
            self.freezeList.remove(v)
        elif v in self.spillList:
            self.spillList.remove(v)
        self.coalescedNodes.add(v)
        self.alias[v] = u
        self.dep_graph[u].move_next = self.dep_graph[u].move_next.union(self.dep_graph[v].move_next)
        self.enable_moves([v])
        for t in self.adjacent(v):
            self.add_edge(t, u)
            self.dec_degree(t)
        if self.degree[u] >= self.K and u in self.freezeList:
            self.freezeList.remove(u)
            self.spillList.append(u)

    def freeze(self):
        u = self.freezeList.pop()
        self.simplifyList.append(u)
        self.freeze_moves(u)

    def freeze_moves(self, u):
        for (x, y) in self.node_moves(u):
            v = None
            if self.get_alias(y) == self.get_alias(u):
                v = self.get_alias(x)
            else:
                v = self.get_alias(y)

            self.activeMoves.remove((x, y))
            self.frozenMoves.add((x, y))

            if v in self.freezeList and len(self.node_moves(v)) == 0:
                self.freezeList.remove(v)
                self.simplifyList.append(v)

    def select_spill(self):
        m = max(self.spillList, key=lambda n: self.degree[n])
        self.spillList.remove(m)
        self.simplifyList.append(m)
        self.freeze_moves(m)

    def assign_colors(self):
        while len(self.selectStack) > 0:
            n = self.selectStack.pop()
            okColors = {k for k in range(self.K)}
            for w in self.dep_graph[n].next:
                w_alias = self.get_alias(w)
                if w_alias in self.colored_nodes or w_alias in self.precolored:
                    if self.coloring[w_alias] in okColors:
                        okColors.remove(self.coloring[w_alias])
            if len(okColors) == 0:
                self.spilledNodes.add(n)
            else:
                self.colored_nodes.add(n)
                c = okColors.pop()
                self.coloring[n] = c
        for n in self.coalescedNodes:
            self.coloring[n] = self.coloring[self.get_alias(n)]

    def rewrite_ir(self, ir_code, time_graph):
        newTemps = set()
        for v in self.spilledNodes:
            def_cnt = 0
            use_cnt = 0
            ir_idx = 0
            for idx, node in enumerate(time_graph):
                if v in node.defs:
                    new_name = v + "/def" + str(def_cnt)
                    ir_code = ir_code[:ir_idx + 1] + [ir.Store(v)] + ir_code[(ir_idx + 1):]
                    def_cnt += 1
                    ir_idx += 1
                if v in node.uses:
                    new_name = v + "/def" + str(use_cnt)
                    newTemps.add(new_name)
                    if hasattr(ir_code[ir_idx], "src"):
                        if ir_code[ir_idx].src == v:
                            ir_code[ir_idx].src = new_name
                    elif hasattr(ir_code[ir_idx], "name"):
                        if ir_code[ir_idx].name == v:
                            ir_code[ir_idx].name = new_name
                    elif hasattr(ir_code[ir_idx], "lhs"):
                        if ir_code[ir_idx].lhs == v:
                            ir_code[ir_idx].lhs = new_name
                    elif hasattr(ir_code[ir_idx], "rhs"):
                        if ir_code[ir_idx].rhs == v:
                            ir_code[ir_idx].rhs = new_name
                    elif hasattr(ir_code[ir_idx], "obj"):
                        if ir_code[ir_idx].obj == v:
                            ir_code[ir_idx].obj = new_name
                    elif hasattr(ir_code[ir_idx], "idx"):
                        if ir_code[ir_idx].idx == v:
                            ir_code[ir_idx].idx = new_name

                    ir_code = ir_code[:ir_idx] + [ir.Fetch(new_name)] + ir_code[(ir_idx+1):]
                    ir_idx += 1
                    use_cnt += 1
                ir_idx += 1
        self.spilledNodes = set()
        self.initial = self.initial.union(self.colored_nodes)
        self.initial = self.initial.union(self.coalescedNodes)
        self.initial = self.initial.union(newTemps)
        self.colored_nodes = set()
        self.coalescedNodes = set()

        return ir_code


def color_variables(ir_all):
    code_coloring = dict()
    for method in ir_all.keys():
        ir_code = ir_all[method]

        tg = build_time_graph_from_ir_method(ir_code)
        dep_graph = build_local_dependency_graph(tg)

        cScope = ColoringScope(dep_graph)
        new_ir_code = ir_code

        while cScope.not_colored():

            tg = build_time_graph_from_ir_method(ir_code)
            dep_graph = build_local_dependency_graph(tg)
            cScope.dep_graph = dep_graph

            while cScope.has_actions():
                if len(cScope.simplifyList) != 0:
                    cScope.simplify()
                elif len(cScope.moveList) != 0:
                    cScope.coalsese()
                elif len(cScope.freezeList) != 0:
                    cScope.freeze()
                elif len(cScope.spillList) != 0:
                    cScope.select_spill()

            cScope.assign_colors()
            if len(cScope.spilledNodes) > 0:
                new_ir_code = cScope.rewrite_ir(tg, ir_code)

        code_coloring[method] = cScope

    return code_coloring

