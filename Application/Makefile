all: SeLinux.out

INSTDIR = 
INCLUDE = .
CFLAGES =

SeLinux.out: SeLinux.o 
	$(CC) -o SeLinux.out SeLinux.o

SeLinux.o: SeLinux.c	
	$(CC) $(CFLAGES) -c SeLinux.c

clean:
	rm *.out *.o
