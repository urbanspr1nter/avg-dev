
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

char* make_filename(int i, char buffer[]) {
    char* prefix = "work-";
    char id = '0' + i;
    char* suffix = ".txt";

    sprintf(buffer, "%s%c%s", prefix, id, suffix);

    return buffer;
}

int expensive_fn(int v) {
    sleep(5);
    return v * 113;
}

int main(void) {
    pid_t children_pid[100];
    int statuses[100];

    for (int i = 0; i < 100; i++) {
        printf("Processing at %d\n", i);
        children_pid[i] = fork();
        if (children_pid[i] == -1) {
            fprintf(stderr, "Could not fork.\n");
            exit(1);
        }

        if (children_pid[i] == 0) {
            char buffer[15];
            FILE* fp = fopen(make_filename(i, buffer), "w");
            int result = expensive_fn(i);
            fprintf(fp, "%d", result);
            fclose(fp);

            exit(0);
        }
    }

    for (int i = 0; i < 100; i++) {
        waitpid(children_pid[i], &statuses[i], 0);
    }

    int sum = 0;
    for (int i = 0; i < 100; i++) {
        char buffer[15];
        FILE* fp = fopen(make_filename(i, buffer), "r");

        char data_buffer[80];
        fgets(data_buffer, 80, fp);

        sum += atoi(data_buffer);

        fclose(fp);
    }

    printf("Result: %d\n", sum);

    return 0;
}