#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <netdb.h>

void error(char* msg) {
  fprintf(stderr, "%s: %s\n", msg, strerror(errno));
  exit(1);
}

int open_socket(char* host, char* port) {
  struct addrinfo* res;

  if (getaddrinfo(host, port, NULL, &res) == -1) {
    error("Can't resolve the address.");
  }

  int d_sock = socket(
    res->ai_family,
    res->ai_socktype,
    res->ai_protocol
  );

  if (d_sock == -1) {
    error("Can't open socket.");
  }

  int c = connect(d_sock, res->ai_addr, res->ai_addrlen);
  freeaddrinfo(res);
  
  if (c == -1) {
    error("Can't connect to socket.");
  }

  return d_sock;
}