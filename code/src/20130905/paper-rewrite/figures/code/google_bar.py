#!/bin/python
import csv
import math
import operator
import numpy as np
import sys
sys.path.append('scripts')
from settings import settings
from scipy import stats
from scipy.stats import ttest_1samp
import matplotlib.pyplot as plt

data = {}
all_data = []

goog_langs = ['el', 'eo', 'zh', 'af', 'vi', 'is', 'it', 'kn', 'cs', 'cy', 'ar', 'eu', 'et', 'gl', 'id', 'es', 'ru', 'az', 'nl', 'pt', 'tr', 'lv', 'lt', 'th', 'gu', 'ro', 'ca', 'pl', 'ta', 'fr', 'bg', 'ms', 'hr', 'de', 'da', 'fa', 'fi', 'hy', 'hu', 'ja', 'he', 'te', 'sr', 'sq', 'ko', 'sv', 'ur', 'sk', 'uk', 'sl', 'sw']

n=0.0;d=0.0;

gmatch = csv.DictReader(open('results/data/googmatch.turkers.txt'), delimiter='\t')
#worker_gmatch = {line['worker']: float(line['match']) for line in gmatch}
worker_gmatch = {}
for line in gmatch : 
	w = line['worker']; l = line['lang']; m = float(line['match'])
	if w not in worker_gmatch : worker_gmatch[w] = {}
	worker_gmatch[w][l] = m

for row in csv.DictReader(open('results/data/googmatch.assigns.txt'), delimiter = '\t'):
	lang = row['lang']
	if lang not in goog_langs : continue
	if worker_gmatch[row['worker']][lang] >= settings['google_overlap_cutoff'] : continue
	if lang not in data : data[lang] = []
	data[lang].append(float(row['match-overall']))
	n += float(row['match-overall']);d+=1
	#if lang == 'cy' : print row['worker'],  worker_gmatch[row['worker']] 
	#data[lang].append(float(row['match']))
	
print n / d

graph_data = [] 
t = 0 
for lang in sorted(data.keys()) : 
	if lang not in goog_langs : continue
	x1 = data[lang]
	n1, (smin1, smax1), m1, v1, ss1, sk1 = stats.describe(x1)
	t += n1
	#if n1 < 50 : continue
	graph_data.append((lang,m1)) 

print "total turkers,", t

graph_data = sorted(graph_data, key=operator.itemgetter(1), reverse=True) 

w = .5
p1 = plt.bar(np.arange(len(graph_data)), [d[1] for d in graph_data], width=w, color='green')
#plt.ylabel('% accuracy against controls')
#plt.ylim(0,1)
plt.xlim(0,len(graph_data))
plt.xticks(np.arange(len(graph_data)) + w / 2.,[d[0] for d in graph_data], size='large', rotation=90)
plt.show()
#plt.savefig('results/lang-quality-comp-distribution.png')
