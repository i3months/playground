/*
 * Example Benchmark for Fault Injection
 * Similar to MiBench benchmarks used in Marvin paper
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// Benchmark selection
#define BENCHMARK_BASICMATH 1
#define BENCHMARK_QSORT 2
#define BENCHMARK_SHA 3

#ifndef BENCHMARK
#define BENCHMARK BENCHMARK_BASICMATH
#endif

// ============================================
// Basic Math Benchmark (similar to Marvin)
// ============================================
#if BENCHMARK == BENCHMARK_BASICMATH

double basic_math_compute(int n) {
    double result = 0.0;
    
    for (int i = 1; i <= n; i++) {
        // Square root approximation
        double x = (double)i;
        double sqrt_approx = x / 2.0;
        for (int j = 0; j < 10; j++) {
            sqrt_approx = (sqrt_approx + x / sqrt_approx) / 2.0;
        }
        
        // Trigonometric approximation (Taylor series)
        double angle = (double)i / 1000.0;
        double sin_approx = angle;
        double term = angle;
        for (int j = 1; j < 10; j++) {
            term *= -angle * angle / ((2*j) * (2*j + 1));
            sin_approx += term;
        }
        
        result += sqrt_approx + sin_approx;
    }
    
    return result;
}

int main() {
    printf("Starting Basic Math Benchmark\n");
    
    volatile double result = basic_math_compute(10000);
    
    printf("Result: %.6f\n", result);
    return 0;
}

// ============================================
// Quick Sort Benchmark
// ============================================
#elif BENCHMARK == BENCHMARK_QSORT

void swap(int* a, int* b) {
    int t = *a;
    *a = *b;
    *b = t;
}

int partition(int arr[], int low, int high) {
    int pivot = arr[high];
    int i = (low - 1);
    
    for (int j = low; j <= high - 1; j++) {
        if (arr[j] < pivot) {
            i++;
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i + 1], &arr[high]);
    return (i + 1);
}

void quickSort(int arr[], int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
    }
}

int main() {
    printf("Starting Quick Sort Benchmark\n");
    
    int n = 10000;
    int* arr = (int*)malloc(n * sizeof(int));
    
    // Initialize with random values
    srand(42);  // Fixed seed for reproducibility
    for (int i = 0; i < n; i++) {
        arr[i] = rand() % 10000;
    }
    
    // Sort
    quickSort(arr, 0, n - 1);
    
    // Verify (simple check)
    int sorted = 1;
    for (int i = 0; i < n - 1; i++) {
        if (arr[i] > arr[i + 1]) {
            sorted = 0;
            break;
        }
    }
    
    printf("Result: %s\n", sorted ? "Sorted correctly" : "Sort failed");
    
    free(arr);
    return 0;
}

// ============================================
// SHA-like Hash Benchmark
// ============================================
#elif BENCHMARK == BENCHMARK_SHA

// Simplified SHA-like hash function
unsigned int rotate_left(unsigned int value, int shift) {
    return (value << shift) | (value >> (32 - shift));
}

void sha_like_hash(const unsigned char* data, int len, unsigned int hash[5]) {
    // Initialize hash values
    hash[0] = 0x67452301;
    hash[1] = 0xEFCDAB89;
    hash[2] = 0x98BADCFE;
    hash[3] = 0x10325476;
    hash[4] = 0xC3D2E1F0;
    
    // Process data in chunks
    for (int i = 0; i < len; i++) {
        unsigned int temp = rotate_left(hash[0], 5) + hash[4] + data[i];
        hash[4] = hash[3];
        hash[3] = hash[2];
        hash[2] = rotate_left(hash[1], 30);
        hash[1] = hash[0];
        hash[0] = temp;
    }
}

int main() {
    printf("Starting SHA-like Hash Benchmark\n");
    
    // Create test data
    int data_size = 100000;
    unsigned char* data = (unsigned char*)malloc(data_size);
    for (int i = 0; i < data_size; i++) {
        data[i] = (unsigned char)(i % 256);
    }
    
    // Compute hash
    unsigned int hash[5];
    sha_like_hash(data, data_size, hash);
    
    printf("Hash: %08x %08x %08x %08x %08x\n", 
           hash[0], hash[1], hash[2], hash[3], hash[4]);
    
    free(data);
    return 0;
}

#endif
