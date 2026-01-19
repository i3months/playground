/* 
 * simple_runner.c - Run program with ptrace (NO fault injection)
 * For collecting normal HPC data with same overhead as fault injection
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

    srand(time(NULL));

    // Fork a child process
    target_pid = fork();

    if (target_pid == 0) {
        // [Child Process]
        ptrace(PTRACE_TRACEME, 0, NULL, NULL);
        execl(argv[1], argv[1], NULL);
    } else {
        // [Parent Process]
        int status;
        
        // Wait for child start
        waitpid(target_pid, &status, 0);

        // Skip same number of instructions (for consistency)
        long instructions_to_skip = rand() % 5000;
        for(int i=0; i < instructions_to_skip; i++) {
             ptrace(PTRACE_SINGLESTEP, target_pid, 0, 0);
             waitpid(target_pid, &status, 0);
        }

        // Read Registers (but don't modify)
        iov.iov_base = &regs;
        iov.iov_len = sizeof(regs);
        ptrace(PTRACE_GETREGSET, target_pid, NT_PRSTATUS, &iov);

        // NO FAULT INJECTION - just continue
        ptrace(PTRACE_CONT, target_pid, 0, 0);
        
        waitpid(target_pid, &status, 0);
    }
    return 0;
}
