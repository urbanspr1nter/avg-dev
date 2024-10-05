#ifndef STACK_H
#define STACK_H

#include <stdbool.h>

typedef struct Node {
  int value;
  struct Node* next;
} Node;

Node* stack_createNode(int value);
Node* stack_push(Node* top, int value);
bool stack_isEmpty(Node* top);
int stack_pop(Node** top); 
int stack_peek(Node* top);
void stack_empty(Node* top);
void stack_print(Node* top);

#endif