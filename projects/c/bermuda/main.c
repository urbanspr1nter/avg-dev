#include <stdio.h>

float MIN_LATITUDE = 26.0;
float MAX_LATITUDE = 34.0;
float MIN_LONGITUDE = -76.0;
float MAX_LONGITUDE = -64.0;

int main(int argc, char* argv[]) {
  // Read the latitude, longitude, etc. for each line
  //  --> read the lines using... fgets, sscanf 
  // if the latitude is between 26 and 34, then:
  //  if the longitude is between -76 and -64 then:
  //    display the latitude, longitude and other data

  float latitude;
  float longitude;
  char data[80];

  char csv_line[160];

  int items_read = 0;
  while (1) {
    fgets(csv_line, 160, stdin);
    items_read = sscanf(csv_line, "%f,%f,%79[^\n]", &latitude, &longitude, data);
    if (items_read < 3) {
      break;
    }

    if (
        (latitude > MIN_LATITUDE && latitude < MAX_LATITUDE) &&
        (longitude > MIN_LONGITUDE && longitude < MAX_LONGITUDE)
      ) {
        printf("%f,%f,%s\n", latitude, longitude, data);
      } 
  }
  return 0;
}

