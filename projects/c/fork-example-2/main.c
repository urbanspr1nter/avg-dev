#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main(int argc, char* argv[]) {
    int status;
    pid_t child_pid = fork();
    if (child_pid == -1) {
        fprintf(stderr, "Can't fork.\n");
        exit(1);
    }

    if (child_pid == 0) {
        char* args[] = {argv[1], NULL};
        int exec_result = execvp(argv[1], args);
        if (exec_result != 0) {
            fprintf(stderr, "Could not exec\n.");
            exit(1);
        } 
    } else {
        printf("I am the parent.\n");
        waitpid(child_pid, &status, 0);
    }


    return 0;    
}