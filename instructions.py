R_TYPE = {
    'add': {'opcode': 0, 'func': 0x20, 'args': ('rd', 'rs', 'rt')},
    'addu': {'opcode': 0, 'func': 0x21, 'args': ('rd', 'rs', 'rt')},
    'sub': {'opcode': 0, 'func': 0x22, 'args': ('rd', 'rs', 'rt')},
    'subu': {'opcode': 0, 'func': 0x23, 'args': ('rd', 'rs', 'rt')},
    'slt': {'opcode': 0, 'func': 0x2A, 'args': ('rd', 'rs', 'rt')},
    'sltu': {'opcode': 0, 'func': 0x2B, 'args': ('rd', 'rs', 'rt')},
    'and': {'opcode': 0, 'func': 0x24, 'args': ('rd', 'rs', 'rt')},
    'or': {'opcode': 0, 'func': 0x25, 'args': ('rd', 'rs', 'rt')},
    'xor': {'opcode': 0, 'func': 0x26, 'args': ('rd', 'rs', 'rt')},
    'nor': {'opcode': 0, 'func': 0x27, 'args': ('rd', 'rs', 'rt')},
    'sll': {'opcode': 0, 'func': 0x0, 'args': ('rd', 'rt', 'shamt')},
    'srl': {'opcode': 0, 'func': 0x2, 'args': ('rd', 'rt', 'shamt')},
    'sra': {'opcode': 0, 'func': 0x3, 'args': ('rd', 'rt', 'shamt')},
    'mult': {'opcode': 0, 'func': 0x18, 'args': ('rs', 'rt')},
    'multu': {'opcode': 0, 'func': 0x19, 'args': ('rs', 'rt')},
    'div': {'opcode': 0, 'func': 0x1a, 'args': ('rs', 'rt')},
    'divu': {'opcode': 0, 'func': 0x1b, 'args': ('rs', 'rt')},
    'jalr': {'opcode': 0, 'func': 0x9, 'args': ('rs', 'rd')},
    'jr': {'opcode': 0, 'func': 0x8, 'args': ('rs',)},
}

I_TYPE = {
    'lw': {'opcode': 0x23, 'args': ('rt', 'imm', 'rs')},
    'addi': {'opcode': 0x8, 'args': ('rt', 'rs', 'imm')},
    'addiu': {'opcode': 0x9, 'args': ('rt', 'rs', 'imm')},
    'andi': {'opcode': 0xc, 'args': ('rt', 'rs', 'imm')},
    'ori': {'opcode': 0xd, 'args': ('rt', 'rs', 'imm')},
    'xori': {'opcode': 0xe, 'args': ('rt', 'rs', 'imm')},
    'lui': {'opcode': 0xf, 'rs': 0, 'args': ('rt', 'imm')},
    'slti': {'opcode': 0xa, 'args': ('rt', 'rs', 'imm')},
    'sltiu': {'opcode': 0xb, 'args': ('rt', 'rs', 'imm')},
    'beq': {'opcode': 0x4, 'args': ('rs', 'rt', 'imm')},
    'bne': {'opcode': 0x5, 'args': ('rs', 'rt', 'imm')},
    'blez': {'opcode': 0x6, 'rt': 0, 'args': ('rs', 'imm')},
    'bgtz': {'opcode': 0x7, 'rt': 0, 'args': ('rs', 'imm')},
    'bltz': {'opcode': 0x1, 'rt': 0, 'args': ('rs', 'imm')},
    'bgez': {'opcode': 0x1, 'rt': 1, 'args': ('rs', 'imm')},
    'lb': {'opcode': 0x20, 'args': ('rt', 'imm', 'rs')},
    'lbu': {'opcode': 0x24, 'args': ('rt', 'imm', 'rs')},
    'lh': {'opcode': 0x21, 'args': ('rt', 'imm', 'rs')},
    'lhu': {'opcode': 0x25, 'args': ('rt', 'imm', 'rs')},
    'sw': {'opcode': 0x2b, 'args': ('rt', 'imm', 'rs')},
    'sb': {'opcode': 0x28, 'args': ('rt', 'imm', 'rs')},
    'sh': {'opcode': 0x29, 'args': ('rt', 'imm', 'rs')}
}

