#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main(int argc, char* argv[]) {
  printf("Hello from C!\n");

  int childPid = fork();

  if (childPid == -1) {
    fprintf(stderr, "Something happened with forking...");
    exit(1);
  }

  if (!childPid) {
    // child process
    execle("/home/roger/.volta/bin/node", "/home/roger/.volta/bin/node", "index.js", NULL, NULL);
  } else {
    int childStatus;
    // parent process
    waitpid(childPid, &childStatus, 0);
    printf("Child process exit code: %d\n", WEXITSTATUS(childStatus));
  }

  printf("Goodbye from C!\n");
  return 0;
}
