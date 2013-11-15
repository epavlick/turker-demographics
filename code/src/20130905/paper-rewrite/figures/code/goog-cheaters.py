#!/bin/python
# -*- coding: utf-8 -*- 

import csv
import sys
import operator
import numpy as np
import scipy.stats
import operator
import matplotlib.pyplot as plt
import sys; sys.path.append('/home/steven/Documents/Ellie/Research/demographics/repo/code/src/20130905')
#from settings import settings

goog_langs = ['el', 'eo', 'zh', 'af', 'vi', 'is', 'it', 'kn', 'cs', 'cy', 'ar', 'eu', 'et', 'gl', 'id', 'es', 'ru', 'az', 'nl', 'pt', 'tr', 'lv', 'lt', 'th', 'gu', 'ro', 'ca', 'pl', 'ta', 'fr', 'bg', 'ms', 'hr', 'de', 'da', 'fa', 'fi', 'hy', 'hu', 'ja', 'he', 'te', 'sr', 'sq', 'ko', 'sv', 'ur', 'sk', 'uk', 'sl', 'sw']

workers = {}
trans = {}
turkers = {row['worker'] : row for row in csv.DictReader(open('results/data/googmatch.turkers.txt'), delimiter='\t')}

def use(worker, threshold) : return (float(turkers[worker]['match']) <= threshold)

for cutoff in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:

	for line in open('data/pass-1').readlines():
		hitid, lang, word, control, goog, responses = line.split('\t', 5)
			
		if lang not in goog_langs : continue

		word = word.lower()

		for response in responses.split('\t'):

			t = response.strip().split(':')

			if len(t) > 1 : 

				worker = t[0]
				translation = t[1].lower()

				if(use(worker, cutoff)):
					if cutoff not in workers: workers[cutoff] = set(); trans[cutoff] = [];
					workers[cutoff].add(worker)
					trans[cutoff].append(translation)

#data = [(0,2305), (0.1,2475), (0.2,2758), (0.3,3198), (0.4,3690), (0.5,4312), (0.6,4836), (0.7,5129), (0.8,5266), (0.9,5280), (1.0,5281)]
	
data = sorted([(w,len(workers[w])) for w in workers], key=operator.itemgetter(0))
data2 = sorted([(w,len(trans[w])) for w in trans], key=operator.itemgetter(0))

#fig, ax1 = plt.subplots()

mx = float(max([d[1] for d in data]))
mx2 = float(max([d[1] for d in data2]))
mn = float(min([d[1] for d in data]))

for d,d2 in zip(data, data2):
	print d[0], d[1], d[1]/mx, d2[1], d2[1]/mx2

p1 = plt.plot([d[0] for d in data], [d[1]/mx for d in data], label='Turkers')

#ax2 = ax1.twinx()
p2 = plt.plot([d[0] for d in data2], [d[1]/mx2 for d in data2], color='r', label='Translations')

plt.xlabel('% overlap with Google Translate')

plt.legend(loc=4)

plt.show()

