#include <stdio.h>
#include <string.h>
#include <stdlib.h>

char* reverse(char* input) {
  int len = strlen(input) + 1;

  char* workingString = strndup(input, len * sizeof(char));
  if (workingString == NULL) {
    fprintf(stderr, "Can't create memory for string\n");
    exit(1);
  }

  // reverse the string
  for (int i = 0, j = len - 2; i <= j; i++, j--) {
    char t = workingString[i];
    workingString[i] = workingString[j];
    workingString[j] = t;
  }

  return workingString;
}

int main(int argc, char* argv[]) {
  if (argc < 2) {
    fprintf(stderr, "./a.out \"string to reverse\"\n");
    return 1;
  }

  char* buf = argv[1];
  char* maybeNewLinePointer = strchr(buf, '\n');
  if (maybeNewLinePointer != NULL) {
    *maybeNewLinePointer = '\0';
  }

  char* reversedString = reverse(buf);
  
  puts(reversedString);

  free(reversedString);

  return 0;
}