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

void dyarr_push(DynamicArray* curr, int item) {
  // resize if needed
  float loadFactor = (float)curr->length / curr->capacity;
  if (loadFactor >= 0.5) {
    int* newData = (int*)malloc(2 * curr->capacity * sizeof(int));

    for (int i = 0; i < curr->length; i++) {
      *(newData + i) = *(curr->data + i);
    }

    free(curr->data);

    curr->data = newData;
    curr->capacity = 2 * curr->capacity;
  }

  *(curr->data + curr->length) = item;
  curr->length = curr->length + 1;
}

int dyarr_get(DynamicArray* curr, int index) {
  if (index < 0 || index >= curr->length) {
    fprintf(stderr, "Index out of range.\n");
    exit(1);
  }

  return *(curr->data + index); 
}

int main(int argc, char* argv[]) {
  DynamicArray w = {.data = NULL, .length = 0, .capacity = 0};
  dyarr_initialize(&w, 3);

  for (int i = 0; i < 100000000; i++) {
    dyarr_push(&w, 888);
    printf("Length of array: %d, Capacity: %d\n", w.length, w.capacity);
  }

  for (int i = 0; i < w.length; i++) {
    // printf("%d\n", dyarr_get(&w, i));
  }

  return 0;
}