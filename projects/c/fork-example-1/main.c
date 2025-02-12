#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int expensive_work(int y) {
    sleep(5);

    int a = y * 2;

    return a;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: ./a.out NUMBER\n");
        exit(1);
    }

    int x = atoi(argv[1]);

    int status = 0;
    pid_t child_pid = fork();
    if (child_pid == -1) {
        fprintf(stderr, "Could not fork.\n");
        exit(1);
    }

    if (child_pid == 0) {
        printf("x: %d, Child pid: %d, this is the child\n", x, child_pid);
        int result = expensive_work(123);
        printf("HELLO!!! %d\n", result);
        exit(23);
    } else {
        printf("x: %d, Child pid: %d, this is the parent\n", x, child_pid);
        waitpid(child_pid, &status, 0);
        printf("Child has exited with status: %d\n", WEXITSTATUS(status));
    }

    return 0;
}