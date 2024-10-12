#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "dyarray.h"

Value* dyarr_get(DynamicArray* curr, int index) {
  if (index < 0 || index >= curr->length) {
    fprintf(stderr, "Index out of range.\n");
    exit(1);
  }

  return curr->data + index; 
}

void dyarr_free(DynamicArray* curr) {
  for (int i = 0; i < curr->length; i++) {
    Value* currElement = dyarr_get(curr, i);
    free(currElement->name);
  }

  free(curr->data);

  curr->data = NULL;
  curr->length = 0;
  curr->capacity = 0;
}

void dyarr_initialize(DynamicArray* curr, int initialCapacity) {
  curr->capacity = initialCapacity;
  curr->length = 0;
  curr->data = (Value*)malloc(sizeof(Value) * initialCapacity);
}

void dyarr_set(DynamicArray* curr, int index, char* value) {
  if (index >= curr->length || index < 0) {
    fprintf(stderr, "Index out of bounds in dyarr_set\n");
    exit(1);
  }

  (curr->data + index)->name = value;
}

void dyarr_push(DynamicArray* curr, char* item) {
  // resize if needed
  float loadFactor = (float)curr->length / curr->capacity;
  if (loadFactor >= 0.5) {
    Value* newData = (Value*)malloc(2 * curr->capacity * sizeof(Value));

    for (int i = 0; i < curr->length; i++) {
      Value copiedValue = { .name = strdup((curr->data + i)->name) };
      *(newData + i) = copiedValue;
    }

    for (int i = 0; i < curr->length; i++) {
      Value* currElement = dyarr_get(curr, i);
      free(currElement->name);
    }
    free(curr->data);
    

    curr->data = newData;
    curr->capacity = 2 * curr->capacity;
  }

  Value newValue = {.name = item};
  *(curr->data + curr->length) = newValue;
  curr->length = curr->length + 1;
}

