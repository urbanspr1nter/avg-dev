#include <stdio.h>

struct exercise {
  const char* description;
  float duration;
};

struct meal {
  const char* ingredients;
  float weight;
};

struct preferences {
  const char* food;
  float exercise_hours;
};

struct fish {
  const char* name;
  const char* species;
  int teeth;
  int age;
  struct preferences care;
};

void catalog(struct fish f) {
  printf(
    "%s is a %s with %i teeth. He is %i\n", 
    f.name, f.species, f.teeth, f.age
  );
}

void label(struct fish f) {
  printf(
    "Name:%s\nSpecies:%s\n%i years old, %i teeth\n",
    f.name, f.species, f.age, f.teeth
  );
}

int main(int argc, char* argv[]) {
  struct fish snappy = {"Snappy", "Piranha", 69, 4, {"Meat", 7.5}};

  printf("Snappy likes to eat %s", snappy.care.food);
  printf("Snappy likes to exercise for %f hours", snappy.care.exercise_hours);


  // & 
  struct fish* snappy_ptr = &snappy;
  printf("snappy start: %p, %ld\n", snappy_ptr, (long int)snappy_ptr);

  char* name = &(snappy.name);
  printf("snappy.name start: %p, %ld\n", name, (long int)name);

  char* species = &(snappy.species);
  printf("snappy.species: %p, %ld\n", species, (long int)species); 

//  const char* snappy_name_ptr = snappy.name;
//  printf("%p, %ld\n", snappy_name_ptr, (long int)snappy_name_ptr);
//
//  const char* snappy_species_ptr = snappy.species;
//  printf("%p, %ld\n", snappy_species_ptr, (long int)snappy_species_ptr);
  
  int* snappy_teeth_ptr = &(snappy.teeth);
  printf("snappy.teeth start: %p, %ld\n", snappy_teeth_ptr, (long int)snappy_teeth_ptr); 
  
  int* snappy_age_ptr = &(snappy.age);
  printf("snappy.age start: %p, %ld\n", snappy_age_ptr, (long int)snappy_age_ptr);

  struct preferences* snappy_care_ptr = &(snappy.care);
  printf("snappy.care start: %p, %ld\n", snappy_care_ptr, (long int)snappy_care_ptr);

  char* food_ptr = &(snappy.care.food);
  printf("snappy.care.food start: %p, %ld\n", food_ptr, (long int)food_ptr);
  // catalog(snappy);

  float* exercise_hours_ptr = &(snappy.care.exercise_hours);
  printf("snappy.care.exercise_hours start: %p, %ld\n", exercise_hours_ptr, (long int)exercise_hours_ptr);
  // label(snappy);

  return 0;
}