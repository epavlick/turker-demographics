#!/bin/python

#lang	assign	worker	overall	overall-ng	num-correct	num-total	num-correct-ng	num-total-ng	status
#gu	267659	1416	0.500	0.500	1.000	2.000	1.000	2.000	approved

import sys
import csv
from settings import settings

byworker = {}
lang_counts = {'1' : [l.strip() for l in open('ref/single-lang').readlines()],
	'0' : [l.strip() for l in open('ref/no-lang').readlines()],
	'many' : [l.strip() for l in open('ref/mult-lang').readlines()]}

turkers = {row['worker'] : row for row in csv.DictReader(open('results/data/googmatch.turkers.txt'), delimiter='\t')}

for line in csv.DictReader(open('results/data/quality.assigns.txt'), delimiter='\t'):
	lang = line['lang']
	worker = line['worker'];
	overall = line['overall']
	overall_syn = line['overall-syn']

	if lang not in byworker: byworker[lang] = {}
	if worker not in byworker[lang] : byworker[lang][worker] = {'correct' : 0 , 'correct-syn' : 0, 'total' : 0, }

	byworker[lang][worker]['correct'] += float(overall)
	byworker[lang][worker]['correct-syn'] += float(overall_syn)
	byworker[lang][worker]['total'] += 1

print 'lang\tworker\tnum_hits\tquality\tquality_syn\tnum_langs\tgoog'
for lang in byworker:
	for worker in byworker[lang]:
		quality = float(byworker[lang][worker]['correct'])/byworker[lang][worker]['total']
		quality_syn = float(byworker[lang][worker]['correct-syn'])/byworker[lang][worker]['total']

		if worker in lang_counts['0'] :  num_langs = '0'
		elif worker in lang_counts['1'] :  num_langs = '1'
		elif worker in lang_counts['many'] :  num_langs = 'many'

		num_hits = byworker[lang][worker]['total']
		goog = float(turkers[worker]['match'])

		params = (lang,worker,num_hits,quality,quality_syn,num_langs,goog)

		print '%s\t%s\t%d\t%.03f\t%.03f\t%s\t%s'%params
