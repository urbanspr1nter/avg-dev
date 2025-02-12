#include <stdio.h>

int main(void) {
	int y = 91;

	printf("%ld, %d, %ld\n", &y, *(&y), &(*(&y))); 

	return 0;
}
