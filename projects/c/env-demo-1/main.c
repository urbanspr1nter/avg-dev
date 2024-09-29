#include <stdio.h>
#include <stdlib.h>

int main(int argc, char* argv[]) {
  char* portAsString = getenv("PORT");
  if (portAsString == NULL) {
    portAsString = "3000";
  }

  int port = atoi(portAsString);

  printf("The port number is: %i\n", port);

  return 0;
}