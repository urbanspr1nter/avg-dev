#include <stdio.h>

int main(int argc, char *argv[]) {
    char first_name[80];
    char last_name[80];
    int age;

    printf("Enter the first and last name along with age.\n");
    scanf("%79s %79s %d", first_name, last_name, &age);

    printf(
        "First: %s, Last: %s, Age: %d\n",
        first_name, last_name, age
    );

    return 0;
}
