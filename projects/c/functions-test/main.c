#include <stdio.h>

void print_hello() {
    printf("Hello, world!\n");

    return; 
}

int get_double_of_y(int y) {
    int doubled = y * 2;

    return doubled;
}

int main() {
    print_hello();

    int double_of_7 = get_double_of_y(7);
    printf("%d\n", double_of_7);

    return 0;
}
