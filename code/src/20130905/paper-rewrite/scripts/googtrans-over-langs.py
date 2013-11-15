#!/bin/python

#lang	assign	worker	match-overall	match-c	match-nc	num-match-overall	num-match-c	num-match-nc	total	status
#gu	267659	1416	0.400	0.000	0.500	4.000	0.000	4.000	10.000	approved
import sys
import csv

bylang = {}

lang_counts = {'1' : [l.strip() for l in open('ref/single-lang').readlines()],
	'0' : [l.strip() for l in open('ref/no-lang').readlines()],
	'many' : [l.strip() for l in open('ref/mult-lang').readlines()]}

for line in csv.DictReader(open('results/data/googmatch.assigns.txt'), delimiter='\t'):
	lang = line['lang']; worker = line['worker'];
	match_overall = line['match-overall']; match_c = line['match-c']; match_nc = line['match-nc']
	if lang not in bylang: bylang[lang] = {'match' : 0, 'match-c' : 0 , 'match-nc' : 0, 'total' : 0}
	bylang[lang]['match'] += float(match_overall)
	bylang[lang]['match-c'] += float(match_c)
	bylang[lang]['match-nc'] += float(match_nc)
	bylang[lang]['total'] += 1

print 'lang\tnum_hits\tmatch\tmatch-c\tmatch-nc'
for lang in bylang:
	quality = float(bylang[lang]['match'])/bylang[lang]['total']
	quality_c = float(bylang[lang]['match-c'])/bylang[lang]['total']
	quality_nc = float(bylang[lang]['match-nc'])/bylang[lang]['total']
	print '%s\t%d\t%.03f\t%.03f\t%.03f'%(lang,bylang[lang]['total'],quality,quality_c,quality_nc)
	
