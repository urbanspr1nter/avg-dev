#include <stdio.h>

int main() {
    int current_count = 0;

    while (current_count <= 10) {
        if (current_count == 6) {
            current_count++;
            continue;
        }

        printf("%d\n", current_count);
        current_count++;
    }

    return 0;
}