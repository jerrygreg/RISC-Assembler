from os import close

from header import *
import sys
import argparse
import re
import datetime

def print_usage():
    print("usage: risc_compiler.py <risc_assembly.txt> [options]")
    print("--debug :Used to turn on debug prints.")

def parse_imm(imm: str, bits: int) -> int | str:
    if re.fullmatch(instr_label_pattern, imm):
        return imm
    elif imm[0:2] == "0x":
        immediate = int(imm[2:], 16)
        if (len(imm) == 2 + int(bits/4)) and bool(re.fullmatch(r"(8|[a-f])",imm[2])):
            immediate -= 2**bits
        return immediate

    elif imm[0:2] == "0b":
        immediate = int(imm[2:], 2)
        if (len(imm) == 2 + bits) and imm[2] == "1":
            immediate -= 2**bits
        return immediate

    else:
        return int(imm)

def dectohex(imm: int, bits: int, signext: bool = False):
    if signext and imm < 0:
        imm += 2**bits
    return hex(imm)[2:].zfill(int(bits/4))

def dectobin(imm: int, bits: int, signext: bool = False):
    if signext and imm < 0:
        imm += 2**bits
    return bin(imm)[2:].zfill(bits)

def strip_instr(instr: str, line: int, debug: bool = False) -> tuple[list[str], INSTR_TYPE]:
    # Parse string
    instr = instr.lower()
    if instr.count("#") != 0:
        if debug: print(f"info  | line:{line} has a comment")
        instr = instr[0:instr.find("#")]
    instr = instr.strip()
    split_instr = instr.split(" ")

    if len(instr) == 0:  # whole line is a comment
        if debug: print(f"info  | line:{line} is a comment")
        return [""], INSTR_TYPE.NONE
    elif len(split_instr) > 4:
        print(f"ERROR | line:{line} This instruction has too many arguments")
        sys.exit(1)

    instr_type: INSTR_TYPE = INSTR_TYPE.NONE
    # Regex
    if re.fullmatch(reg_instr_pattern, instr):
        if debug: print(f"info  | line:{line} is a 3reg instruction")
        instr_type = INSTR_TYPE.REG
    elif re.fullmatch(store_pattern, instr):
        if debug: print(f"info  | line:{line} is a store instruction")
        instr_type = INSTR_TYPE.STORE
    elif re.fullmatch(imm_pattern, instr):
        if debug: print(f"info  | line:{line} is a immediate instruction")
        instr_type = INSTR_TYPE.IMM
    elif re.fullmatch(tworeg_pattern, instr):
        if debug: print(f"info  | line:{line} is a 2reg instruction")
        instr_type = INSTR_TYPE.TWOREG
    elif re.fullmatch(label_pattern, instr):
        if debug: print(f"info  | line:{line} is a label")
        instr_type = INSTR_TYPE.LABEL
    else:
        print(f"ERROR | line:{line} This line does not match the pattern of any other instructions")
        sys.exit(2)

    split_instr = [var.strip(",").strip(":").strip() for var in split_instr]

    return split_instr, instr_type
#END strip_instr


