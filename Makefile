CFLAGS=-g -Wall

a1main: a1sampler.o tsc.c
	$(CC) $(CFLAGS) -o a1sampler a1sampler.c tsc.c

	
	
clean:
	rm -f a1sampler a1sampler.o
	rm -f *.pyc
	rm -f random.eps
