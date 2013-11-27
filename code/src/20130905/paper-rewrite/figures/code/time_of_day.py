#!/bin/python

import csv
import datetime
import operator
import numpy as np
import matplotlib.pyplot as plt

OUTPUT_DIR = 'results/data'
RAW_DIR = '/home/steven/Documents/Ellie/Research/demographics/data/dictionary-data-dump-2012-11-13_15:11'

def turker_counts():
	counts = {}
	for line in csv.DictReader(open('results/data/quality.langs.txt'), delimiter='\t'):
		counts[line['lang']] = int(line['num_turkers'])
	return counts

def time_map():
	print "Reading data"
	tdict = dict()
	for line in open('%s/byassign.times'%OUTPUT_DIR).readlines():
		aid, start, end = line.split('\t')
		start_t = datetime.datetime.strptime(start.strip(), "%Y-%m-%d %H:%M:%S")
		end_t = datetime.datetime.strptime(end.strip(), "%Y-%m-%d %H:%M:%S")
		tdict[aid] = (start_t, end_t)
	return tdict

def write_all_times():
        out = open('%s/byassign.times'%OUTPUT_DIR, 'w')
        for line in csv.DictReader(open('%s/assignments'%RAW_DIR)):
                aid = line['id']
                start = line['accept_time']
                end = line['submit_time']
                out.write('%s\t%s\t%s\n'%(aid,start,end,))
        out.close()

def graph(langtimes):
	langnum = 0
	y = []
	x = []
	size = []
	yax = []
	langcounts = []
	tcounts = turker_counts()
	for lang in tcounts :
		langcounts.append((lang,sum([langtimes[lang][h] for h in langtimes[lang]])))
	langs = [t[0] for t in sorted(langcounts, key=operator.itemgetter(1), reverse=True) if tcounts[t[0]] >= 100]
	print [t for t in sorted(langcounts, key=operator.itemgetter(1), reverse=True) if tcounts[t[0]] >= 100]
	for lang in langs: 
		langnum += 1
		yax.append(lang)
		for h in langtimes[lang] : 
			y.append(langnum)
			x.append(h)
			size.append(langtimes[lang][h])
	plt.scatter(x,y, s=size)
	plt.yticks(range(1,langnum+1,1),tuple(yax),rotation=90)
	plt.xticks(range(-1,24), tuple([''] + ['%d'%i for i in range(0,24)] + ['']),rotation=90)
	plt.tick_params(axis='both', which='major', labelsize=14)
	plt.xlabel('Time of day')
	plt.xlim(-1,24)
	plt.ylim(0,langnum+1)
	#plt.show()
	plt.savefig("times.pdf")

write_all_times()
times = time_map()

langtimes = {}

for line in open('%s/quality.assigns.txt'%OUTPUT_DIR).readlines()[1:]:
	lang, aid, _ = line.strip().split('\t',2)
	if lang not in langtimes : langtimes[lang] = {}
	st, end = times[aid]
	h = st.hour 
	if h not in langtimes[lang] : langtimes[lang][h] = 0
	langtimes[lang][h] += 1

graph(langtimes)

