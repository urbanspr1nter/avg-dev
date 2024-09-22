#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum {
  MALE,
  FEMALE 
} Gender;

typedef struct {
  char* firstName;
  char* lastName;
  short age;
  Gender gender;
  struct Person* next;
} Person;

void printPerson(Person *p) {
  char* maleGender = "Male";
  char* femaleGender = "Female";

  printf("%s %s, %i, %s\n",
    p->firstName,
    p->lastName, 
    p->age, 
    p->gender == MALE ? maleGender : femaleGender
  );
}

void printList(Person* start) {
  Person* t = start;
  while (t != NULL) {
    printPerson(t);
    t = (Person*)t->next;
  }
}

/**
 * This function will allocate memory in the heap to store a Person structure.
 * Remember to call free() to give back memory to the system when the struct 
 * is no longer needed.
 */
Person* createPerson(char* firstName, char* lastName, short age, Gender gender) {
  Person* p = (Person*)malloc(sizeof(Person));
  if (p == NULL) {
    fprintf(stderr, "Not enough memory to create a new Person\n");
    exit(1);
  }

  p->firstName = firstName;
  p->lastName = lastName;
  p->age = age;
  p->gender = gender;
  p->next = NULL;

  return p;
}

void append(Person* tail, Person* p) {
  if (tail == NULL) {
    return;
  }
  tail->next = (struct Person*)p;
}

void freeList(Person* start) {
  Person* startNode = start;
  Person* nextNode = NULL;

  while (startNode != NULL) {
    nextNode = (Person*)startNode->next;
    free(startNode);
    startNode = nextNode;
  }
}

int main(int argc, char* argv[]) {
  Person* a = createPerson("Bob", "Peters", 43, MALE);
  Person* b = createPerson("Sally", "Peters", 43, FEMALE);
  Person* c = createPerson("Ken", "Peters", 8, MALE);
  Person* d = createPerson("Joe", "Peters", 80, MALE);
  Person* e = createPerson("Ann", "Peters", 80, FEMALE);

  append(NULL, a);
  append(a, b);
  append(b, c);
  append(c, d);
  append(d, e);

  printList(a); 

  // Free memory that was allocated for the list
  freeList(a);

  return 0;
}