def process_instr(instr: str, line: int, debug = False) -> Instruction_t:
    # Init
    instruction: Instruction_t = Instruction_t()

    split_instr, instr_type = strip_instr(instr, line, debug = debug)

    instruction.type = instr_type

    # Find opcode if need be
    if instruction.type != INSTR_TYPE.NONE:
        try:
            if instruction.type == INSTR_TYPE.TWOREG:
                opcode = 0b1111
            elif instruction.type != INSTR_TYPE.LABEL:
                opcode = instr_map[split_instr[0]]
            else:
                opcode = 0b0000 # shouldn't be reachable
        except KeyError:
            print(f"ERROR | line:{line} This instruction '{split_instr[0]}' is not valid as a '{instruction.type}' instruction.")
            print(f"      | You may have provided the wrong arguments.")
            sys.exit(3)

        if instruction.type == INSTR_TYPE.REG:
            #parse reg
            instruction.set_reg(
                opcode = opcode,
                rd = int(split_instr[1][1:]),
                rs1 = int(split_instr[2][1:]),
                rs2 = int(split_instr[3][1:])
            )
        elif instruction.type == INSTR_TYPE.STORE:
            #parse store
            immediate = parse_imm(split_instr[2][:], 8)
            assert(type(immediate) == int)
            if not(-128 <= immediate <= 127):
                print(f"ERROR | line:{line} The immediate is out of range [-128,127]")
                sys.exit(3)
            instruction.set_store(
                opcode = opcode,
                rd = int(split_instr[1][1:]),
                imm = immediate,
            )
        elif instruction.type == INSTR_TYPE.IMM:
            #parse imm
            immediate = parse_imm(split_instr[1][:], 12)
            if type(immediate) == int:
                if not(-2048 <= immediate <= 2047):
                    print(f"ERROR | line:{line} The immediate is out of range [-2048,2047]")
                    sys.exit(3)

            instruction.set_imm(
                opcode = opcode,
                imm = immediate,
            )
        elif instruction.type == INSTR_TYPE.TWOREG:
            #parse tworeg
            try:
                ex_code = ex_map[split_instr[0]]
            except KeyError:
                print(f"ERROR | line:{line} This instruction '{split_instr[0]}' is not valid as a '{instruction.type}' instruction.")
                print(f"      | You may have provided the wrong arguments.")
                sys.exit(3)
            instruction.set_tworeg(
                opcode = opcode,
                rd = int(split_instr[1][1:]),
                rs1 = int(split_instr[2][1:]),
                ex = ex_code,
            )
        elif instruction.type == INSTR_TYPE.LABEL:
            try:
                label = split_instr[0]
            except KeyError:
                print(f"ERROR | line:{line} This instruction '{split_instr[0]}' is not valid as a '{instruction.type}'.")
                print(f"      | You may have provided the wrong arguments.")
                sys.exit(3)
            instruction.set_label(
                label = label,
            )

    return instruction
#END Process_instr

def write_instr(p_instr: Instruction_t, label_table: dict[str, tuple[int, int]], 
                writeable_file, line: int,
                print_hex = False, concat_str = "_",
                formatted = False, address = 0x0,
                push_back: str = ""):
    assert(p_instr.type != INSTR_TYPE.NONE)
    # To catch any instances where we get to the end without hitting any of the if/elif statements
    write_str = "Some error occured when writing the instruction."

    convert = dectobin
    if print_hex: convert = dectohex

    opcode_bin = convert(p_instr.opcode,4)
    if p_instr.type == INSTR_TYPE.REG:
        # write reg
        rd_bin = convert(p_instr.rd,4)
        rs1_bin = convert(p_instr.rs1,4)
        rs2_bin = convert(p_instr.rs2,4)
        write_str = concat_str.join([opcode_bin, rd_bin, rs1_bin, rs2_bin])

    elif p_instr.type == INSTR_TYPE.STORE:
        # write store
        rd_bin = convert(p_instr.rd,4)
        imm8_bin = convert(p_instr.imm8,8, signext = True)
        write_str = concat_str.join([opcode_bin, rd_bin, imm8_bin])

    elif p_instr.type == INSTR_TYPE.IMM:
        # write imm
        if type(p_instr.imm12) == str:
            if p_instr.imm12 in label_table.keys():
                p_instr.imm12 = label_table[p_instr.imm12][1] - addr
                if not(-2048 <= p_instr.imm12 <= 2047):
                    print(f"ERROR | line:{line} The immediate is out of range [-2048,2047]")
                    sys.exit(3)
            else:
                print(f"ERROR | line:{line} The label '{p_instr.imm12}' does not exist as a label.")
                sys.exit(4)
            
        assert(type(p_instr.imm12) == int)
        
        imm12_bin = convert(p_instr.imm12, 12, signext = True)
        write_str = concat_str.join([opcode_bin, imm12_bin])

    elif p_instr.type == INSTR_TYPE.TWOREG:
        # write tworeg
        rd_bin = convert(p_instr.rd, 4)
        rs1_bin = convert(p_instr.rs1, 4)
        ex_bin = convert(p_instr.ex, 4)
        write_str = concat_str.join([opcode_bin, rd_bin, rs1_bin, ex_bin])

    # Format string
    if formatted:
        if print_hex:
            justify_len = 4
            write_str = "x\"" + write_str
        else:
            justify_len = 16
            write_str = "b\"" + write_str
        write_str = ((write_str + "\",").ljust(2 + justify_len + 3*len(concat_str) + 2)
                     + f" -- Address 0x{dectohex(address, bits = 4*4)} ({push_back})")

    writeable_file.write(write_str + "\n")
    return write_str

