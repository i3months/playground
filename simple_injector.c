/* * simple_injector.c - A Native Fault Injector for ARM64 (Marvin Implementation)
 * Fixed header conflicts for Raspberry Pi OS
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
 #include <linux/elf.h> // NT_PRSTATUS 정의를 위해 필요할 수 있음
 
 /* * ARM64의 레지스터 구조체를 직접 정의하여 사용합니다.
  * <sys/user.h>와 충돌할 경우 이름을 'my_user_pt_regs'로 바꾸세요.
  */
 struct user_pt_regs_arm64 {
     __u64 regs[31];
     __u64 sp;
     __u64 pc;
     __u64 pstate;
 };
 
 int main(int argc, char *argv[]) {
     pid_t target_pid;
     struct user_pt_regs_arm64 regs; // 이름 변경
     struct iovec iov;
     
     if (argc < 2) {
         fprintf(stderr, "Usage: %s <target_program>\n", argv[0]);
         exit(1);
     }
 
     srand(time(NULL));
 
     // 1. Fork a child process
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
 
         // Randomly skip instructions
         long instructions_to_skip = rand() % 5000;
         for(int i=0; i < instructions_to_skip; i++) {
              ptrace(PTRACE_SINGLESTEP, target_pid, 0, 0);
              waitpid(target_pid, &status, 0);
         }
 
         // 2. Read Registers
         iov.iov_base = &regs;
         iov.iov_len = sizeof(regs);
         ptrace(PTRACE_GETREGSET, target_pid, NT_PRSTATUS, &iov);
 
         // 3. Inject Fault (Bit-flip in x1)
         int target_reg = 1; 
         int target_bit = rand() % 64; 
         
         // printf("[Marvin] Flipping x%d bit %d\n", target_reg, target_bit);
         regs.regs[target_reg] ^= (1ULL << target_bit);
 
         // 4. Write back
         ptrace(PTRACE_SETREGSET, target_pid, NT_PRSTATUS, &iov);
 
         // 5. Continue
         ptrace(PTRACE_CONT, target_pid, 0, 0);
         
         waitpid(target_pid, &status, 0);
     }
     return 0;
 }