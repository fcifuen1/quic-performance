# !/usr/bin/env python
# 
# Author: Federico Cifuentes-Urtubey (fc8@illinois.edu)
# 
# Usage: python3 stats.py [csv file] > [results text file]
#
# Assumes the format of the csv file is
# Protocol, Day, Time, Environment, Website, Response time

from statistics import mean, median, stdev
from csv import reader
from sys import argv

# printStats() - prints various statistics from a list of timings
def printStats(l):
	print('MIN     = ', min(l))
	print('MAX     = ', max(l))
	print('AVG     = ', mean(l))
	print('MEDIAN  = ', median(l))
	print('STD DEV = ', stdev(l))

def main():

	print('Stats from {0}'.format(argv[1]) + '\n')

	with open(argv[1], 'r') as f:
		r = reader(f)
		next(r, None)  # Skips header
		
		allTimes = []
		h2_Times = []
		h11_Times = []

		# Processes each row
		for row in r:

			# Timings are in the format #:##:##.######
			timing = float((row[5].split(":"))[2])

			# Sort entries by protocol
			if row[0] == 'HTTP/2':
				h2_Times.append(timing)
			elif row[0] == 'HTTP/1.1':
				h11_Times.append(timing)

			allTimes.append(timing)

		print('Statistics for all timings')
		printStats(allTimes)

		print('Statistics for HTTP/1.1 timings')
		printStats(h11_Times)

		print('Statistics for HTTP/2 timings')
		printStats(h2_Times)

if __name__ == '__main__':
	main()
