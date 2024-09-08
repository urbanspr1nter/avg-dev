#include <stdio.h>

void swap_string(char** a, char** b) {
  char* c = *a;
  *a = *b;
  *b = c;
}

int main() {
  char* x = "hi!";
  char* y = "bye";

  printf("x = %s\n", x); // hi!
  printf("y = %s\n", y); // bye

  swap_string(&x, &y);

  printf("x = %s\n", x); // bye
  printf("y = %s\n", y); // hi!

  return 0;
}