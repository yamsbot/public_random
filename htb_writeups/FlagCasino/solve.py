#!/usr/bin/env python3
from pwn import *
from string import printable as ap

'''
This challenge allows us to control the seed used for rand,
but to simplify the solution; instead of reversing __srandom_r() from glibc
to determine all the inputs we can simply bruteforce the solution..
'''

context.binary = binary = ELF("./casino", checksec=False)
context.log_level = "critical"

def runner():
    i = 0
    flag = ""
    while i < len(ap):
        p = process()
        p.recvuntil(b"BETS ***]")
        
        attempt = flag + ap[i]
        attempt = attempt.encode()
        p.sendline(attempt)
        
        print("sending", attempt)
        
        for x in range(0, len(attempt), 1):
            v = p.recvline_regex(b"\w{7,9}", timeout=1)
            if b"INCORRECT" in v:
                p.kill()
                i += 1
            elif b" CORRECT" in v and x == len(attempt)-1:
                flag += ap[i]
                p.kill()
                i = 0

            if flag.endswith("}"):
                print("flag found:", flag)
                quit()

if __name__ == "__main__":
    runner()
