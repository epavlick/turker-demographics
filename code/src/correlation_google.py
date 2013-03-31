#!/bin/python

import sys
import scipy.stats

if len(sys.argv) < 3:
	print 'USAGE ./correlation.py FILE1 FILE2'
	exit(0)


file1 = sys.argv[1]
file2 = sys.argv[2]

scores1 = list(); scores2 = list()

for s1, s2 in zip(open(file1).readlines()[1:], open(file2).readlines()[1:]):
	s1 = s1.strip().split(); s2 = s2.strip().split();
	if s1[3] == 'N/A' or s2[3] == 'N/A':
		continue
	scores1.append(float(s1[3]))
	scores2.append(float(s2[3]))


print 'Their average:', sum(scores1)/len(scores1)
print 'Our average:', sum(scores2)/len(scores2)

print 'Pearson:', scipy.stats.pearsonr(scores1,scores2)
print 'Spearman:', scipy.stats.spearmanr(scores1,scores2)
print 'Kendall Tau:', scipy.stats.kendalltau(scipy.stats.stats.rankdata(scores1),scipy.stats.stats.rankdata(scores2))

