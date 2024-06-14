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

listen:
xor rsi, rsi
xor rdx, rdx
mov rax, 50
syscall

accept:
mov rax, 43
syscall

fork:
mov r8, rdi             # store socket return (3) into r8
mov r9, rax             # store accept return (4) into r9
mov rax, 57
syscall

child_or_parent:
cmp rax, 0
je child_exec
mov rdi, r9             # r9 NOT free to use in child (?)
mov rax, 3
syscall
mov rdi, r8
jmp accept

child_exec:
mov rdi, r8             # close socket in child
mov rax, 3
syscall                 # close()

read_request:
mov rdi, r9
sub rsp, 0xffff         # allocate stack
mov rsi, rsp
mov rdx, 0x0200         # 512 bytes for request
mov rax, 0              # read()
syscall

post_or_get:            # cmp first byte of request to determine if POST or GET
xor rbx, rbx
mov rax, [rsp]
and rax, 0xff
cmp al, 0x47
je setupGET

setupPOST:
mov rbx, 2
add rsp, 5
xor rcx, rcx
mov rsi, rsp
mov rdx, rsp            # stack pointer into rdx
add rdx, 0x0200         # store @ 0x0200 on stack
jmp parse_path

setupGET:
mov rbx, 1
add rsp, 4
xor rcx, rcx
mov rsi, rsp
mov rdx, rsp
add rdx, 0x0200

parse_path:
mov rax, [rsi+rcx]      # grab value from ??
and rax, 0xff           # move to rax and and
cmp al, 0x20            # compare to space
je parse_content_setup
mov [rdx], al           # move value into rdx
add rdx, 1              # if not space inc variable slot
inc rcx
jmp parse_path          # loop

parse_content_setup:
cmp rbx, 1              # check if GET or POST request
je open_for_read
mov r10, rcx            # r10 = size of path?
xor rcx, rcx
xor rbx, rbx
mov r9, rdx             # r9 = PATH on STACK ????
mov rdx, rsp
mov rsi, rsp
add rsi, 0x0800         # store content @ 0x0800

parse_content:
mov rax, [rdx+rcx]
and rax, 0xff
inc rcx
cmp al, 0x0d            # if \r
jne reset
mov rax, [rdx+rcx]
and rax, 0xff
inc rcx
cmp al, 0x0a            # if \n
jne parse_content
inc rbx
cmp rbx, 2
jne parse_content
add rdx, rcx
xor rcx, rcx
jmp pc_final

reset:
mov rbx, 0
jmp parse_content

pc_final:
mov rax, [rdx+rcx]
and rax, 0xff
cmp al, 0x00
je open_for_write
mov [rsi], al
inc rsi
inc rcx
jmp pc_final

open_for_write:
mov r8, rdi
mov rdi, r9             # this can be changed to rsp + 0x0200? 
sub rdi, r10
mov r9, rcx             # size of write stored in r9
mov rsi, 00000101
mov rdx, 0777
mov rax, 2
syscall

write_content_to_file:
mov rdi, rax
mov rsi, rsp
add rsi, 0x0800
mov rdx, r9
mov rax, 1
syscall
# close file
mov rax, 3
syscall
mov rdi, r8
call write_200
jmp exit

open_for_read:
mov rdi, rsp
add rdi, 0x0200
mov rsi, 0
mov rax, 2
syscall
# read
mov rdi, rax
mov rsi, rsp
add rsi, 0x1000
mov rdx, 1024
mov rax, 0
syscall
# close
mov rax, 3
syscall
mov rdi, r9
call write_200

xor rcx, rcx
mov rsi, rsp
add rsi, 0x1000

get_sz_file:
mov rax, [rsi+rcx]
and rax, 0xff
cmp al, 0x00
je write_to_http
inc rcx
jmp get_sz_file

write_to_http:
mov rdx, rcx
mov rax, 1
syscall

#close
mov rax, 3
syscall

exit:
xor rdi, rdi
xor rsi, rsi
xor rdx, rdx
mov rax, 60
syscall

write_200: # 200 OK
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
mov rsi, rsp
mov rdx, 19
mov rax, 1
syscall
add rsp, 20
ret
