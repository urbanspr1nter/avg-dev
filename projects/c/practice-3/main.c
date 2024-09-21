#include <stdio.h>
#include <stdlib.h>

void printIntArray(int d[], int len) {
  for (int i = 0; i < len; i++) {
    printf("%i\n", d[i]);
  }
}

int main(int argc, char* argv[]) {
  if (argc < 2) {
    fprintf(stderr, "Not enough arguments. Usage: ./a.out NUMBER\n");
    return 1;
  }

  char*  lengthAsString = argv[1];
  int length = atoi(lengthAsString);

  int* data = (int*)malloc(length * sizeof(int));
  if (data == NULL) {
    fprintf(stderr, "Not enough memory.");
  }
 
  for (int i = 0; i < length; i++) {
    *(data + i) = 1;
  }

  int j = 0;
  while (j < length) {
    *(data + j) = (*(data + j) + j) * 10;
    j++;
  }

  printIntArray(data, length);
  
  free(data);
  return 0;
}