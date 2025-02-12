#include <stdio.h>

int main(void) {
	int x[5] = {4, 10, 11, 32, 91};
	
	printf("%d\n", x[0]);
	printf("%d\n", x[3]);

	printf("Address which x points to: %p, %ld\n", x, x) ;

	// int* x == int x[]
	// *(x + 1) == x[1]
	printf("value at the address: %d, address: %ld\n", *(x), x);
	printf("value at the address: %d, address: %ld\n", *(x + 1), x + 1);
	printf("value at the address: %d, address: %ld\n", *(x + 2), x + 2);
	printf("value at the address: %d, address: %ld\n", *(x + 3), x + 3);

	
	return 0;
}
