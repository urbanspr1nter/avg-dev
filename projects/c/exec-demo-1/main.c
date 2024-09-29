#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

int main(int argc, char* argv[]) {
  char* programName = "cat";

  execlp(programName, programName, "test.txt", NULL);
  
  // This only executes if the execle call fails
  puts("The execlp call failed!");
  printf("The errno is: %i\n", errno);
  printf("errno message: %s\n",strerror(errno));
  
  return 0;
}