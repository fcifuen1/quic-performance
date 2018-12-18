# !/usr/bin/env python
# 
# Author: Federico Cifuentes-Urtubey (fc8@illinois.edu)
# 
# Usage: python3 metrics.py [environment] [csv file]
# where environment is 'ethernet', 'w_clear', or 'w_crowded'
# and csv file is the file to store collected data
# 
# hyper automatically uses HTTP/2 but falls back to HTTP/1.1 if the request fails

from hyper import HTTPConnection, HTTP20Connection
from hyper.contrib import HTTP20Adapter
from json import loads
from sys import argv
from time import clock
import datetime
import csv
import requests
import socket
import ssl

"""
http://docs.python-requests.org/en/master/
https://www.sjero.net/pubs/2017_IMC_QUIC.pdf
https://hyper.readthedocs.io/en/latest/api.html#http-2

http://pyfound.blogspot.com/2017/01/time-to-upgrade-your-python-tls-v12.html
https://security.stackexchange.com/questions/52150/identify-ssl-version-and-cipher-suite
"""


ENVIRONMENT = argv[1]
INPUT_FILE  = argv[2]

PORT = 443

URL_FACEBOOK = 'https://facebook.com/facebook'
URL_GOOGLE   = 'https://google.com'
URL_YOUTUBE  = 'https://youtube.com'
URL_AKAMAI_DEMO = 'https://http2.akamai.com/demo'


# detectProtoSupport() - Determines if a server supports specific app layer protocols.
#    This relies on the TLS Application-Layer Protocol Negotiation (ALPN) extension
#    since that is where the HTTP version of the request is determined. 
#
# protocols (list): a priority list of protocols the client wants to use
# 
def detectProtoSupport(protocols=['h2', 'http/1.1']):
    context = ssl.create_default_context()
    context.set_alpn_protocols(protocols)
    
    conn = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                               server_hostname=URL_GOOGLE)
    conn.connect((URL_GOOGLE, PORT))
    
    print('detectProtoSupport(): Next protocol: ', conn.selected_alpn_protocol())


# getTiming() - Returns a list of 2 elements for current day and time
# 
def getTiming():
    now = datetime.datetime.now()
    day = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M")
    return [day, time]


# googleSearch() - Performs a Google search using HTTP/1.1
# 
# query (string): the input for a Google search
# 
def googleSearch(query, proto='h1.1'):
    query = query.replace(" ", "+")
    url = URL_GOOGLE + '/search?q=' + query

    # Sends an HTTP/1.1 request
    if proto == 'h1.1':
        Connect_HTTP11(url)

        ##*** Another method returning a Response object ***##
        """
        # s is a context manager for a persistent (TCP) connection
        with requests.Session() as s:
            q = {'q': query }
            resp = requests.get(URL_GOOGLE, params=q)
        return resp
        """

    # Sends an HTTP/2 request
    if proto == 'h2':
        Connect_HTTP2(url)
            

# Connect_HTTP11() - Sends an HTTP/1.1 request to the specified website
#
# website (string): the domain to send an HTTP request to
#
def Connect_HTTP11(website):
    #conn = HTTPConnection(website, port=PORT, secure=True)
    resp = requests.get(website)
    
    timing = getTiming()
    l = ['HTTP/1.1', timing[0], timing[1], ENVIRONMENT, website, resp.elapsed]

    updateCSV(INPUT_FILE, l)

    #print('HTTP11(): HTTP ver: ' + str(resp.raw.version))
    

# Connect_HTTP2() - sends an HTTP/2 request to the specified website
# 
# website (string): the domain to send an HTTP request to
# 
def Connect_HTTP2(website):
    conn = requests.Session()
    conn.mount(website, HTTP20Adapter())
    r = conn.get(website)
    r.close()
    
    timing = getTiming()
    l = ['HTTP/2', timing[0], timing[1], ENVIRONMENT, website, r.elapsed]

    updateCSV(INPUT_FILE, l)

    #data = r.json
    #tls_ver = data['tls_version']
    #print('HTTP2(): TLSv: ' +str(tls_ver))

    #print('HTTP2(): ' + str(r.headers))
    

# updateCSV() - appends to the csv file to collect metric data
#
# file (string): name of csv file
# entry (list): includes time and metric data
#
# Format of csv file: protocol, day, time of day, environment, website, response time
#
def updateCSV(filename, entry):
    with open(filename, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(entry)


def main():

    # Write header into the csv file
    with open(INPUT_FILE, 'w') as f:
        csv.writer(f).writerow(['Protocol', 'Day', 'Time', 'Environment', 'Website', 'Response Time'])
    f.close()

    """
    print 'Starting Test 1... \n'
    Connect_HTTP11(URL_GOOGLE)

    
    print 'Starting Test 2... \n'
    googleSearch("voyager 2", 'h1.1')
    
    print 'Starting Test 3... \n'
    Connect_HTTP2(URL_AKAMAI_DEMO)
    

    print 'Starting Test 4... \n'
    googleSearch("pixel 3", 'h2')


    print 'Starting Test 5... \n'
    Connect_HTTP2(URL_FACEBOOK)
    
    print('Completed tests!\n')
    """

    print('Starting data collection... \n')

    for n in range(250):
    	Connect_HTTP11(URL_GOOGLE)
    	googleSearch("2018 acm conferences", 'h1.1')
    	Connect_HTTP2(URL_AKAMAI_DEMO)
    	googleSearch("pixel 3", 'h2')
    	Connect_HTTP2(URL_FACEBOOK)
    	googleSearch("cs@illinois", 'h2')

    print('Experiments completed! \n')

if __name__ == '__main__':
    main() 
