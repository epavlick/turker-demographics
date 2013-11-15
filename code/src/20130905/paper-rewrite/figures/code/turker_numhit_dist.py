#!/bin/python

import csv
import operator
import numpy as np
import matplotlib.pyplot as plt

data = []

for line in csv.DictReader(open('results/data/quality.turkers.txt'), delimiter='\t') : 
	if line['approved'] == 'True': data.append((line['lang'], line['worker'], int(line['num_hits'])))


langs = [d[0] for d in sorted(data, key = operator.itemgetter(2), reverse=True)]
data = [d[2] for d in sorted(data, key = operator.itemgetter(2), reverse=True)]
lang_counts = {} 

bins=5
all_data = []

for lang in set(langs) :
	ldata = [d for d,l in zip(data, langs) if (l == lang)]
	if len(ldata) < 50 : continue
	lang_counts[lang] = len(ldata)
	#count, edges = np.histogram(ldata, bins)
	count = []
	for i in range(bins-1) : count.append(sum(ldata[10*i:10*(i+1)]))
	count.append(sum(ldata[40:]))
	tot = sum(count)
	pcnthits = [float(c) / tot for c in count]
	all_data.append(tuple([lang]+pcnthits))

all_data = sorted(all_data, key=operator.itemgetter(1))

last = [] 

key = []

#colors = ['w','#E8E8F5', '#CECFF6', '#BBBDF9', '#A4A7FA', '#8A8DFA', '#7176FA', '#5157FA', '#343BFB', '#1A22FA']
colors = ['#E8E8F5', '#BBBDF9', '#8A8DFA', '#5157FA', '#1A22FA']
w = 0.8
for i in range(bins) : 
	pcnt = [e[i+1] for e in all_data]
	if i == 0 : 
		key.append(plt.bar(np.arange(len(all_data)), pcnt, color=colors[len(colors)-(i+1)], width=w))
		last = pcnt
	else : 
		key.append(plt.bar(np.arange(len(all_data)), pcnt, bottom=last, color=colors[len(colors)-(i+1)], width=w))
		last = [last[i] + p for i,p in enumerate(pcnt)]

plt.ylim(0,1)
plt.ylabel('Proportion of HITs contributed', rotation=90)
plt.yticks(rotation=90)
plt.xticks(np.arange(len(all_data))+w/2., ['%s %d'%(e[0],lang_counts[e[0]]) for e in all_data], rotation=90, size='small') 
#plt.legend(tuple(key), ('10 turkers with the most HITs', 'Next 10 turkers', 'Next 10 turkers', 'Next 10 turkers', 'Remaining turkers'), loc='lower right')
plt.show()

