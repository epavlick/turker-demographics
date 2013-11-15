#!/bin/python

#lang	assign	worker	match-overall	match-c	match-nc	num-match-overall	num-match-c	num-match-nc	total	status
#gu	267659	1416	0.400	0.000	0.500	4.000	0.000	4.000	10.000	approved
import sys
import csv

byworker = {}
lang_counts = {'1' : [l.strip() for l in open('ref/single-lang').readlines()],
	'0' : [l.strip() for l in open('ref/no-lang').readlines()],
	'many' : [l.strip() for l in open('ref/mult-lang').readlines()]}

for line in csv.DictReader(open('results/data/googmatch.assigns.txt'), delimiter='\t'):
	lang = line['lang']; worker = line['worker'];
	match_overall = line['match-overall']; match_c = line['match-c']; match_nc = line['match-nc']
	if lang not in byworker: byworker[lang] = {}
	if worker not in byworker[lang] : byworker[lang][worker] = {'match' : 0, 'match-c' : 0 , 'match-nc' : 0, 'total' : 0}
	byworker[lang][worker]['match'] += float(match_overall)
	byworker[lang][worker]['match-c'] += float(match_c)
	byworker[lang][worker]['match-nc'] += float(match_nc)
	byworker[lang][worker]['total'] += 1

print 'lang\tworker\tnum_hits\tmatch\tmatch-c\tmatch-nc\tnum_langs'
for lang in byworker:
	for worker in byworker[lang]:
		quality = float(byworker[lang][worker]['match'])/byworker[lang][worker]['total']
		quality_c = float(byworker[lang][worker]['match-c'])/byworker[lang][worker]['total']
		quality_nc = float(byworker[lang][worker]['match-nc'])/byworker[lang][worker]['total']
		if worker in lang_counts['0'] :  num_langs = '0'
		elif worker in lang_counts['1'] :  num_langs = '1'
		elif worker in lang_counts['many'] :  num_langs = 'many'
		print '%s\t%s\t%d\t%.03f\t%.03f\t%.03f\t%s'%(lang,worker,byworker[lang][worker]['total'],quality,quality_c,quality_nc,num_langs)
	
