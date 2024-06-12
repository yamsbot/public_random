.global _start
_start:
.intel_syntax noprefix

# socket 
mov rdi, 2
mov rsi, 1
mov rdx, 0
mov rax, 41
syscall                 # create socket

# bind
mov rdi, rax
mov rax, 0x00000000     # 0.0.0.0
shl rax, 16
mov al, 0x00            # 0.0.0.0:0080
mov ah, 0x50
shl rax, 16             # AF_INET
mov al, 2               # AF_INET
push rax
mov rsi, rsp
mov rdx, 16             # SIZE
mov rax, 49             # bind()
syscall

# listen
xor rsi, rsi
mov rax, 50
syscall

# accept
xor rdx, rdx
mov rax, 43
syscall

# exit
xor rdi, rdi
xor rsi, rsi
xor rdx, rdx
mov rax, 60
syscall
