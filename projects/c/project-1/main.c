// Builds a web page that has the following content:
// Title: Hello, world!
// Content: Welcome to my new personal web page. :)

#include <stdio.h>

int main(int argc, char* argv[]) {
  puts("<html>");
  puts("<head>");
  puts("<title>My website</title>");
  puts("</head>");
  puts("<body>");
  puts("<h1>Hello, world</h1>");
  puts("<p>Welcome to my new personal web page. :)</p>");
  puts("</body>");
  puts("</html>");

  return 0;
}