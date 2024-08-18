#include <stdio.h>
#include <string.h>

void print_reverse(char* s) {
  size_t len = strlen(s);

  char* t = s + len - 1;

  while (t >= s) {
    printf("%c", *t);
    t = t - 1; 
  }

  puts("");
}


int main(int argc, char* argv[]) {
  if (argc <= 1) {
    printf("Please provide a second argument to reverse.\n");

    return 1;
  }
  
  print_reverse(argv[1]);

  return 0;
}