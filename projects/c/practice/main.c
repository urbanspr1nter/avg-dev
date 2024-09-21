#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void reverse(char* original, char* result) {
  int len = strlen(original) + 1;
  
  // copy
  for (int i = 0; i < len; i++) {
    result[i] = original[i];
  }
  result[len - 1] = '\0';

  for (int i = 0, j = len - 2; i <= j; i++, j--) {
    char t = result[i];
    result[i] = result[j];
    result[j] = t;
  }
}

int main(int argc, char* argv[]) {
  char buf[80];
  char result[80];
  
  printf("What is your string? ");
  fgets(buf, 80, stdin);

  char* indexOfNewLineCharacter = strchr(buf, '\n');
  if (indexOfNewLineCharacter != NULL) {
    *indexOfNewLineCharacter = '\0';
  }

  reverse(buf, result);
  
  printf("Reversed: %s\n", result);

  return 0;
}