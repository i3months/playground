/* 
 * simple_injector_v2.c - Simplest version (inject at start only)
 */

#include <stdio.h>
#include <stdlib.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <sys/uio.h> 
#include <unistd.h>
#include <time.h>
#include <linux/elf.h>

struct user_pt_regs_arm64 {
    __u64 regs[31];
    __u64 sp;
    __u64 pc;
    __u64 pstate;
};

int main(int argc, char *argv[]) {
    pid_t target_pid;
    struct user_pt_regs_arm64 regs; 
    struct iovec iov;
    
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <target_program>\n", argv[0]);
        exit(1);
    }

    srand(time(NULL) ^ getpid());

    target_pid = fork();

    if (target_pid == 0) {
        // [Child Process]
        ptrace(PTRACE_TRACEME, 0, NULL, NULL);
        execl(argv[1], argv[1], NULL);
        exit(1);
    } else {
        // [Parent Process]
        int status;
        
        // Wait for child start
        waitpid(target_pid, &status, 0);
        
        // Read Registers
        iov.iov_base = &regs;
        iov.iov_len = sizeof(regs);
        ptrace(PTRACE_GETREGSET, target_pid, NT_PRSTATUS, &iov);
        
        // Inject Fault (random register at start)
        int target_reg = rand() % 8;
        int target_bit = rand() % 64;
        regs.regs[target_reg] ^= (1ULL << target_bit);
        
        // Write back
        ptrace(PTRACE_SETREGSET, target_pid, NT_PRSTATUS, &iov);
        
        // Continue
        ptrace(PTRACE_CONT, target_pid, 0, 0);
        waitpid(target_pid, &status, 0);
    }
    return 0;
}
