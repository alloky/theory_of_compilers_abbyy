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
        return f"{self.method_name}:"\
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
        return  "{} {} {}".format(self.cmd, self.src, self.dst)


class AsmStatement2:
    def __init__(self, cmd, src):
        self.cmd = cmd
        self.src = src

    def __str__(self):
        return  "{} {}".format(self.cmd, self.src)


class AsmPrint:
    def __init__(self, src):
        self.src = src

    def __str__(self):
        # TODO : call print
        return  "{} {}".format("print", self.src)



class X86Assembler:
    def ir_to_asm(self, ir, sym_table):
        """
        ir - linear statement representation
        """

        new_ir = dict()
        for method in ir:
            if method == 'main':
                pass
                # TODO entry point
            else:
                className, classMethod = method.split('.')
                local_vars = []

                for statement in ir[method].statements:
                    if isinstance(statement, ir.Local):
                        local_vars.append(statement)

                new_ir[method] = AsmMethod(sym_table[className].methods[classMethod].params, local_vars, method)

                local_sym_table = dict()
                for idx, key in enumerate(sym_table[className].methods[classMethod].params):
                    local_sym_table[key] = idx

                for idx, key in enumerate(sym_table[className].methods[classMethod].vars,
                                          start=len(local_sym_table.keys())):
                    local_sym_table[key] = idx

                for statement in ir[method].statements:
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
                            new_ir[method].statements.append(f"{method}_label_{statement.id}:")
                        else:
                            new_ir[method].statements.append(f"GLOBAL_label_{statement.id}:")
                    if isinstance(statement, ir.Jump):
                        if statement.local:
                            new_ir[method].statements.append(AsmStatement2("jmp", f"{method}_label_{statement.id}"))
                        else:
                            new_ir[method].statements.append(AsmStatement2("jmp", f"GLOBAL_label_{statement.id}"))
                    if isinstance(statement, ir.Print):
                        new_ir[method].statements.append(AsmPrint(statement.src))
                    if isinstance(statement, ir.AssignLocal):
                        trg = local_sym_table[statement.name]
                        new_ir[method].statements.append(AsmStatement3("mov", trg, statement.src))










