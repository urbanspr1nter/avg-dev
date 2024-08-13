#include <stdio.h>

int main(int argc, char* argv[]) {
    // %p vs %d
    int x = 1227;

    int *a = &x;
    long int b = &x;

    printf("The address of x as a base 16 number: %p\n", a);
    printf("The address of x as a base 10 number: %ld\n", a);
    printf("The number %ld\n", b);

    // print out what's inside a
    printf("The value inside a is: %d\n", *a);

    int *c = a;
    printf("The address of a is: %p\n", a);
    printf("The address of c is: %p\n", c);
    printf("The value at a is: %d, and the value at c is %d\n", *a, *c);

    x = 5;
    printf("The value at x is %d\n", x);
    printf("The value at a is now: %d and c is is now: %d\n", *a, *c);

    *a = 78;
    printf("The value at a is: %d\n", *a);
    printf("The value of x is: %d\n", x);
    printf("The value of c is: %d\n", *c);

    *c = 123;
    printf("The value at a is: %d\n", *a);
    printf("The value of x is: %d\n", x);
    printf("The value of c is: %d\n", *c);

    return 0;
}