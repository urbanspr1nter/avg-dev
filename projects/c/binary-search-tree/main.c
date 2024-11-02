#include <stdio.h>
#include <stdlib.h>

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

Node* createNode(int value) {
  Node* result = (Node*)malloc(sizeof(Node));

  result->value = value;
  result->left = NULL;
  result->right = NULL;

  return result;
}

void insertHelper(Node** root, Node* nodeToInsert) {
  Node *currNode = (*root);
  
  if (currNode->left == NULL 
        && currNode->right == NULL) {

    if (nodeToInsert->value < currNode->value) {
      currNode->left = nodeToInsert;
    } else {
      currNode->right = nodeToInsert;
    }

    return;
  }

  if (currNode->left == NULL 
        && nodeToInsert->value < currNode->value) {
    currNode->left = nodeToInsert;

    return;
  }
  if (currNode->right == NULL 
        && nodeToInsert->value >= currNode->value) {
    currNode->right = nodeToInsert;

    return;
  }
  
  if (nodeToInsert->value < currNode->value) {
    insertHelper(&(currNode->left), nodeToInsert);
  } else {
    insertHelper(&(currNode->right), nodeToInsert);
  }
}

void insert(Node**root, int value) {
  Node* nodeToInsert = createNode(value);

  if (*root == NULL) {
    *root = nodeToInsert;
    return;
  }

  insertHelper(root, nodeToInsert);
}

int main(int argc, char* argv[]) {
  Node* nRoot = NULL;
  int v = 20;

  insert(&nRoot, v);
  insert(&nRoot, 10);
  insert(&nRoot, 30);
  insert(&nRoot, 15);
  insert(&nRoot, 35);
  insert(&nRoot, 5);
  insert(&nRoot, 25);
  insert(&nRoot, 28);

  inorder(nRoot);
  printf("\n");

  return 0;
}