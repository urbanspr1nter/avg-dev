#include "write_styles.h"

void write_styles(FILE* output_file, char* page_stylesheet_filename) {
  fprintf(output_file, "<style>\n");
  char style_line_buffer[1000];
  FILE *style_file = fopen(page_stylesheet_filename, "r");
  while (fscanf(style_file, "%999[^\n]\n", style_line_buffer) == 1) {
    fprintf(output_file, "%s", style_line_buffer);  
  }
  fclose(style_file);
  fprintf(output_file, "</style>\n");
}