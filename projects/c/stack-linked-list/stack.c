#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "stack.h"

/**
 * Creates a node ready to be pushed into the
 * stack.
 */
Node* stack_createNode(int value) {
  Node* n = (Node*)malloc(sizeof(Node)); 
  n->value = value;
  n->next = NULL;

  return n;
}

/**
 * Pushes the value to the top of the stack
 * returns a reference to the new top of the stack
 */
Node* stack_push(Node* top, int value) {
  if (top == NULL) {
    top = stack_createNode(value);
    return top;
  }

  Node* n = stack_createNode(value);

  n->next = top;
  top = n;

  return top;
}

/**
 * Returns true if the given stack is empty
 * false otherwise.
 */
bool stack_isEmpty(Node* top) {
  return top == NULL;
}

/**
 * Returns the value at the top of the stack 
 * and removes it from the stack
 */
int stack_pop(Node** top) {
  if (stack_isEmpty(*top)) {
    fprintf(stderr, "Cannot pop an empty stack.\n");
    exit(1);
  }

  Node* prevTop = *top;
  *top = (*top)->next;

  int result = prevTop->value;

  // Remove the node from heap
  // it is dangling.
  free(prevTop);

  return result;
}

/**
 * Returns the top of the stack, but does not
 * remove the value from the stack.
 */
int stack_peek(Node* top) {
  if (stack_isEmpty(top)) {
    fprintf(stderr, "Cannot peek at an empty stack\n");
    exit(1);
  }
  return top->value;
}

/**
 * Frees allocated memory from the stack.
 */
void stack_empty(Node* top) {
  Node* t = top;
  while (top != NULL) {
    t = top;
    top = top->next;
    free(t);
  }
}

/**
 * Prints the contents of the stack
 */
void stack_print(Node* top) {
  Node* t = top;

  while (t != NULL) {
    printf("%d -> ", t->value);
    t = t->next;
  }
  printf("NULL\n");
}