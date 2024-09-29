#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

int main(int argc, char* argv[]) {
  if (execl("/sbin/ifconfig", "/sbin/ifconfig", NULL) == -1) {
    // This code will never run if /sbin/ifconfig is successful
    if (execl("/usr/sbin/ip", "/usr/sbin/ip", "a", NULL) == -1) {
      // This code will never run if /usr/sbin/ip a is successful
      fprintf(stderr, "Cannot run ip: %s\n", strerror(errno));
      return 1;
    }
  }

  return 0;
}