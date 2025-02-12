#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int expensive_fn(int v) {
    sleep(3);
    return v * 113;
}

int main(void) {
    int sum = 0;

    for (int i = 0; i < 10; i++) {
        printf("Computing at %d\n", i);
        sum += expensive_fn(i);
    }

    printf("Result: %d\n", sum);

    return 0;
}