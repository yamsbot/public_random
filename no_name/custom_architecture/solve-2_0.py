#!/usr/bin/python3
from pwn import *

binpath = ("???")
context.binary = binary = ELF(binpath,checksec=False)

gdbscript = '''
set disassembly-flavor intel
'''

p = process()
#p = gdb.debug(binpath, gdbscript=gdbscript, terminal=['tmux', 'splitw', '-h'])

# opcodes
# 01 = jmp, 02 = imm, 04 = add, 08 = ldm, 10 = ???, 20 = sys, 40 = ???, 80 = stk

# registers
# a = 10
# b = 08
# c = 40
# d = 20
# s = 04
# i = 01
# f = 02

# syscalls
# 1=read_code, 2=read_memory, 8=sleep, 10=exit 40=write,  80=open

# Potential values:
# REGS : A     B     C     D     S     I     F 
# OPS  : IMM   STK   ADD   STM   LDM   JMP   CMP   SYS
# SYSC : OPEN  READM READC WRITE SLEEP EXIT
# FLAG : L     G     E     N     Z
#pvals = ["01", "02", "04", "08", "10", "20", "40", "80"]

shellcode = ""
flag = ["2f", "66", "6c", "61", "67", "00"]
push_a = "108000"
for v in flag:
    shellcode += v
    shellcode += "02"
    shellcode += "10"
    shellcode += push_a

# open()
shellcode += "010210"
shellcode += "000208"
shellcode += "202080"

# read()
shellcode += "000210"
shellcode += "200410"
shellcode += "000220"
shellcode += "ff0240"
shellcode += "202002"

# write()
shellcode += "010210"
shellcode += "000240"
shellcode += "200440"
shellcode += "202040"

# exit()
shellcode += "202010"

shellcode = bytes.fromhex(shellcode)
p.recv()
p.sendline(shellcode)
p.recv()
p.interactive()
