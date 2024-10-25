#include <stdio.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <string.h>

int main() {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1) {
        perror("socket");
        return 1;
    }

    struct hostent* host = gethostbyname("wikipedia.org");
    if (!host) {
        perror("gethostbyname");
        return 1;
    }

    struct in_addr a;

    printf("Host name: %s\n", host->h_name);
    int i = 0;
    for (struct in_addr* addr = host->h_addr_list; addr != NULL; addr++) {
        printf("%02x.%02x.%02x.%02x\n", addr->sa_data & 0xff, addr->sa_data >> 
8 & 0xff,
                   addr->sa_data >> 16 & 0xff, addr->sa_data >> 24 & 0xff);
        i++;
    }

    close(sock);
    return 0;
}
