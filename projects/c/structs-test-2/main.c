#include <stdio.h>

typedef struct exercise {
  const char* description;
  float duration;
} exercise;

typedef struct meal {
  const char* ingredients;
  float weight;
} meal;

typedef struct preferences {
  struct meal food;
  struct exercise exercise;
} preferences;

typedef struct {
  const char* name;
  const char* species;
  int teeth;
  int age;
  struct preferences care;
} fish;

void label(fish f) {
  printf("Name:%s\n", f.name);
  printf("Species:%s\n", f.species);
  printf("%d years old, %d teeth\n", f.age, f.teeth);
  printf(
    "Feed with %.2f lbs of %s and allow to %s for %.2f hours\n",
    f.care.food.weight,
    f.care.food.ingredients,
    f.care.exercise.description,
    f.care.exercise.duration
  );
}

int main(int argc, char* argv[]) {
  fish snappy = {
    .name = "Snappy",
    .species = "Piranha",
    .teeth = 69,
    .age = 4,

    .care = {
      .food = { .ingredients = "meat", .weight = 0.2 },
      .exercise = { .description = "swim in the jacuzzi", .duration = 7.5}
    }
  }; 

  label(snappy);

  return 0;
}