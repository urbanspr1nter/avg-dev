#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

struct A {
    uint32_t a;
    uint64_t b;
    char c;
    uint32_t d;
    bool e;
};

struct B {
    uint64_t b;
    uint32_t a;
    uint32_t d;
    char c;
    bool e;
};

struct D {
    char a;
    bool b;
    bool c;
};

int main(void) {
    size_t size_a = sizeof(struct A);
    printf("Size of struct A: %d\n", size_a);

    size_t size_b = sizeof(struct B);
    printf("Size of struct B: %d\n", size_b);

    size_t size_d = sizeof(struct D);
    printf("Size of struct D: %d\n", size_d);

/*     struct D arr_d[3];
    size_t size_arr_d = sizeof(arr_d);
    printf("Size of arr of struct D: %d, base address: %p\n", size_arr_d, arr_d);

    struct A arr_a[3];
    size_t size_arr_a = sizeof(arr_a);
    printf("Size of arr of struct A: %d, base address: %p\n", size_arr_a, arr_a); */

    struct D* arr_d = malloc(sizeof(struct D) * 3);
    printf("Size of array of struct D: %d, address: %p\n", sizeof(struct D) * 3, arr_d);

    struct A* arr_a = malloc(sizeof(struct A) * 3);
    printf("Size of array of struct A: %d, address: %p\n", sizeof(struct A) * 3, arr_a);

    return 0;
}
