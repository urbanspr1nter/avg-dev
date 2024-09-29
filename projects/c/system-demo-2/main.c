#include <stdio.h>
#include <stdlib.h>
#include <time.h>

char* now() {
  time_t t;
  time(&t);
  return asctime(localtime(&t));
}

int main(int argc, char* argv[]) {
  char comment[80];
  char cmd[120];

  fgets(comment, 80, stdin);
  sprintf(cmd, "echo '%s %s' >> reports.log", comment, now());

  printf("The command to be run is: %s\n", cmd);

  system(cmd);
  return 0;
}
