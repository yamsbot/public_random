#!/usr/bin/python3
from pwn import *

context.binary = binary = ELF("???",checksec=False)
bin_path=("???")

gdb_script='''
set disassembly-flavor intel
break *????+0x5a
display/8i $rip
display/x $rax
display/x $rbx
display/x $rcx
display/x $rdx
display/x $rdi
display/x $rsi
c
'''

p = process()
#p = gdb.debug(bin_path, gdbscript=gdb_script, terminal=['tmux', 'splitw', '-h'])

shellcode = ""

# _registers
# 0x400; 0x20 = a
# 0x401; 0x40 = b
# 0x402; 0x04 = c
# 0x403; 0x02 = d
# 0x404; 0x10 = vStack pointer
# 0x405; 0x08 = vInstruction pointer
# 0x406; 0x01 = f

# constants
_open = ("080102") # store in register d
_read = ("040102") # store in register d
_write = ("100120")
_exit = ("020100")
imm_a = ("2004")
imm_b = ("4004")
imm_c = ("0404")
imm_d = ("0204")
imm_s = ("1004")
imm_i = ("0804")
imm_f = ("0104")
ldm_a = ("2080")
ldm_b = ("4080")
ldm_c = ("0480")

# build and call open()
flag = ["2f", "66", "6c", "61", "67", "00"] # '/flag\0'
psh_a = ("000820")
for v in flag:
    shellcode += imm_a
    shellcode += v
    shellcode += psh_a

shellcode += imm_a + "01"
shellcode += imm_b + "00"
shellcode += _open

# build and call read()
shellcode += imm_a + "00"
shellcode += "204002"       # add d to a
shellcode += imm_d + "00"
shellcode += imm_c + "ff"   # size to read
shellcode += _read

# build and call write()
shellcode += imm_a + "01"
shellcode += imm_c + "00"
shellcode += "044002"       # add d to c
shellcode += _write

# exit cleanly
shellcode += _exit
shellcode = bytes.fromhex(shellcode)

p.recv()
p.sendline(shellcode)
p.interactive()
