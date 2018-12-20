# quic-performance
A small scale study on performance of the QUIC protocol

### Dependencies
[Requests](http://docs.python-requests.org/en/master/)

[Hyper](https://hyper.readthedocs.io/en/latest/)


### Usage

To gather request metrics, run *metrics.py*: ```$ python3 metrics.py [environment] [csv file]```
where environment is 'ethernet', 'w_clear', or 'w_crowded'


To generate statistics from a csv file:
```$ python3 stats.py [csv file] > [results text file]```


The *dataset.py* program requires filtering from csv files made from *metrics.py*. It was made to give data on individual protocols. Below is how to filter for HTTP/1.1 requests. 
```
$ cat [csv file] | grep "HTTP/1.1" > [txt file]
$ python3 dataset.py [txt file] > [results file]
```


To dump UDP packets with the packet parser, first run `make` using the Makefile in this repo, then

```$ ./packet_parser [pcap file] [environment]```
