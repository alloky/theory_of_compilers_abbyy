import ir


class LocalVar:
    def __init__(self, inreg, num):
        self.num = num
        self.inReg = inreg


class AsmMethod:

    def __init__(self, params, local_vars, method_name):
        self.params = list(params)
        self.local = local_vars
        self.method_name = method_name
        self.statements = []    
    
    def add_statement(self, stm):
        self.statements.append(stm)

    def __str__(self):
        body = [str(stm) for stm in self.statements]
        return self.get_prologue() + '\n' + '\n'.join(body) + '\n' + self.get_epilogue()

    def get_prologue(self):
        return f"{self.method_name}:\n"\
               "push ebp\n" \
               "mov ebp, esp"

    def get_epilogue(self):
        return "mov esp, ebp\n"\
                "pop ebp\n"\
                "ret"


class AsmStatement3:
    def __init__(self, cmd, src, dst):
        self.cmd = cmd
        self.src = src
        self.dst = dst

    def __str__(self):
        return "{} {}, {}".format(self.cmd, self.src, self.dst)


class AsmStatement2:
    def __init__(self, cmd, src):
        self.cmd = cmd
        self.src = src

    def __str__(self):
        return "{} {}".format(self.cmd, self.src)


class AsmPrint:
    def __init__(self, src):
        self.src = src

    def __str__(self):
        # TODO : call print
        return "{} {}".format("print", self.src)


