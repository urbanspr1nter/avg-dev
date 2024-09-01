#include <stdio.h>

typedef struct {
  const char* name;
  const char* species;
  int age;
} turtle;

void happy_birthday(turtle* t) {
  t->age = t->age + 1;
  printf(
    "Happy Birthday %s! You are now %i years old!\n",
    t->name,
    t->age
  );
}

int main(int argc, char* argv[]) {
  turtle myrtle = {
    .name = "Myrtle", 
    .species = "Leatherback sea turtle", 
    .age = 99
  };
  happy_birthday(&myrtle); // &myrtle -> turtle* 
  printf("%s's age is now %i\n", myrtle.name, myrtle.age);

  return 0;
}