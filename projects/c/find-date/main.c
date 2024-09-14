#include <stdio.h>
#include <string.h>

int NUM_ADS = 7;

char *ADS[] = {
  "William: SBM GSOH likes sports, TV, dining",
  "Matt: SWM NS likes art, movies, theater",
  "Luis: SLM ND likes books, theater, art",
  "Mike: DWM DS likes trucks, sports and bieber",
  "Peter: SAM likes chess, working out and art",
  "Josh: SJM likes sports, movies and theater",
  "Jed: DBM likes theater, books and dining"
};

int sports_no_bieber(char* ad) {
  return strstr(ad, "sports") && !strstr(ad, "bieber");
}

int sports_or_workout(char* ad) {
  return strstr(ad, "sports") || strstr(ad, "working out");
}

int ns_theater(char* ad) {
  return strstr(ad, "NS") && strstr(ad, "theater");
}

int arts_theater_or_dining(char* ad) {
  return strstr(ad, "arts") || strstr(ad, "theater") || strstr(ad, "dining");
}

void find(int (*match)(char*)) {
  int i; 
  puts("Search results:");
  puts("-------------------------");

  for (i = 0; i < NUM_ADS; i++) {
    if (match(ADS[i])) {
      printf("%s\n", ADS[i]);
    }
  }

  puts("-------------------------");
}

int main(int argc, char* argv[]) {
  find(arts_theater_or_dining);     // sports_no_bieber -> int (*match)(char*)
  return 0; 
}