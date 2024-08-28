#include "write_contents.h"

void write_contents(FILE* output_file, char* page_contents_filename) {
  // declare a line buffer of 1000 characters
  char line_buffer[1000];

  // open the file found at page_contents_filename
  FILE *contents_file = fopen(page_contents_filename, "r");

  // simply for now, print out the contents
  while (fscanf(contents_file, "%999[^\n]\n", line_buffer) == 1) {
    fprintf(output_file, "<p>%s</p>\n", line_buffer);
  }

  fclose(contents_file);
}