#!/bin/python

import sys
import scipy.stats

if len(sys.argv) < 3:
	print 'USAGE ./correlation.py FILE1 FILE2'
	exit(0)

extlangs = ['az','bg','bn','bs','cy','es','fa','hi','id','lv','ms','ne','pl','ro','ru','sk','so','sq','sr','ta','tr','uk','ur','uz']


file1 = sys.argv[1]
file2 = sys.argv[2]

langs1 = [l.split('\t')[0] for l in open(file1).readlines()]
langs2 = [l.split('\t')[0] for l in open(file2).readlines()]

langs = list(set(langs1).intersection(set(langs2)))
for l in langs: print '%s '%l,
print

scores1 = {l.split('\t')[0] : float(l.split('\t')[1]) for l in open(file1).readlines()}
scores2 = {l.split('\t')[0] : float(l.split('\t')[1]) for l in open(file2).readlines()}

s1 = list(); s2 = list()

for l in extlangs:
	s1.append(scores1[l])
	s2.append(scores2[l])

print 'Their average:', sum(s1)/len(s1)
print 'Our average:', sum(s2)/len(s2)

print 'Pearson:', scipy.stats.pearsonr(s1,s2)
print 'Spearman:', scipy.stats.spearmanr(s1,s2)
#print scipy.stats.stats.rankdata(s1)
#print scipy.stats.stats.rankdata(s2)
print 'Kendall Tau:', scipy.stats.kendalltau(scipy.stats.stats.rankdata(s1),scipy.stats.stats.rankdata(s2))

print zip(langs,s1,s2)

