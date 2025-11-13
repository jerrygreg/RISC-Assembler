# RISC-Assembler
This is a small python script to compile the RISC (Reduced Instruction Set Computer) architecture assembly for the Johns Hopkins University's Advanced Digital Systems final project. This assembler is accurate atleast upto Fall 2025.

The architecture and associated assembly is detailed in the [RISC Specifications](cpu.pdf). 

**Why was this created?** \
This was created to tackle the issue of manually translating the instructions is this architecture. Simply, it reduces the tedious work of transcribing assembly into machine code.

## Prerequisites
Make sure you have python downloaded. If you do not, you can go to `Anaconda Navigator` and download python from them.

## How to use?
First, you should clone this repo into a location that is close to where you are working on the final project. 
```
git clone https://github.com/jerrygreg/RISC-Assembler.git
cd RISC-Assembler
python risc_assembler.py --help
```
This should show you the options for calling the [RISC Assembler](risc_assembler.py) script. If you'd like to actually use it to assemble some RISC assembly, you can call something like the following.
```
python risc_assembler.py risc_asm.txt --debug
```
This will output the assembled code in two forms. The binary machine code in `outbin.txt` and the hex machine code in `outhex.txt`.

***NOTE:*** **When using this script, double check the assembled program. This script was created in a day and may have bugs.**

## Calling
When you call this script, you must provide a file to assemble.
```
python risc_assembler.py <risc_asm-file>
```
There are some optional flags you may also pass.
- `--debug`: Provides debug prints to the console when you call the script. Tells you information such as how the script is interpreting each line.

## Instruction Convention
There are 4 different types of instructions.

**Three-Register** \
These are instructions such as `and` which take 3 registers as input. They all follow the form `instruction rd, rs1, rs2`.\
**For Example:** `and r1, r2, r15`

**Store** \
These are instructions such as `lui` which take 1 register and an 8-bit immediate as input. They all follow the form `instruction rd, imm8`.\
 **For Example:**`lui r3, 102 `

**Immediate** \
These are instructions such as `bra` which take a 12-bit immediate as input. They all follow the form `instruction imm12`.\
 **For Example:** `bra 0x01F`

**Two-Register** \
These are instructions such as `neg` which take two registers as input. They all follow the form `instruction rd, rs1`.\
 **For Example:** `neg r5, r6`

## Immediates
When writing an immediates there are 3 formats you can use:
- `0b<binary-number>`
e.g. `0b11111111`
- `0x<hex-number>`
e.g. `0xFF`
- `<decimal-number>`
e.g. `255`

Immediates can be negative.

## Comments
You can add comments anywhere by using a `#`. This will comment out the rest of the line and the assembler will ignore it.

## Labels
Labels are not supported by this assembler.

## Contact
Send me an email if you have questions. jgrego28@jh.edu
