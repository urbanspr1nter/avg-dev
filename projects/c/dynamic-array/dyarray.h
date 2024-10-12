#ifndef DYARRAY_H
#define DYARRAY_H

typedef struct Value {
  char* name;
} Value;

typedef struct DynamicArray {
  // the block of heap memory containing the collection of Values
  Value* data;

  // the current number of elements of the array
  int length;

  // total number of element of which data can grow to
  int capacity; 
} DynamicArray;

Value* dyarr_get(DynamicArray* curr, int index);
void dyarr_free(DynamicArray* curr);
void dyarr_initialize(DynamicArray* curr, int initialCapacity);
void dyarr_set(DynamicArray* curr, int index, char* item);
void dyarr_push(DynamicArray* curr, char* item);


#endif