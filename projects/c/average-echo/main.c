#include <stdio.h>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printf("\n");

        return 0;
    }

    char *value = argv[1];
    printf("%s\n", value);

    return 0;
}
