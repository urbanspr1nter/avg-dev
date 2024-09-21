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

int main(int argc, char* argv[]) {
  Person a = {
      .firstName = "Bob",
      .lastName = "Peters",
      .age = 43,
      .gender = MALE,
      .next = NULL
  };

  Person b = {
      .firstName = "Sally",
      .lastName = "Peters",
      .age = 43,
      .gender = FEMALE,
      .next = NULL
  };

  Person c = {
      .firstName = "Ken",
      .lastName = "Peters",
      .age = 8,
      .gender = MALE,
      .next = NULL
  };

  Person d = {
    .firstName = "Joe",
    .lastName = "Peters",
    .age = 80, 
    .gender = MALE,
    .next = NULL
  };

  a.next = (struct Person*)&b;
  b.next = (struct Person*)&c;
  c.next = (struct Person*)&d;

  Person* t = &a;
  while (t != NULL) {
    printPerson(t);
    t = (Person*)(t->next);
  }

  Person e = {
    .firstName = "Ann",
    .lastName = "Peters",
    .age = 80,
    .gender = FEMALE,
    .next = NULL
  };

  puts("------------");
  d.next = (struct Person*)&e;


  t = &a;
  while (t != NULL) {
    printPerson(t);
    t = (Person*)(t->next);
  }

  return 0;
}