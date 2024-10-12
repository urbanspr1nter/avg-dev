#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "dyarray.h"

int main(int argc, char* argv[]) {
  DynamicArray w = {.data = NULL, .length = 0, .capacity = 0};
  dyarr_initialize(&w, 3);

  for (int i = 0; i < 16; i++) {
    char* t = strdup("Hello");
    dyarr_push(&w, t);
    // printf("Length of array: %d, Capacity: %d\n", w.length, w.capacity);
  }
 
  for (int i = 0; i < w.length; i++) {
    printf("%s\n", dyarr_get(&w, i)->name);
  }
  printf("--------------\n");
  

  char* world = strdup("World");
  dyarr_set(&w, 10, world);

  for (int i = 0; i < w.length; i++) {
    printf("%s\n", dyarr_get(&w, i)->name);
  }

  dyarr_free(&w);

  return 0;
}