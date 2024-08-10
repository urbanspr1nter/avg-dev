#include <stdio.h>

int main(int argc, char* argv[]) {
    printf("Number of arguments: %d\n", argc);
    
    for(int arg_idx = 0; arg_idx < argc; arg_idx++) {
        printf(
            "The current value at index %d: %s\n", 
            arg_idx,
            argv[arg_idx]
        );
    }

    return 0;
}