# Main function
if __name__ == "__main__":
    print("---------------------------------------------------------------")
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument("file_path", type=str, help="The path to a text file with the risc assembly.")
    parser.add_argument("-d", "--debug", action="store_true", help="Turn on debug prints.")
    parser.add_argument("-F", "--formatted", action="store_true", help="Formats the print for direct copy-paste into the vhdl memory file.")
    parser.add_argument("-nu", "--no-underscore", action="store_true", help="Turns off the underscore spacers in output files.")
    parser.add_argument("-bf", "--binf", type=str, default="outbin.txt", help="Specifies the file to output the binary machine code to.")
    parser.add_argument("-hf", "--hexf", type=str, default="outhex.txt", help="Specifies the file to output the hex machine code to.")
    args = parser.parse_args()

    #debug
    print(f"Running with arguments:",f"{args}"[9:])
    debug_on = args.debug
    file_path = args.file_path
    formatted_flag = args.formatted

    if args.no_underscore:
        concat_str = ""
    else:
        concat_str = "_"

    outfile_bin = open(args.binf, "w")
    outfile_hex = open(args.hexf, "w")

    # Headers
    outfile_hex.write(f"'{file_path}' assembled at '{datetime.datetime.now()}' with arguments " + f"{args}"[9:] + "\n")
    outfile_bin.write(f"'{file_path}' assembled at '{datetime.datetime.now()}' with arguments " + f"{args}"[9:] + "\n")

    # stored as {label, (line, addr)}
    label_table: dict[str, tuple[int,int]] = {}
    # stored as {line_num, instr, addr, original}
    instr_table: list[tuple[int, Instruction_t,int,str]] = []

    addr = 0x0
    with open(file_path, "r") as infile:
        line_num: int = 1
        for instr in infile:
            # Process instruction
            p_instr = process_instr(instr, line_num, debug=debug_on)
            if p_instr.type == INSTR_TYPE.LABEL:
                if p_instr.label in label_table.keys():
                    raise ValueError(f"ERROR | line:{line_num} you may have a duplicate label. {p_instr.label} at line {line_num} and {label_table[p_instr.label][0]}")
                else:
                    label_table[p_instr.label] = (line_num, addr)
            elif p_instr.type != INSTR_TYPE.NONE:
                instr_table.append((line_num, p_instr, addr, instr))
                addr += addr_increment

            line_num += 1

    # Write instruction
    for line, p_instr, addr, instr in instr_table:
        if (p_instr.type != INSTR_TYPE.NONE) and (p_instr.type != INSTR_TYPE.LABEL):
            write_instr(p_instr, label_table, outfile_bin, line, print_hex = False, address = addr,
                        concat_str = concat_str, formatted = formatted_flag,
                        push_back = instr.rstrip())
            write_instr(p_instr, label_table, outfile_hex, line, print_hex = True, address = addr,
                        concat_str = concat_str, formatted = formatted_flag,
                        push_back = instr.rstrip())

    instr_table.sort(key = lambda x : x[2])
    if debug_on:
        print("INFO  | LABEL TABLE")
        print("{")
        for key,value in label_table.items():
            print(f"{(key + ":"):14} line: {value[0]:3d}, addr: {hex(value[1]):>5}")
        print("}")
        print("INFO  | INSTRUCTION TABLE")
        print("[")
        for entry in instr_table:
            print(f"line: {entry[0]:3d}, {entry[1]}, addr: {hex(entry[2]):>5}, text: {entry[3].strip("\n")}")
        print("]")
        print()

    outfile_bin.close()
    outfile_hex.close()

    print("This assembler has completed running!")
    print("Please make sure you double check the machine code. \nThis program was make in one day, it could have bugs.")
    print("---------------------------------------------------------------")