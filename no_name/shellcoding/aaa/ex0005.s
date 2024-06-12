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

# read
pop rdi
mov rdi, rax
sub rsp, 256
mov rsi, rsp
mov rdx, 256
mov rax, 0
syscall

setup: # FOR TESTING
add rsp, 4
xor rcx, rcx
mov rsi, rsp
mov rdx, rsp            # stack pointer into rdx
add rdx, 180            # add 100 to stack pointer for ???

parse:			# parse requested file
mov rax, [rsi+rcx]      # grab value from ??
and rax, 0xff           # move to rax and and
cmp al, 0x20            # compare to space
je open
mov [rdx], al           # move value into rdx
add rdx, 1              # if not space inc variable slot
inc rcx
jmp parse               # loop

open:
mov r10, rdi
mov rdi, rdx
sub rdi, rcx
xor rsi, rsi
mov rax, 2
syscall

read:
sub rsp, 0xffff
mov rsi, rsp
add rsi, 0x0f00
mov rbx, rsi
mov rdi, rax
mov rdx, 1024
mov rax, 0
syscall

close:
mov rax, 3
syscall 

write: # 200 OK
mov rax, 0x000a0d0a0d4b4f20
push rax
mov rax, 0x30303220302e312f
push rax
xor rax, rax
mov ax, 0x5054
push ax
xor rax, rax
mov ax, 0x5448
push ax
mov rdi, r10
mov rsi, rsp
mov rdx, 19
mov rax, 1
syscall

xor rcx, rcx
parse0:			# count size of file
mov rsi, rbx
mov rax, [rsi+rcx]      # grab value from stack
and rax, 0xff           # move to rax > and
cmp al, 0x00            # compare to z
je write_file
inc rcx
jmp parse0              # loop

write_file:
mov rsi, rbx
mov rdx, rcx
mov rax, 1
syscall

# close
mov rax, 3
syscall 

exit:
xor rdi, rdi
xor rsi, rsi
xor rdx, rdx
mov rax, 60
syscall
