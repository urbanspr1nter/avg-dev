#include <stdio.h>

int main(int argc, char* argv[]) {
    printf("sizeof int: %li\n", sizeof(int));
    printf("sizeof long int: %li\n", sizeof(long int));
    printf("sizeof char: %li\n", sizeof(char));
    printf("sizeof float: %li\n", sizeof(float));
    printf("sizeof double: %li\n", sizeof(double));
    printf("sizeof short: %li\n", sizeof(short));
    printf("sizeof this string \"hello hello\" with the null character: %li\n", sizeof("hello hello"));

    return 0;
}