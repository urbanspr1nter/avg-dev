#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    char first_name[80];
    char last_name[80];
    char age[3];

    printf("Please enter your first name, last name and age in different lines.\n");
    fgets(first_name, 80, stdin);
    fgets(last_name, 80, stdin);
    fgets(age, 3, stdin);

    char *new_line_occ_first_name = strchr(first_name, '\n');
    if (new_line_occ_first_name != NULL) {
        *new_line_occ_first_name = '\0';
    } 

    char *new_line_occ_last_name = strchr(last_name, '\n');
    if (new_line_occ_last_name) {
        *new_line_occ_last_name = '\0';
    }

    char *new_line_occ_age = strchr(age, '\n');
    if (new_line_occ_age != NULL) {
        *new_line_occ_age = '\0';
    }

    printf(
        "First name: %s, last name: %s, age: %d\n",
        first_name,
        last_name,
        atoi(age)
    );
    
    return 0;
}