class X86Assembler:
    need_malloc = False

    def binop_to_asm(self, expr, new_ir_m, local_sym_table, temp_vars, var_name):
        var_name = self.make_assign_expr(expr.lhs, new_ir_m, local_sym_table, temp_vars, var_name)
        right = self.make_assign_expr(expr.rhs, new_ir_m, local_sym_table, temp_vars)
        if expr.op == '+':
            new_ir_m.statements.append(AsmStatement3("add", var_name, right))
        elif expr.op == '-':
            new_ir_m.statements.append(AsmStatement3("sub", var_name, right))
        elif expr.op == '*':
            new_ir_m.statements.append(AsmStatement3("mov", "al", var_name))
            new_ir_m.statements.append(AsmStatement2("imul", right))
            new_ir_m.statements.append(AsmStatement3("mov", var_name, "al"))
        elif expr.op == '/':
            new_ir_m.statements.append(AsmStatement3("mov", "ax", var_name))
            new_ir_m.statements.append(AsmStatement2("idiv", right))
            new_ir_m.statements.append(AsmStatement3("mov", var_name, "al"))
        elif expr.op == '%':
            new_ir_m.statements.append(AsmStatement3("mov", "ax", var_name))
            new_ir_m.statements.append(AsmStatement2("idiv", right))
            new_ir_m.statements.append(AsmStatement3("mov", var_name, "ah"))
        else:
            print("Error: unknown operation:" + expr.op)
            exit(0)
        return var_name

    def make_assign_expr(self, statement, new_ir_m, local_sym_table, temp_vars, var_name=None):
        new_var = False
        if not var_name:
            idx = len(local_sym_table)
            var_name = "var_" + str(idx)
            local_sym_table[var_name] = idx
            new_var = True

        if isinstance(statement, ir.Constexpr):
            new_ir_m.statements.append(AsmStatement3("mov", var_name, str(statement.value)))
            return var_name

        if isinstance(statement, int):
            st = temp_vars[statement]
            if isinstance(st, ir.NewArray):
                self.need_malloc = True
                new_ir_m.statements.append(AsmStatement3("mov", "edi", "4*" + str(st.size.value) + "+4"))
                new_ir_m.statements.append(AsmStatement2("call", "malloc"))
                new_ir_m.statements.append(AsmStatement3("mov", var_name, str(st.size.value)))
                new_ir_m.statements.append(AsmStatement3("mov", "[ax]", var_name))
                new_ir_m.statements.append(AsmStatement3("mov", var_name, "ax"))
                temp_vars[statement] = var_name

            if isinstance(st, ir.BinOp):
                var_name = self.binop_to_asm(st, new_ir_m, local_sym_table, temp_vars, var_name)
                temp_vars[statement] = var_name

            if isinstance(st, ir.Length):
                if not (st.obj in temp_vars) or (not isinstance(temp_vars[st.obj], str)):
                    print("Error: array " + str(st.obj) + "does not exist")
                    exit(0)
                new_ir_m.statements.append(AsmStatement3("mov", var_name, "[" + temp_vars[st.obj] + "]"))
                temp_vars[statement] = var_name

            if isinstance(st, str):
                if new_var:
                    local_sym_table.pop(var_name)
                var_name = st

        return var_name

    def ir_to_asm(self, ir_tree, sym_table):
        """
        ir - linear statement representation
        """

        new_labels_counter = 0

        new_ir = dict()

        temp_vars = {}  # Indices of temp vars in ir
        
        for method in ir_tree:
            if method == 'main':
                pass
                # TODO entry point
            else:
                class_name, class_method = method.split('.')
                local_vars = []

                for statement in ir_tree[method].statements:
                    if isinstance(statement, ir.Local):
                        local_vars.append(statement)

                new_ir[method] = AsmMethod(sym_table[class_name].methods[class_method].params, local_vars, method)

                local_sym_table = dict()
                for idx, key in enumerate(sym_table[class_name].methods[class_method].params):
                    local_sym_table[key] = idx

                for idx, key in enumerate(sym_table[class_name].methods[class_method].vars,
                                          start=len(local_sym_table.keys())):
                    local_sym_table[key] = idx

                for statement in ir_tree[method].statements:
                    if isinstance(statement, ir.Call):
                        new_ir[method].statements.append("#save_locals")
                        for idx, param in enumerate(statement.args[:4]):
                            new_ir[method].statements.append(AsmStatement3("mov", f"r{idx}", param))
                        for idx, param in enumerate(statement.args[4:]):
                            new_ir[method].statements.append(AsmStatement2("push", param))
                        new_ir[method].statements.append(AsmStatement2("call", statement.method))
                        new_ir[method].statements.append(f"#call_trg {statement.trg}")

                    if isinstance(statement, ir.Label):
                        if statement.local:
                            new_ir[method].statements.append(f"{class_name}_{class_method}_label_{statement.label_id}:")
                        else:
                            new_ir[method].statements.append(f"GLOBAL_label_{statement.label_id}:")

                    if isinstance(statement, ir.Print):
                        new_ir[method].statements.append(AsmPrint(statement.src))

                    if isinstance(statement, ir.Jump):
                        if statement.local:
                            new_ir[method].statements.append(AsmStatement2(
                                "jmp", f"{class_name}_{class_method}_label_{statement.label}"))
                        else:
                            new_ir[method].statements.append(AsmStatement2("jmp", f"GLOBAL_label_{statement.label}"))

                    if isinstance(statement, ir.CJumpLess):
                        left = self.make_assign_expr(statement.lhs, new_ir[method], local_sym_table, temp_vars)
                        right = self.make_assign_expr(statement.rhs, new_ir[method], local_sym_table, temp_vars)
                        new_ir[method].statements.append(AsmStatement3("cmp", left, right))
                        if statement.local:
                            if statement.iffalse:
                                new_ir[method].statements.append(
                                    AsmStatement2("jl", f"{class_name}_{class_method}_label_{statement.iffalse}"))
                            if statement.iftrue:
                                new_ir[method].statements.append(
                                    AsmStatement2("jge", f"{class_name}_{class_method}_label_{statement.iftrue}"))
                        else:
                            if statement.iffalse:
                                new_ir[method].statements.append(AsmStatement2(
                                    "jl", f"GLOBAL_label_{statement.iffalse}"))
                            if statement.iftrue:
                                new_ir[method].statements.append(AsmStatement2(
                                    "jge", f"GLOBAL_label_{statement.iftrue}"))

                    if isinstance(statement, ir.CJumpBool):
                        val = self.make_assign_expr(statement.val, new_ir[method], local_sym_table, temp_vars)
                        new_ir[method].statements.append(AsmStatement3("mov", "dx", "0"))
                        new_ir[method].statements.append(AsmStatement3("cmp", val, "dx"))
                        if statement.local:
                            if statement.iffalse:
                                new_ir[method].statements.append(
                                    AsmStatement2("jne", f"{class_name}_{class_method}_label_{statement.iffalse}"))
                            if statement.iftrue:
                                new_ir[method].statements.append(
                                    AsmStatement2("jne", f"{class_name}_{class_method}_label_{statement.iftrue}"))
                        else:
                            if statement.iffalse:
                                new_ir[method].statements.append(AsmStatement2(
                                    "jne", f"GLOBAL_label_{statement.iffalse}"))
                            if statement.iftrue:
                                new_ir[method].statements.append(AsmStatement2(
                                    "jne", f"GLOBAL_label_{statement.iftrue}"))

                    if isinstance(statement, ir.NewArray):
                        temp_vars[statement.trg] = statement

                    if isinstance(statement, ir.AssignLocal):
                        self.make_assign_expr(statement.src, new_ir[method], local_sym_table, temp_vars, statement.name)

                    if isinstance(statement, ir.Local):
                        temp_vars[statement.trg] = statement.name

                    if isinstance(statement, ir.ArrayAssign):
                        if not (statement.arr in temp_vars):
                            print("Error: array " + str(statement.arr) + " does not exist")
                            exit(0)
                        idx = self.make_assign_expr(statement.idx.src, new_ir[method], local_sym_table, temp_vars)
                        src = self.make_assign_expr(statement.idx.src, new_ir[method], local_sym_table, temp_vars)
                        new_ir[method].statements.append(AsmStatement3("mov", "[" + str(temp_vars[statement.arr]) +
                                                                       "+4*" + str(idx) + "+4]", src))

                    if isinstance(statement, ir.BinOp):
                        temp_vars[statement.trg] = statement

                    if isinstance(statement, ir.Index):
                        idx = len(local_sym_table)
                        var_name = "var_" + str(idx)
                        local_sym_table[var_name] = idx
                        new_ir[method].statements.append(AsmStatement3(
                            "mov", var_name, "[" + str(temp_vars[statement.obj]) + "+4*" + str(statement.idx) + "+4]"))
                        temp_vars[statement.trg] = var_name

                    if isinstance(statement, ir.Length):
                        if not (statement.obj in temp_vars):
                            print("Error: array " + str(statement.obj) + " does not exist")
                            exit(0)
                        temp_vars[statement.trg] = statement

                    if isinstance(statement, ir.Not):
                        temp_vars[statement.trg] = temp_vars[statement.arg]
                        new_ir[method].statements.append(AsmStatement3("mov", "dx", "0"))
                        new_ir[method].statements.append(AsmStatement3("cmp", temp_vars[statement.arg], "dx"))
                        lab_1, lab_2 = new_labels_counter, new_labels_counter + 1
                        new_labels_counter += 2
                        new_ir[method].statements.append(AsmStatement2(
                            "je", f"{class_name}_{class_method}_label_not_{lab_1}:"))
                        new_ir[method].statements.append(AsmStatement3("mov", temp_vars[statement.arg], "0"))
                        new_ir[method].statements.append(AsmStatement2(
                            "jmp", f"{class_name}_{class_method}_label_not_{lab_2}:"))
                        new_ir[method].statements.append(f"{class_name}_{class_method}_label_not_{lab_2}:")
                        new_ir[method].statements.append(AsmStatement3("mov", temp_vars[statement.arg], "1"))
                        new_ir[method].statements.append(f"{class_name}_{class_method}_label_not_{lab_1}:")

                    if isinstance(statement, ir.Return):
                        new_ir[method].statements.append(AsmStatement3("mov", "eax", str(self.make_assign_expr(
                            statement.src, new_ir[method], local_sym_table, temp_vars))))

        return new_ir
