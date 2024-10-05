#include <stdio.h>
#include <stdlib.h>
#include "stack.h"

int main(int argc, char* argv[]) {
  Node* stack = NULL;

  stack = stack_push(stack, 1);
  stack = stack_push(stack, 3);
  stack = stack_push(stack, 5);
  stack = stack_push(stack, 9);

  while (!stack_isEmpty(stack)) {
    int popped = stack_pop(&stack);
    printf("%d\n", popped);
  }

  stack_empty(stack);

  return 0;
}