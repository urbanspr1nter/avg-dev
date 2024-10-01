#include <stdio.h>
#include <stdlib.h>
#include "stack.h"

/**
 * Pushes an element to the stack
 */
void stack_push(Stack* stack, int item) {
  if (stack->topIdx + 1 >= stack->capacity) {
    fprintf(stderr, "The stack is full!\n");
    exit(1);
  }

  stack->topIdx = stack->topIdx + 1;
  *(stack->data + stack->topIdx) = item;
}

/**
 * Tells us if the stack is empty
 */
bool stack_isEmpty(Stack* stack) {
  if (stack->topIdx == -1) {
    return true;
  }

  return false;
}

/**
 * Returns whatever is on top of the stack
 */
int stack_peek(Stack* stack) {
  if (stack_isEmpty(stack)) {
    fprintf(stderr, "Attempting to peek at an empty stack!\n");
    exit(1);
  }

  return *(stack->data + stack->topIdx);
}

/**
 * Removes the element at the top of the stack, and returns it.
 */
int stack_pop(Stack* stack) {
  if (stack_isEmpty(stack)) {
    fprintf(stderr, "Attempting to pop an empty stack!\n");
    exit(1);
  }
  int t = stack_peek(stack);
  stack->topIdx = stack->topIdx - 1;
  return t;
}

void stack_emptyAndPrint(Stack* stack) {
  while (!stack_isEmpty(stack)) {
    int popped = stack_pop(stack);
    printf("Value popped: %i\n", popped);
  }

  printf("EMPTY STACK!!!\n");
}
