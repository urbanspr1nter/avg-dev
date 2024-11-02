#include <stdio.h>

typedef struct Node {
  int value;
  struct Node* left;
  struct Node* right;
} Node;

void doSomething(Node* currRoot) {
  printf("%d, ", currRoot->value);
}

void inorder(Node* currRoot) {
  if (currRoot == NULL) {
    return;
  }

  inorder(currRoot->left);
  doSomething(currRoot);
  inorder(currRoot->right);
}

void preorder(Node* currRoot) {
  if (currRoot == NULL) {
    return;
  }

  doSomething(currRoot);
  preorder(currRoot->left);
  preorder(currRoot->right);
}

void postorder(Node* currRoot) {
  if (currRoot == NULL) {
    return;
  }

  postorder(currRoot->left);
  postorder(currRoot->right);
  doSomething(currRoot);
}

int main(int argc, char* argv[]) {
  Node nRoot = {.value = 20, .left = NULL, .right = NULL};
  Node n10 = {.value = 10, .left = NULL, .right = NULL};
  Node n30 = {.value = 30, .left = NULL, .right = NULL};
  Node n5 = {.value = 5, .left = NULL, .right= NULL};
  Node n15 = {.value = 15, .left = NULL, .right = NULL};
  Node n25 = {.value = 25, .left = NULL, .right = NULL};
  Node n35 = {.value = 35, .left = NULL, .right = NULL};

  nRoot.left = &n10;
  nRoot.right = &n30;

  n10.left = &n5;
  n10.right = &n15;

  n30.left = &n25;
  n30.right = &n35;


  // Test the inorder traversal
  // 5, 10, 15, 20, 25, 30, 35,
  puts("Inorder traversal");
  inorder(&nRoot);
  printf("\n");

  puts("Preorder traversal");
  preorder(&nRoot);
  printf("\n");


  puts("Postorder traversal");
  postorder(&nRoot);
  printf("\n");

  return 0;
}