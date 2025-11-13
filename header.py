from enum import Enum

instr_map: dict = {
    "li":   0b0000,
    "nor":  0b0001,
    "clrb": 0b0010,
    "lsl":  0b0011,
    "lsr":  0b0100,
    "asr":  0b0101,
    "xor":  0b0110,
    "nand": 0b0111,
    "and":  0b1000,
    "xnor": 0b1001,
    "lui":  0b1010,
    "bra":  0b1011,
    "add":  0b1100,
    "sub":  0b1101,
    "or":   0b1110,
    "tworeg": 0b1111,
}

ex_map: dict = {
    "sw":   0b0000,
    "sb":   0b0001,
    "lw":   0b0010,
    "lbu":  0b0011,
    "lbs":  0b0100,
    "bz":   0b0101,
    "jz":   0b0110,
    "jal":  0b0111,
    "neg":  0b1000,
    "com":  0b1001,
    "sle":  0b1010,
    "slt":  0b1011,
    "sge":  0b1100,
    "sgt":  0b1101,
    "snz":  0b1110,
    "sz":   0b1111,
}


class INSTR_TYPE(Enum):
    NONE = -1
    REG = 0
    STORE = 1
    IMM = 2
    TWOREG = 3

format_map: dict = {
    INSTR_TYPE.REG:[
        "nor",
        "clrb",
        "lsl",
        "lsr",
        "asr",
        "xor",
        "nand",
        "and",
        "xnor",
        "add",
        "sub",
        "or",
    ],
    INSTR_TYPE.STORE:[
        "li",
        "lui",
    ],
    INSTR_TYPE.IMM:[
        "bra",
    ],
    INSTR_TYPE.TWOREG:list(ex_map.keys()),
}

register_pattern = r"r\d[0-5]?"
instruction_pattern = r"^\s*[a-z]{2,4}"
label_pattern = r"^\s*[a-zA-Z]*:\s*"
#instr rd, rs1, rs2
reg_instr_pattern = (instruction_pattern + r"\s*" +
                     register_pattern + r",\s*" +
                     register_pattern + r",\s*" +
                     register_pattern + r"\s*")
#instr rd, imm
store_pattern = (instruction_pattern + r"\s*" +
                 register_pattern + r",\s*" +
                 r"((0b[0-1]{1,8})|(0x[0-9a-f]{1,2})|(-?[0-9]{1,3}))" + r"\s*")
#instr imm
imm_pattern = (instruction_pattern + r"\s*" +
                 r"((0b[0-1]{1,12})|(0x[0-9a-f]{1,3})|(-?[0-9]{1,4}))" + r"\s*")
#instr rd, rs1
tworeg_pattern = (instruction_pattern + r"\s*" +
                  register_pattern + r",\s*" +
                  register_pattern + r"\s*")

class Instruction_t():
    def __init__(self):
        self.type = INSTR_TYPE.NONE
        self.opcode: int = -1
        self.ex: int = -1
        self.imm8: int = -1
        self.imm12: int = -1
        self.rs1: int = -1
        self.rs2: int = -1
        self.rd: int = -1

    def __str__(self):
        return f"type: {self.type}, opcode: {self.opcode}, ex: {self.ex}, imm8: {self.imm8}, imm12: {self.imm12}, rs1: {self.rs1}, rs2: {self.rs2}, rd: {self.rd}"

    def set_reg(self, opcode, rd, rs1, rs2):
        #todo: add checks
        self.type = INSTR_TYPE.REG
        self.opcode = opcode
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2

    def set_store(self, opcode, rd, imm):
        #todo: add checks
        self.type = INSTR_TYPE.STORE
        self.opcode = opcode
        self.rd = rd
        self.imm8 = imm

    def set_imm(self, opcode, imm):
        #todo: add checks
        self.type = INSTR_TYPE.IMM
        self.opcode = opcode
        self.imm12 = imm

    def set_tworeg(self, opcode, rd, rs1, ex):
        #todo: add checks
        self.type = INSTR_TYPE.TWOREG
        self.opcode = opcode
        self.rd = rd
        self.rs1 = rs1
        self.ex = ex

