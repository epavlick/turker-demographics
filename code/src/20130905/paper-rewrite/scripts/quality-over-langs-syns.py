#!/bin/python

#lang	assign	worker	overall	overall-ng	num-correct	num-total	num-correct-ng	num-total-ng	status
#gu	267659	1416	0.500	0.500	1.000	2.000	1.000	2.000	approved

#lang	worker	num_hits	quality	quality_ng	quality_syn	quality_syn_ng	num_langs	goog	approved

import sys
import csv
from settings import settings

bylang = {}

lang_counts = {
	'1' : [l.strip() for l in open('ref/single-lang').readlines()],
	'0' : [l.strip() for l in open('ref/no-lang').readlines()],
	'many' : [l.strip() for l in open('ref/mult-lang').readlines()]
}

turkers = {row['worker'] : row for row in csv.DictReader(open('results/data/googmatch.turkers.txt'), delimiter='\t')}

allow = []	
for lang_count in settings['use_workers_with_langcounts'] : 
	allow += lang_counts[lang_count]

if settings['avg_lang_over'] == 'assigns' : 
	data_file = 'results/data/quality.assigns.txt'
	label_overall = 'overall'
	label_overall_syn = 'overall-syn'
	
elif settings['avg_lang_over'] == 'turkers' : 
	data_file = 'results/data/quality.turkers.txt'
	label_overall = 'quality'
	label_overall_syn = 'quality_syn'

for line in csv.DictReader(open(data_file), delimiter='\t'):

	lang = line['lang']; worker = line['worker']
	
	if worker not in allow : continue
	
	overall = line[label_overall]
	overall_syn = line[label_overall_syn]

	if lang not in bylang: bylang[lang] = {'correct' : 0, 'correct-syn' : 0, 'total' : 0, 'turkers' : set() }

	bylang[lang]['correct'] += float(overall)
	bylang[lang]['correct-syn'] += float(overall_syn)

	bylang[lang]['total'] += 1
	bylang[lang]['turkers'].add(worker)

print 'lang\tnum_hits\tnum_turkers\tquality\tquality_syn'
for lang in bylang:
	quality = float(bylang[lang]['correct'])/bylang[lang]['total']
	quality_syn = float(bylang[lang]['correct-syn'])/bylang[lang]['total']
	params = (lang,bylang[lang]['total'],len(bylang[lang]['turkers']),quality,quality_syn)
	print '%s\t%d\t%d\t%.03f\t%.03f'%params


	
