#include <stdio.h>

int main(int argc, char* argv[]) {
  FILE* fp = fopen("test.txt", "w");

  int descriptor = fileno(fp);

  fprintf(fp, "hello world\n");

  printf("the descriptor number of fp: %d\n", descriptor);

  fclose(fp);

  return 0;
}