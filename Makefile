CC=gcc
CFLAGS=-Wall -I/usr/include -L/usr/lib -lpcap -lnsl

packet_parser: packet_parser.c
	${CC} packet_parser.c ${CFLAGS} -o packet_parser

clean:
	rm -f packet_parser packet_parser.o