#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "stack.h"

int main(int argc, char* argv[]) {
  // --------- Initialize the Stack ---------
  // Allocate memory to represent a "Stack"
  Stack* myStack = (Stack*)malloc(sizeof(Stack));
  myStack->capacity = 10;

  // Allocate memory to represent our collection of items
  myStack->data = (int*)malloc(myStack->capacity * sizeof(int));

  // Set topIdx to -1
  myStack->topIdx = -1;
  // -----------------------------------------

  stack_push(myStack, 8);
  printf("peek: %i\n", stack_peek(myStack));

  stack_push(myStack, 3);
  printf("peek: %i\n", stack_peek(myStack));

  stack_push(myStack, 6);
  printf("peek: %i\n", stack_peek(myStack));

  stack_emptyAndPrint(myStack);

  free(myStack->data);
  free(myStack);

  return 0;
}
