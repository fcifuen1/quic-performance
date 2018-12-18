/* Usage: ./packet_parser [pcap file] [environment]
 *
 * Author: Federico Cifuentes-Urtubey
 * Modified packet parser for UDP packets
 *
 * See original at http://eecs.berkeley.edu/~ee122/fa07/projects/p2files/
 */

/* Demonstration program of reading packet trace files recorded by pcap
 * (used by tshark and tcpdump) and dumping out some corresponding information
 * in a human-readable form.
 *
 * Note, this program is limited to processing trace files that contains
 * UDP packets.  It prints the timestamp, source port, destination port,
 * and length of each such packet.
 */

#include <pcap.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include <net/if.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/if_ether.h>

static char* ENVIRONMENT;
//static char* FILENAME;

struct UDP_hdr {
	u_short	uh_sport;		/* source port */
	u_short	uh_dport;		/* destination port */
	u_short	uh_ulen;		/* datagram length */
	u_short	uh_sum;			/* datagram checksum */
};

/* Returns a string representation of a timestamp. */
const char *timestamp_string(struct timeval ts);

/* Report a problem with dumping the packet with the given timestamp. */
void problem_pkt(struct timeval ts, const char *reason);

/* Report the specific problem of a packet being too short. */
void too_short(struct timeval ts, const char *truncated_hdr);

/* Extracts packet info into a CSV file */
void updateCSV(char* filename, char* proto, char* day, char* time, 
               char* env, char* site, char* resp_time);

/* dump_UDP_packet()
 *
 * This routine parses a packet, expecting Ethernet, IP, and UDP headers.
 * It extracts the UDP source and destination port numbers along with the UDP
 * packet length by casting structs over a pointer that we move through
 * the packet.  We can do this sort of casting safely because libpcap
 * guarantees that the pointer will be aligned.
 *
 * The "ts" argument is the timestamp associated with the packet.
 *
 * Note that "capture_len" is the length of the packet *as captured by the
 * tracing program*, and thus might be less than the full length of the
 * packet.  However, the packet pointer only holds that much data, so
 * we have to be careful not to read beyond it.
 */
void dump_UDP_packet(const unsigned char *packet, struct timeval ts, 
	                 unsigned int capture_len)
{
	struct ip *ip;
	struct UDP_hdr *udp;
	unsigned int IP_header_length;

	/* For simplicity, we assume Ethernet encapsulation. */

	if (capture_len < sizeof(struct ether_header))
	{
		/* We didn't even capture a full Ethernet header, so we
		 * can't analyze this any further.
		 */
		too_short(ts, "Ethernet header");
		return;
	}

	/* Skip over the Ethernet header. */
	packet += sizeof(struct ether_header);
	capture_len -= sizeof(struct ether_header);

	if (capture_len < sizeof(struct ip))
	{ /* Didn't capture a full IP header */
		too_short(ts, "IP header");
		return;
	}

	ip = (struct ip*) packet;
	IP_header_length = ip->ip_hl * 4;	/* ip_hl is in 4-byte words */

	if (capture_len < IP_header_length)
	{ /* didn't capture the full IP header including options */
		too_short(ts, "IP header with options");
		return;
	}

	/* QUIC runs on top of UDP, so it has a UDP header */
	if (ip->ip_p != IPPROTO_UDP)
	{
		problem_pkt(ts, "non-UDP packet");
		return;
	}

	/* Skip over the IP header to get to the UDP header. */
	packet += IP_header_length;
	capture_len -= IP_header_length;

	if (capture_len < sizeof(struct UDP_hdr))
	{
		too_short(ts, "UDP header");
		return;
	}

	udp = (struct UDP_hdr*) packet;

	printf("%s UDP src_port=%d dst_port=%d length=%d\n",
		timestamp_string(ts),
		ntohs(udp->uh_sport),
		ntohs(udp->uh_dport),
		ntohs(udp->uh_ulen));

/*
	updateCSV(char* filename, char* proto, char* day, \
                char* time, char* env, char* site, char* resp_time)

*/

/*
	char *day, *time;

	time_t t = time(NULL);
	struct tm curtime = *localtime(&t);

	strftime(day, 10, "%Y-%m-%d", curtime);
	strftime(time, 5, "%H:%M", curtime);


	updateCSV(FILENAME, "GQUIC", day, time, ENVIRONMENT,
*/
}


int main(int argc, char *argv[])
{
	pcap_t *pcap;
	const unsigned char *packet;
	char errbuf[PCAP_ERRBUF_SIZE];
	struct pcap_pkthdr header;

	/* Skip over the program name. */
	++argv; --argc;

	/* The program requires 2 arguments */
	if ( argc != 2 )
	{
		printf("argc = %d", argc);
		fprintf(stderr, "Program requires 2 arguments: packet trace and environment \n");
		exit(1);
	}

	//FILENAME = argv[2];
	ENVIRONMENT = argv[2]; //[3]; once FILENAME is added

	pcap = pcap_open_offline(argv[0], errbuf);
	if (pcap == NULL)
	{
		fprintf(stderr, "error reading pcap file: %s\n", errbuf);
		exit(1);
	}

	/* Now just loop through extracting packets as long as we have
	 * some to read.
	 */
	while ((packet = pcap_next(pcap, &header)) != NULL)
		dump_UDP_packet(packet, header.ts, header.caplen);

	return 0;
}


/* Note, this routine returns a pointer into a static buffer, and
 * so each call overwrites the value returned by the previous call.
 */
const char *timestamp_string(struct timeval ts)
{
	static char timestamp_string_buf[256];

	sprintf(timestamp_string_buf, "%d.%06d",
		(int) ts.tv_sec, (int) ts.tv_usec);

	return timestamp_string_buf;
}

void problem_pkt(struct timeval ts, const char *reason)
{
	fprintf(stderr, "%s: %s\n", timestamp_string(ts), reason);
}

void too_short(struct timeval ts, const char *truncated_hdr)
{
	fprintf(stderr, "packet with timestamp %s is truncated and lacks a full %s\n",
		timestamp_string(ts), truncated_hdr);
}

void updateCSV(char* filename, char* proto, char* day, 
		       char* time, char* env, char* site, char* resp_time)
{
	FILE *f;
	f = fopen(filename, "a");
	if (f == NULL)
	{
		printf("Couldn't open file!\n");
		return;
	}

	fprintf(f, "%s,%s,%s,%s,%s,%s", 
		    proto, day, time, env, site, resp_time);

	fclose(f);
}