#ifndef STACK_H
#define STACK_H

#include <stdbool.h>

typedef struct Stack {
  int* data;
  int topIdx;
  int capacity;
} Stack;

void stack_push(Stack* stack, int item);
bool stack_isEmpty(Stack* stack);
int stack_peek(Stack* stack);
int stack_pop(Stack* stack);
void stack_emptyAndPrint(Stack* stack);

#endif