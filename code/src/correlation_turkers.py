#!/bin/python

import sys
import scipy.stats

if len(sys.argv) < 3:
	print 'USAGE ./correlation.py EXT_SCORES OUR_SCORES'
	exit(0)

file1 = sys.argv[1]
file2 = sys.argv[2]

ids1 = [l.split('\t')[0] for l in open(file1).readlines()]
ids2 = [l.split('\t')[0] for l in open(file2).readlines()]

ids = list(set(ids1).intersection(set(ids2)))
#for i in ids: print '%s '%i,
#print

print len(ids)

scores1 = {l.split('\t')[0] : float(l.split('\t')[1]) for l in open(file1).readlines()}
scores2 = {l.split('\t')[0] : float(l.split('\t')[1]) for l in open(file2).readlines()}

s1 = list(); s2 = list()

for i in ids:
	s1.append(scores1[i])
	s2.append(scores2[i])

print 'Their average:', sum(s1)/len(s1)
print 'Our average:', sum(s2)/len(s2)

print 'Pearson:', scipy.stats.pearsonr(s1,s2)
print 'Spearman:', scipy.stats.spearmanr(s1,s2)
#print scipy.stats.stats.rankdata(s1)
#print scipy.stats.stats.rankdata(s2)
print 'Kendall Tau:', scipy.stats.kendalltau(scipy.stats.stats.rankdata(s1),scipy.stats.stats.rankdata(s2))

#print zip(ids,s1,s2)

