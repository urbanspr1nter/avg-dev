// Builds a web page that has the following content:
// Title: Hello, world!
// Content: Welcome to my new personal web page. :)

/**
 * gcc main.c -o webby
 * 
 * ./webby -s /path/to/style.css -t "My Portfolio" -h "Roger's Coding Portfolio" -c contents.txt -o /path/to/index.html
 */


#include <stdio.h>
#include <unistd.h>

int main(int argc, char* argv[]) {
  char* page_stylesheet_filename;
  char* page_title;
  char* page_heading;
  char* page_contents_filename;
  char* page_output_filename;

  char ch;
  while ((ch = getopt(argc, argv, "s:t:h:c:o:")) != EOF) {
    switch (ch) {
      case 's':
        page_stylesheet_filename = optarg;
        break;
      case 't':
        page_title = optarg;
        break;
      case 'h':
        page_heading = optarg;
        break;
      case 'c':
        page_contents_filename = optarg;
        break;
      case 'o':
        page_output_filename = optarg;
        break;
      default:
        break;
    }
  }

  // Create an output file
  FILE *output_file = fopen(page_output_filename, "w");

  fprintf(output_file, "<html>");
  fprintf(output_file, "<head>");
  fprintf(output_file, "<title>%s</title>\n", page_title);

  fprintf(output_file, "<style>\n");
  char style_line_buffer[1000];
  FILE *style_file = fopen(page_stylesheet_filename, "r");
  while (fscanf(style_file, "%999[^\n]\n", style_line_buffer) == 1) {
    fprintf(output_file, "%s", style_line_buffer);  
  }
  fclose(style_file);
  fprintf(output_file, "</style>\n");

  fprintf(output_file, "</head>");
  fprintf(output_file,"<body>");
  fprintf(output_file, "<h1>%s</h1>\n", page_heading);
  
  // declare a line buffer of 1000 characters
  char line_buffer[1000];

  // open the file found at page_contents_filename
  FILE *contents_file = fopen(page_contents_filename, "r");

  // simply for now, print out the contents
  while (fscanf(contents_file, "%999[^\n]\n", line_buffer) == 1) {
    fprintf(output_file, "<p>%s</p>\n", line_buffer);
  }

  fclose(contents_file);

  fprintf(output_file, "</body>");
  fprintf(output_file, "</html>");

  fclose(output_file);

  return 0;
}