J_TYPE = {
    'j': {'opcode': 0x2, 'args': ('target',)},
    'jal': {'opcode': 0x3, 'args': ('target',)}
}

REGISTERS = {
    '$zero': 0, '$at': 1,
    '$v0': 2, '$v1': 3,
    '$a0': 4, '$a1': 5, '$a2': 6, '$a3': 7,
    '$t0': 8, '$t1': 9, '$t2': 10, '$t3': 11, '$t4': 12, '$t5': 13, '$t6': 14, '$t7': 15,
    '$s0': 16, '$s1': 17, '$s2': 18, '$s3': 19, '$s4': 20, '$s5': 21, '$s6': 22, '$s7': 23,
    '$t8': 24, '$t9': 25,
    '$k0': 26, '$k1': 27,
    '$gp': 28,
    '$sp': 29, '$fp': 30,
    '$ra': 31
}

label_table = {}


class Instruction(object):
    label, type, name, opcode, instruction_string, address = None, None, None, 0, None, 0

    def __init__(self, dictionary):
        self.__dict__.update(dictionary)


class R_instruction(Instruction):
    rs, rt, rd, shamt, func = 0, 0, 0, 0, 0

    def __init__(self, dictionary):
        super().__init__(dictionary)
        for i in R_TYPE[self.name]['args']:
            if i != 'shamt':
                self.__setattr__(i, REGISTERS[dictionary[i]])
            else:
                self.__setattr__(i, int(self.shamt))

    def to_binary(self):
        return "{0}{1}{2}{3}{4}{5}".format(bin(self.opcode)[2:].zfill(6),
                                           bin(self.rs)[2:].zfill(5),
                                           bin(self.rt)[2:].zfill(5),
                                           bin(self.rd)[2:].zfill(5),
                                           bin(self.shamt)[2:].zfill(5),
                                           bin(self.func)[2:].zfill(6))


class I_instruction(Instruction):
    rs, rt, imm = 0, 0, 0

    def __init__(self, dictionary):
        super().__init__(dictionary)
        for i in I_TYPE[self.name]['args']:
            if i != 'imm':
                self.__setattr__(i, REGISTERS[dictionary[i]])
            else:
                # if self.imm[:2].lower() == '0x' and self.imm[2:].isnumeric():
                if self.imm[:2].lower() == '0x':
                    self.__setattr__(i, int(self.imm, 16))
                elif str(self.imm).isnumeric() or (str(self.imm)[0] == '-' and str(self.imm)[1:].isnumeric()):
                    self.__setattr__(i, int(self.imm, 10))
                else:
                    if self.name == 'beq' or self.name == 'bne':
                        self.__setattr__(i, label_table[self.imm] - self.address - 1)
                    else:
                        self.__setattr__(i, label_table[self.imm])

    def to_binary(self):
        if self.imm >= 0:
            return "{0}{1}{2}{3}".format(bin(self.opcode)[2:].zfill(6),
                                         bin(self.rs)[2:].zfill(5),
                                         bin(self.rt)[2:].zfill(5),
                                         bin(self.imm)[2:].zfill(16))
        else:
            offset = self.imm & 0b1111111111111111
            return "{0}{1}{2}{3}".format(bin(self.opcode)[2:].zfill(6),
                                         bin(self.rs)[2:].zfill(5),
                                         bin(self.rt)[2:].zfill(5),
                                         bin(offset)[2:].zfill(16))


class J_instruction(Instruction):
    target = 0

    def __init__(self, dictionary):
        super().__init__(dictionary)
        if isinstance(self.target, str):
            self.target = label_table[self.target]

    def to_binary(self):
        return "{0}{1}".format(bin(self.opcode)[2:].zfill(6),
                               bin(self.target)[2:].zfill(26))
