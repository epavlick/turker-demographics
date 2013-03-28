#!/bin/python

import csv
import sys
import scipy.stats

if len(sys.argv) < 3:
	print 'USAGE ./correlation.py EXT_SCORES OUR_SCORES'
	exit(0)

cutoff = 100

lfile1 = 'output/bylang.quality.external'
lfile2 = 'dictionaries/all.turkerqual'

langs1 = [l.split('\t')[0] for l in open(lfile1).readlines()]
langs2 = [l.split('\t')[0] for l in open(lfile2).readlines()]

extlangs = list(set(langs1).intersection(set(langs2)))
for l in extlangs: print '%s '%l,
print

file1 = sys.argv[1]
file2 = sys.argv[2]

ids1 = [l.split('\t')[0] for l in open(file1).readlines()]
ids2 = [l.split('\t')[0] for l in open(file2).readlines()]

all_ids = list(set(ids1).intersection(set(ids2)))

turkers_by_lang = dict()

#get mapping of lang: list of turkers
for nl in ['onelang', 'nolang', 'multlang']:
	for line in csv.DictReader(open('output/byturker.voc.%s'%nl), delimiter='\t'):
		tid = line['id']; l = line['hitlang'];
		for ll in l.strip().split(';'):
			if not ll == '':
				if ll not in turkers_by_lang: turkers_by_lang[ll] = set()
				turkers_by_lang[ll].add(tid)

scores1 = dict()
for l in open(file1).readlines():
	ll = l.strip().split('\t')
#	if len(ll) >= 2:
#		if int(ll[2]) > cutoff:
	scores1[ll[0]] = float(ll[1])
#	else:
#		print ll

scores2 = dict()
for l in open(file2).readlines():
	ll = l.strip().split('\t')
#	if len(ll) > 2:
#		if int(ll[2]) > 10:
	scores2[ll[0]] = float(ll[1])
#	else:
#		print ll



#scores1 = {l.split('\t')[0] : float(l.split('\t')[1]) for l in open(file1).readlines() if int(l.strip().split('\t')[2]) > 10}
#scores2 = {l.split('\t')[0] : float(l.split('\t')[1]) for l in open(file2).readlines() if int(l.strip().split('\t')[2])> 10}

all1 = list()
all2 = list()

pavged = list()
savged = list()
kavged = list()

for lang in turkers_by_lang:
#	if lang in extlangs: print '**Language: %s'%lang
#	else: print 'Language: %s'%lang
	s1 = list(); s2 = list()

	ids = turkers_by_lang[lang]

	for i in ids:
		if i in all_ids:
			try:
				s1.append(scores1[i])
				s2.append(scores2[i])
			except KeyError: 
#				print i
				pass

#	print 'Total Turkers: %d'%len(s1)

	if len(s1) > 0 and len(s2) > 0:
		
		all1 += s1; all2 += s2;

#		print '\tTheir average:', sum(s1)/len(s1)
#		print '\tOur average:', sum(s2)/len(s2)

#		print '\tPearson:', scipy.stats.pearsonr(s1,s2)
#		print '\tSpearman:', scipy.stats.spearmanr(s1,s2)
#		print '\tKendall Tau:', scipy.stats.kendalltau(scipy.stats.stats.rankdata(s1),scipy.stats.stats.rankdata(s2))
		if lang in extlangs: 
			pavged.append(scipy.stats.pearsonr(s1,s2))
			savged.append(scipy.stats.spearmanr(s1,s2))
			kavged.append(scipy.stats.kendalltau(scipy.stats.stats.rankdata(s1),scipy.stats.stats.rankdata(s2)))
#	print
	#print zip(ids,s1,s2)
print 'Their average:', sum(all1)/len(all1)
print 'Our average:', sum(all2)/len(all2)

print 'Pearson:', scipy.stats.pearsonr(all1,all2)
print 'Spearman:', scipy.stats.spearmanr(all1,all2)
print 'Kendall Tau:', scipy.stats.kendalltau(scipy.stats.stats.rankdata(all1),scipy.stats.stats.rankdata(all2))

print 'Pearson:', sum([s[0] for s in pavged]) / len(pavged), len(pavged)
print 'Spearman:', sum([s[0] for s in savged]) / len(savged), len(savged)
print 'Kendall Tau:', sum([s[0] for s in kavged]) / len(kavged), len(kavged)
