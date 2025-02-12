#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>

#define MAX_LINE_SIZE 256

// vim
void runProgram(char* name) {
	pid_t childPid = fork();
	
	if (childPid == 0) {
		printf("child is here\n");
		// this is the child
		char** args = malloc(sizeof(char*) * 2);
		if (args == NULL) {
			fprintf(stderr, "Not enough memory!\n");
			exit(1);
		}

		*(args + 0) = name;
		*(args + 1) = (char*)NULL;

		int execStatus = execvp(name, args);
		if (execStatus == -1) {
			printf("ERROR!!!!!\n");
		}
		
	} else {
		// this is the parent because childPid is something
		printf("CHILD PID: %d\n", childPid);
		
		int status;
		do {
			waitpid(childPid, &status, WUNTRACED);
		} while (!WIFEXITED(status) && !WIFSIGNALED(status));
	}
}

int main(void) {
	char* input = malloc(sizeof(char) * MAX_LINE_SIZE);
	char* result = malloc(sizeof(char) * MAX_LINE_SIZE);

	bool keepPrompting = true;
	while (keepPrompting) {
		printf("$ ");
		fgets(input, MAX_LINE_SIZE, stdin);
		sscanf(input, "%s", result);
		*(result + strlen(result)) = '\0';

		////
		if (strcmp(result, "exit") == 0) {
			keepPrompting = false;
		} else {
			runProgram(result);
		}

	}

	return 0;
}
