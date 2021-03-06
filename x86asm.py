import ir


class LocalVar:
    def __init__(self, inreg, num):
        self.num = num
        self.inReg = inreg


class AsmMain:

    def __init__(self):
        self.method_name = 'main'
        self.statements = []

    def add_statement(self, stm):
        self.statements.append(stm)

    def __str__(self):
        body = [str(stm) for stm in self.statements]
        return self.get_prologue() + '\n' + '\n'.join(body) + '\n' + self.get_epilogue()

    def get_prologue(self):
        return f"{self.method_name.replace('.', '_')}:\n" \
            "start:\n" \
            ".386"

    def get_epilogue(self):
        return "mov ah, 4c00h\n"\
               "int 21h\n"\
               "end start"


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
        return f"{self.method_name.replace('.', '_')}:\n" \
            "push ebp\n" \
            "mov ebp, esp"

    def get_epilogue(self):
        return "mov esp, ebp\n" \
               "pop ebp\n" \
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


class LocationOfClasses:
    def __init__(self):
        self.classes = {}

    def count_memory(self, class_name, sym_table):
        if class_name in self.classes:
            return self.classes[class_name]['TOTAL']

        res = 4
        self.classes[class_name] = {}
        fields = sym_table[class_name].fields
        for field in fields:
            self.classes[class_name][field] = res
            if fields[field] == 'int' or fields[field] == 'int[]':
                res += 4
            elif fields[field] == 'boolean':
                res += 1
            else:
                res += 4

        self.classes[class_name]['TOTAL'] = res
        return res

    def get_memory_count(self, class_name):
        return self.classes[class_name]['TOTAL']

    def find_offset(self, class_name, field_name):
        return self.classes[class_name][field_name]


