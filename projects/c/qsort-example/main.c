#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int compare_scores(const void* score_a, const void* score_b) {
  int a = *(int*)score_a;
  int b = *(int*)score_b;

  return a - b;
}

int compare_scores_desc(const void* score_a, const void* score_b) {
  return compare_scores(score_b, score_a);
}

typedef struct {
  int width;
  int height;
} rectangle;

int compare_areas(const void* a, const void* b) {
  rectangle rect_a = *(rectangle*)a;
  rectangle rect_b = *(rectangle*)b;

  int area_a = rect_a.width * rect_a.height;
  int area_b = rect_b.width * rect_b.height;

  return area_a - area_b;
}

int compare_names(const void* a, const void* b) {
  char** str_a = (char**)a;
  char** str_b = (char**)b;

  return strcmp(*str_a, *str_b);
}

int compare_areas_desc(const void* a, const void* b) {
  return compare_areas(b, a);
}

int compare_names_desc(const void* a, const void* b) {
  return compare_names(b, a);
}

int main(int argc, char* argv[]) {
  int scores[] = {543, 323, 32, 554, 11, 3, 112};
  qsort(scores, 7, sizeof(int), compare_scores_desc);
  puts("These are the scores in order:");
  for (int i = 0; i < 7; i++) {
    printf("Score = %i\n", scores[i]);
  }

  char* names[] = {"Karen", "Mark", "Brett", "Molly"};
  qsort(names, 4, sizeof(char*), compare_names);
  puts("These are the names in order:");
  for (int i = 0; i < 4; i++) {
    printf("%s\n", names[i]);
  }

  rectangle* rects = malloc(sizeof(rects) * 3);
  rects[0].width = 3;
  rects[0].height = 8;

  rects[1].width = 6;
  rects[1].height = 9;

  rects[2].width = 10;
  rects[2].height = 10;

  qsort(rects, 3, sizeof(rectangle), compare_areas_desc);
  for (int i = 0; i < 3; i++) {
    printf("Rect %i: width: %i, height: %i\n", i, rects[i].width, rects[i].height);
  }

  return 0;
}