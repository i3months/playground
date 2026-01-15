#include <stdio.h>
#include <stdlib.h>

int main() {
    volatile unsigned long long count = 0;
    unsigned long long limit = 10000000; 

    for (count = 0; count < limit; count++) {
    }

    printf("Finish: %llu\n", count);
    return 0;
}