class X86Assembler:
    def __init__(self, symbol_table):
        self.need_malloc = False
        self.sym_table = symbol_table
        self.location_of_classes = LocationOfClasses()
        for cls in symbol_table:
            self.location_of_classes.count_memory(cls, self.sym_table)

    def binop_to_asm(self, expr, new_ir_m, local_sym_table, temp_vars, allocated_memory, var_name):
        var_name = self.make_assign_expr(expr.lhs, new_ir_m, local_sym_table, temp_vars, allocated_memory, var_name)
        right = self.make_assign_expr(expr.rhs, new_ir_m, local_sym_table, temp_vars, allocated_memory)
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

    def make_assign_expr_or_const(self, statement, new_ir_m, local_sym_table, temp_vars, allocated_memory, var_name=None):
        if hasattr(statement, 'src'):
            return self.make_assign_expr(statement.src, new_ir_m, local_sym_table, temp_vars, allocated_memory, var_name)
        else:
            return self.make_assign_expr(statement, new_ir_m, local_sym_table, temp_vars, allocated_memory, var_name)

    def make_assign_expr(self, statement, new_ir_m, local_sym_table, temp_vars, allocated_memory, var_name=None):
        new_var = False
        if not var_name:
            idx = len(local_sym_table)
            var_name = "asm_var_" + str(idx)
            local_sym_table[var_name] = idx
            new_var = True
        elif var_name in local_sym_table:
            var_name = "asm_var_" + str(local_sym_table[var_name])
        else:
            idx = len(local_sym_table)
            local_sym_table[var_name] = idx
            var_name = "asm_var_" + str(idx)

        if isinstance(statement, ir.Constexpr):
            new_ir_m.statements.append(AsmStatement3("mov", var_name, str(statement.value)))
            return var_name

        if isinstance(statement, int):
            st = temp_vars[statement]
            if isinstance(st, ir.NewArray):
                self.need_malloc = True
                st_size = self.make_assign_expr_or_const(st.size, new_ir_m, local_sym_table, temp_vars,
                                                         allocated_memory)
                new_ir_m.statements.append(AsmStatement3("mov", "edi", "4*" + st_size + "+4"))
                new_ir_m.statements.append(AsmStatement2("push", "edi"))
                new_ir_m.statements.append(AsmStatement2("call", "malloc"))
                new_ir_m.statements.append(AsmStatement3("add", "rsp", "4"))
                new_ir_m.statements.append(AsmStatement3("mov", var_name, st_size))
                new_ir_m.statements.append(AsmStatement3("mov", "[ax]", var_name))
                new_ir_m.statements.append(AsmStatement3("mov", var_name, "ax"))
                allocated_memory.append(var_name)
                temp_vars[statement] = var_name

            if isinstance(st, ir.New):
                self.need_malloc = True
                need_memory = self.location_of_classes.get_memory_count(st.obj_type)
                new_ir_m.statements.append(AsmStatement3("mov", "edi", need_memory))
                new_ir_m.statements.append(AsmStatement2("push", "edi"))
                new_ir_m.statements.append(AsmStatement2("call", "malloc"))
                new_ir_m.statements.append(AsmStatement3("add", "rsp", "4"))
                new_ir_m.statements.append(AsmStatement3("mov", var_name, "ax"))
                new_ir_m.statements.append(AsmStatement3("mov", "[" + var_name + ']', var_name))
                allocated_memory.append(var_name)

            if isinstance(st, ir.BinOp):
                var_name = self.binop_to_asm(st, new_ir_m, local_sym_table, temp_vars, allocated_memory, var_name)
                temp_vars[statement] = var_name

            if isinstance(st, ir.Const):
                new_ir_m.statements.append(AsmStatement3("mov", var_name, st.value))
                temp_vars[statement] = var_name

            if isinstance(st, ir.Length):
                if not (st.obj in temp_vars) or (not isinstance(temp_vars[st.obj], str)):
                    print("Error: array " + str(st.obj) + "does not exist")
                    exit(0)
                new_ir_m.statements.append(AsmStatement3("mov", var_name, "[" + temp_vars[st.obj] + "]"))
                temp_vars[statement] = var_name

            if isinstance(st, ir.Call):
                class_name, class_method = st.method.split('.')
                parameters = list(self.sym_table[class_name].methods[class_method].params.keys())

                locals_in_stack = []
                new_ir_m.statements.append(";save some locals")
                for var in local_sym_table:
                    if var in parameters or var == 'this':
                        new_ir_m.statements.append(AsmStatement2("push", "asm_var_" + str(local_sym_table[var])))
                        locals_in_stack.append(var)

                new_ir_m.statements.append(AsmStatement3("mov", "this", '[' + self.make_assign_expr(
                        st.args[0], new_ir_m, local_sym_table, temp_vars, allocated_memory) + ']'))
                for idx, arg in enumerate(st.args[1:4]):
                    self.make_assign_expr_or_const(arg, new_ir_m, local_sym_table, temp_vars, allocated_memory,
                                                   parameters[idx - 1])
                for idx, arg in enumerate(st.args):
                    if idx >= 3:
                        self.make_assign_expr_or_const(arg, new_ir_m, local_sym_table, temp_vars,
                                                       allocated_memory, parameters[idx - 1])

                new_ir_m.statements.append(";save rest of locals")
                for var in local_sym_table:
                    if not (var in parameters or var == 'this'):
                        new_ir_m.statements.append(AsmStatement2("push", "asm_var_" + str(local_sym_table[var])))
                        locals_in_stack.append(var)

                new_ir_m.statements.append(";put params")
                for idx, arg in enumerate(st.args):
                    if idx >= 3:
                        new_ir_m.statements.append(AsmStatement2("push", parameters[idx - 1]))

                new_ir_m.statements.append(AsmStatement2("call", st.method.replace('.', '_')))

                for var in reversed(locals_in_stack):
                    new_ir_m.statements.append(AsmStatement2("pop", "asm_var_" + str(local_sym_table[var])))

                new_ir_m.statements.append(";call return value")
                new_ir_m.statements.append(AsmStatement3("mov", var_name, "ax"))
                temp_vars[statement] = var_name

            if isinstance(st, str):
                if new_var:
                    local_sym_table.pop(var_name)
                var_name = st

        return var_name

    def ir_to_asm(self, ir_tree, code_coloring):
        """
        ir - linear statement representation
        """

        new_labels_counter = 0

        new_ir = dict()

        temp_vars = {}  # Indices of temp vars in ir
        
        for method in ir_tree:
            local_sym_table = dict()
            allocated_memory = []
            color_table = code_coloring[method]

            if method == 'main':
                class_name, class_method = '', 'main'
                new_ir[method] = AsmMain()
            else:
                class_name, class_method = method.split('.')
                local_vars = []

                for statement in ir_tree[method].statements:
                    if isinstance(statement, ir.Local):
                        local_vars.append(statement)

                new_ir[method] = AsmMethod(self.sym_table[class_name].methods[class_method].params, local_vars, method)

                for idx, key in enumerate(self.sym_table[class_name].methods[class_method].params):
                    local_sym_table[key] = idx

                for idx, key in enumerate(self.sym_table[class_name].methods[class_method].vars,
                                          start=len(local_sym_table.keys())):
                    local_sym_table[key] = idx

                local_sym_table['this'] = 0

                params = reversed(list(self.sym_table[class_name].methods[class_method].params.keys())[3:])
                for param in params:
                    new_ir[method].statements.append(AsmStatement2("pop", param))

            for statement in ir_tree[method].statements:
                if isinstance(statement, ir.Call):
                    temp_vars[statement.trg] = statement

                if isinstance(statement, ir.Label):
                    if statement.local:
                        new_ir[method].statements.append(f"{class_name}_{class_method}_label_{statement.label_id}:")
                    else:
                        new_ir[method].statements.append(f"GLOBAL_label_{statement.label_id}:")

                if isinstance(statement, ir.Print):
                    new_ir[method].statements.append(AsmStatement3("mov", "ax", self.make_assign_expr_or_const(
                        statement, new_ir[method], local_sym_table, temp_vars, allocated_memory)))
                    # new_ir[method].statements.append(AsmStatement3("mov", "ax", "3030h"))
                    # new_ir[method].statements.append(AsmStatement3("mov", "dl", "sh"))
                    # new_ir[method].statements.append(AsmStatement3("mov", "dh", "al"))
                    # new_ir[method].statements.append(AsmStatement3("mov", "ah", "02"))
                    # new_ir[method].statements.append(AsmStatement2("int", "21h"))
                    # new_ir[method].statements.append(AsmStatement3("mov", "dl", "dh"))
                    new_ir[method].statements.append(AsmStatement2("call", "print"))

                if isinstance(statement, ir.Jump):
                    if statement.local:
                        new_ir[method].statements.append(AsmStatement2(
                            "jmp", f"{class_name}_{class_method}_label_{statement.label}"))
                    else:
                        new_ir[method].statements.append(AsmStatement2("jmp", f"GLOBAL_label_{statement.label}"))

                if isinstance(statement, ir.CJumpLess):
                    left = self.make_assign_expr(
                        statement.lhs, new_ir[method], local_sym_table, temp_vars, allocated_memory)
                    right = self.make_assign_expr(
                        statement.rhs, new_ir[method], local_sym_table, temp_vars, allocated_memory)
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
                    val = self.make_assign_expr(
                        statement.val, new_ir[method], local_sym_table, temp_vars, allocated_memory)
                    # new_ir[method].statements.append(AsmStatement3("mov", "dx", "0"))
                    new_ir[method].statements.append(AsmStatement3("cmp", val, "0"))
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

                if isinstance(statement, ir.New):
                    temp_vars[statement.trg] = statement

                if isinstance(statement, ir.AssignLocal):
                    self.make_assign_expr_or_const(
                        statement, new_ir[method], local_sym_table, temp_vars, allocated_memory, statement.name)

                if isinstance(statement, ir.AssignParam):
                    self.make_assign_expr_or_const(
                        statement, new_ir[method], local_sym_table, temp_vars, allocated_memory, statement.name)

                if isinstance(statement, ir.AssignField):
                    field_class, field_name = statement.name.split('.')
                    self.make_assign_expr_or_const(statement, new_ir[method], local_sym_table, temp_vars,
                                                   allocated_memory, '[' + temp_vars[statement.this] + ' + ' +
                                                   str(self.location_of_classes.find_offset(field_class, field_name)) +
                                                   ']')

                if isinstance(statement, ir.Local):
                    temp_vars[statement.trg] = statement.name

                if isinstance(statement, ir.Param):
                    temp_vars[statement.trg] = statement.name

                if isinstance(statement, ir.Field):
                    field_class, field_name = statement.name.split('.')
                    temp_vars[statement.trg] = '[' + temp_vars[statement.this] + ' + ' + str(
                        self.location_of_classes.find_offset(field_class, field_name)) + ']'

                if isinstance(statement, ir.ArrayAssign):
                    if not (statement.arr in temp_vars):
                        print("Error: array " + str(statement.arr) + " does not exist")
                        exit(0)
                    idx = self.make_assign_expr_or_const(
                        statement.idx, new_ir[method], local_sym_table, temp_vars, allocated_memory)
                    src = self.make_assign_expr_or_const(
                        statement.idx, new_ir[method], local_sym_table, temp_vars, allocated_memory)
                    new_ir[method].statements.append(AsmStatement3("mov", "[" + str(temp_vars[statement.arr]) +
                                                                   "+4*" + idx + "+4]", src))

                if isinstance(statement, ir.BinOp):
                    temp_vars[statement.trg] = statement

                if isinstance(statement, ir.Const):
                    temp_vars[statement.trg] = statement

                if isinstance(statement, ir.Index):
                    idx = len(local_sym_table)
                    var_name = "asm_var_" + str(idx)
                    local_sym_table[var_name] = idx
                    st_idx = self.make_assign_expr_or_const(
                        statement.idx, new_ir[method], local_sym_table, temp_vars, allocated_memory)
                    new_ir[method].statements.append(AsmStatement3(
                        "mov", var_name, "[" + str(temp_vars[statement.obj]) + "+4*" + st_idx + "+4]"))
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
                    new_ir[method].statements.append(AsmStatement3("mov", "ax", self.make_assign_expr_or_const(
                        statement, new_ir[method], local_sym_table, temp_vars, allocated_memory)))

            for var in allocated_memory:
                new_ir[method].statements.append(AsmStatement2("push", var))
                new_ir[method].statements.append(AsmStatement2("call", "free"))
                new_ir[method].statements.append(AsmStatement3("add", "rsp", "4"))

        return new_ir
