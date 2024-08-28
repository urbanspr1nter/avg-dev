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
#include "write_styles.h"
#include "write_contents.h"

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

  write_styles(output_file, page_stylesheet_filename);

  fprintf(output_file, "</head>");
  fprintf(output_file,"<body>");
  fprintf(output_file, "<h1>%s</h1>\n", page_heading);
  
  write_contents(output_file, page_contents_filename);

  fprintf(output_file, "</body>");
  fprintf(output_file, "</html>");

  fclose(output_file);

  return 0;
}