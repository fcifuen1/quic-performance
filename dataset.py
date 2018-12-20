# !/usr/bin/env python3
# 
# Author: Federico Cifuentes-Urtubey (fc8@illinois.edu)
# 
# Usage: python3 dataset.py [source text file] > [results text file]
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
		times = []

		# Processes each row
		for row in r:

			# Timings are in the format #:##:##.######
			timing = float((row[5].split(":"))[2])

			times.append(timing)

		printStats(times)

if __name__ == '__main__':
	main()
