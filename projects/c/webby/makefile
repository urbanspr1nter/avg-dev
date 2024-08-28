write_styles.o: write_styles.h write_styles.c
	gcc -c write_styles.h write_styles.c

write_contents.o: write_contents.h write_contents.c
	gcc -c write_contents.h write_contents.c

main.o: main.c
	gcc -c main.c

webby: write_styles.o write_contents.o main.o
	gcc write_styles.o write_contents.o main.o -o webby