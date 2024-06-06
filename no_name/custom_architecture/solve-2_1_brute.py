#!/usr/bin/python3
import re
import time
from pwn import *

# colors
base = "\033[0m"
green = "\033[0;32m"
yellow = "\033[0;33m"

binpath = ("")
context.binary = binary = ELF(binpath,checksec=False)
context.log_level = "error"
possible_values = ["01", "02", "04", "08", "10", "20", "40", "80"]
valid_opcodes = ["01", "10", "20", "40", "80"]
valid_instructions = []
f = open("./output.txt", "a")

_exit = "401004"

def _read(instruction):
    print(yellow + "Executing: " + green + instruction + base)
    shellcode = bytes.fromhex(instruction)
    
    p = process()
    p.sendline(shellcode)
    p.recvall(timeout=3).decode("utf-8")
    
    exit_code = p.poll()
    if exit_code != 0 and exit_code != 1:
        f.write(instruction + "\n")
        f.write("exit code:" + str(exit_code) + "\n\n")
    print("exit code:", exit_code, "\n")
    
    p.close()
    time.sleep(0.5)

def _execute_mov():
    for i in range(len(possible_values)):
        shellcode = possible_values[i]
        for ii in range(len(possible_values)):
            shellcode = shellcode[:2]
            shellcode += possible_values[ii]
            for iii in range(len(possible_values)):
                shellcode += possible_values[iii]
                if re.search("^20", shellcode) != None:
                        _execute_all(shellcode)
                shellcode = shellcode[:4]

def _execute_all(start_inst):
    for i in range(len(possible_values)):
        shellcode = possible_values[i]
        for ii in range(len(possible_values)):
            shellcode = shellcode[:2]
            shellcode += possible_values[ii]
            for iii in range(len(possible_values)):
                shellcode += possible_values[iii]
                x_shellcode = start_inst
                x_shellcode += shellcode
                x_shellcode += _exit
                shellcode = shellcode[:4]
                _read(x_shellcode)

def _run_noCrash():
    f = open("./no-crash.txt", "r")
    for line in f:
        if re.search("^80", line) != None:
            shellcode = line.rstrip()
            shellcode = _exit
            _read(shellcode)

_execute_mov()
f.close()
