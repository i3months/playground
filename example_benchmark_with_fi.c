/* Benchmark with Software-based Fault Injection */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <string.h>

// Fault Injection 설정
static int FAULT_ENABLED = 0;
static int fault_injected = 0;
static unsigned long instruction_count = 0;
static unsigned long fault_trigger_point = 0;

// Fault Injection 초기화
void init_fault_injection() {
    char *env = getenv("ENABLE_FAULT");
    if (env && strcmp(env, "1") == 0) {
        FAULT_ENABLED = 1;
        srand(time(NULL) ^ getpid());
        // 10K~60K instruction 사이에 fault 발생
        fault_trigger_point = 10000 + (rand() % 50000);
    }
}

// Fault Injection 체크 (각 함수에서 호출)
#define CHECK_FAULT() do { \
    if (FAULT_ENABLED && !fault_injected) { \
        instruction_count++; \
        if (instruction_count >= fault_trigger_point) { \
            inject_fault(); \
        } \
    } \
} while(0)

// 실제 Fault Injection
void inject_fault() {
    fault_injected = 1;
    // 이 함수는 각 벤치마크에서 실제 변수를 조작하도록 호출됨
}

// 전역 변수 (벤치마크에서 사용)
static double global_a = 0.0;
static double global_b = 0.0;
static int global_arr[1000];

// Fault injection 헬퍼
void inject_fault_to_double(double *var) {
    if (FAULT_ENABLED && !fault_injected) {
        instruction_count++;
        if (instruction_count >= fault_trigger_point) {
            fault_injected = 1;
            unsigned long long *ptr = (unsigned long long*)var;
            int bit = rand() % 64;
            *ptr ^= (1ULL << bit);
        }
    }
}

void inject_fault_to_int(int *var) {
    if (FAULT_ENABLED && !fault_injected) {
        instruction_count++;
        if (instruction_count >= fault_trigger_point) {
            fault_injected = 1;
            int bit = rand() % 32;
            *var ^= (1 << bit);
        }
    }
}

// BasicMath 벤치마크
void basicmath_test() {
    double a = 1.5, b = 2.5, result;
    
    for (int i = 0; i < 100000; i++) {
        // Fault injection to actual variables
        inject_fault_to_double(&a);
        inject_fault_to_double(&b);
        
        result = sqrt(a * b);
        result = sin(result);
        result = cos(result);
        result = tan(result);
        
        a += 0.001;
        b += 0.002;
    }
}

// Qsort 벤치마크
void qsort_test() {
    int arr[1000];
    
    for (int i = 0; i < 1000; i++) {
        arr[i] = rand();
    }
    
    for (int i = 0; i < 100; i++) {
        // Bubble sort
        for (int j = 0; j < 999; j++) {
            for (int k = 0; k < 999 - j; k++) {
                // Fault injection to array element
                inject_fault_to_int(&arr[k]);
                
                if (arr[k] > arr[k+1]) {
                    int temp = arr[k];
                    arr[k] = arr[k+1];
                    arr[k+1] = temp;
                }
            }
        }
    }
}

int main() {
    init_fault_injection();
    
    #ifdef BENCHMARK
    #if BENCHMARK == 1
        basicmath_test();
    #elif BENCHMARK == 2
        qsort_test();
    #else
        basicmath_test();
    #endif
    #else
        basicmath_test();
    #endif
    
    return 0;
}
