#include <stdio.h>
#include <stdlib.h>

typedef struct DynamicArray {
  // the block of heap memory containing the collection of ints
  int* data;
  
  // the current number of elements of the array
  int length;

  // total number of element of which data can grow to
  int capacity; 
} DynamicArray;

void dyarr_initialize(DynamicArray* curr, int initialCapacity) {
  curr->capacity = initialCapacity;
  curr->length = 0;
  curr->data = (int*)malloc(sizeof(int) * initialCapacity);
}

int main(int argc, char* argv[]) {
  DynamicArray w = {.data = NULL, .length = 0, .capacity = 0};
  dyarr_initialize(&w, 3);

  *(w.data + 0) = 7;

  printf("Dynamic array information: first element: %i, length: %i, capacity: %i\n", *w.data, w.length, w.capacity);

  return 0;
}