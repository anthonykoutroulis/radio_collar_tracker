#!/usr/bin/env python
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plot
from multiprocessing import Pool
import argparse
import sys
from Queue import PriorityQueue
import math

queue = PriorityQueue()
freq_index = 0
target_frequency = 0

def procFile(i):
	# print("Getting data from file %d..."%(i))
	outputfile = open("output%02d.txt"%(int(i)), "r")
	filestream = open("fft_%09d_%03d.txt"%(target_frequency, i), "w")
	for line in outputfile:
		# print("Getting line...")
		time = float(line.strip().split(',')[0])
		# print("Got time %.3f" % (time))
		fft = [float(data) for data in line.strip().split(',')[1:]]

		filestream.write("%.3f,%f\n" % (time, fft[freq_index]))

		# break
	outputfile.close()
	filestream.close()
	return

# Parse arguments
parser = argparse.ArgumentParser(description='Extracts a specific frequency'
	' from the exported FFT data')
parser.add_argument('frequency', help='Frequency to extract')
parser.add_argument('max', help='max amplitude')
args = parser.parse_args()


X_labels = np.genfromtxt("fftheader.txt", delimiter=',', skip_footer=3)
X_label = [float(label) for label in X_labels]

#freq_index = int(math.ceil(40960 / 2 + float(40960) * float(int(args.frequency) + 11000 - 172464000) / 2048000 + 1))
freq_index = int(args.frequency)
print("Using frequency %.3f" % (X_label[freq_index]))
target_frequency = X_label[freq_index]
data = np.genfromtxt("fftheader.txt", skip_header=1)
minFFT = data[1]
maxFFT = data[2]
numFiles = data[0]

print("Got header")

print("Running processes...")
p = Pool(8)

p.map(procFile, range(int(numFiles)))

# All files done


print("Plotting...")
plot.cla()
fig = plot.figure()
fig.set_size_inches(8, 6)
fig.set_dpi(72)
ax = plot.gca()
ax.set_title("Frequency: %f"%(X_label[freq_index]))

fft = []
time = []

for i in range(int(numFiles)):
	datafile = open("fft_%09d_%03d.txt"%(target_frequency, i), "r")
	for line in datafile:
		fft.append(line.strip().split(",")[1])
		time.append(line.strip().split(",")[0])

ax.set_ylim(bottom=minFFT, top=float(args.max))
plt = plot.plot(time, fft)
xx, locs = plot.xticks()
ll = ['%.0f' % a for a in xx]
plot.xticks(xx, ll)
plot.xticks(rotation='vertical')
plot.savefig("frequency_%09d.png"%(int(X_label[freq_index])), bbox_inches='tight')
