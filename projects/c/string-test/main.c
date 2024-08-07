#include <stdio.h>

int main() {
    char s[] = "Shatner";

    printf("%s\n", s);

    printf("[%c]\n", s[0]);
    printf("[%c]\n", s[1]);

    printf("[%c]\n", s[6]);

    printf("[%c]\n", s[7]);

    s[0] = 'S';
    printf("%s\n", s);

    s[0] = 'H';
    printf("%s\n", s);

    printf("At index 891: [%c]\n", s[891]);

    s[7] = 'a';

    printf("The string after replacing NULL character: [%s]\n", s);

    s[4] = '\0';

    printf("%s\n", s);

    return 0;
}
