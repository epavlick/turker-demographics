#!/bin/python
import csv
import math
import operator
import numpy as np
from scipy import stats
from scipy.stats import ttest_1samp
import matplotlib.pyplot as plt

data = {}
all_data = []

goog_langs = ['el', 'eo', 'zh', 'af', 'vi', 'is', 'it', 'kn', 'cs', 'cy', 'ar', 'eu', 'et', 'gl', 'id', 'es', 'ru', 'az', 'nl', 'pt', 'tr', 'lv', 'lt', 'th', 'gu', 'ro', 'ca', 'pl', 'ta', 'fr', 'bg', 'ms', 'hr', 'de', 'da', 'fa', 'fi', 'hy', 'hu', 'ja', 'he', 'te', 'sr', 'sq', 'ko', 'sv', 'ur', 'sk', 'uk', 'sl', 'sw']

for row in csv.DictReader(open('results/data/quality.turkers.txt'), delimiter = '\t'):
	lang = row['lang']
	if lang not in data : data[lang] = []
	data[lang].append((float(row['quality']), float(row['quality_syn'])))
	
graph_data = [] 
t = 0 
for lang in sorted(data.keys()) : 
#	if lang not in goog_langs : continue
	x1 = [d[0] for d in data[lang]]
	x2 = [d[1] for d in data[lang]]
	n1, (smin1, smax1), m1, v1, ss1, sk1 = stats.describe(x1)
	n2, (smin2, smax2), m2, v2, ss2, sk2 = stats.describe(x2)
	t += n1
	if n1 < 50 : continue
	graph_data.append((m1,m2,1.96*(math.sqrt(v2) / math.sqrt(n2)),lang))
#	tstat, pval = stats.ttest_1samp(x, am)
#	print '%s\t%.02f\t%.02f\t%.02f\t'%(lang, m, v, pval)

print "total turkers,", t

print '\n'.join([d[3] for d in graph_data])
exit(0)
graph_data = sorted(graph_data, key=operator.itemgetter(1), reverse=True) 

w = .5
p1 = plt.bar(np.arange(len(graph_data)), [d[1] for d in graph_data], width=w, color='#6699FF', yerr=[d[2] for d in graph_data], ecolor='black')
p1 = plt.bar(np.arange(len(graph_data)), [d[0] for d in graph_data], width=w, color='#0000FF')
#plt.ylabel('% accuracy against controls')
plt.ylim(0,1)
plt.xlim(0,len(graph_data))
plt.xticks(np.arange(len(graph_data)) + w / 2.,[d[3] for d in graph_data], size='large', rotation=90)
plt.show()
#plt.savefig('results/lang-quality-comp-distribution.png')
