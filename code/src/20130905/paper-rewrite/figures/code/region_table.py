#Hindi&\textbf{0.35} (299)&0.34 (7)&India (285) UAE (5) UK (5) &Saudi Arabia (2) Russia (1) Oman (1) \\
#Tamil&\textbf{0.37} (278)&0.00 (2)&India (271) US (3) Canada (2) &Tunisia (1) Egypt (1) \\
#Malayalam&0.48 (235) &\textbf{0.58} (2)&India (224) UAE (6) US (3) &Saudi Arabia (1) Maldives (1) \\
#Spanish&\textbf{0.72} (205)&0.61 (23)&US (131) Mexico (18) Spain (14) &India (19) Macedonia (2) New Zealand (1) \\

import csv
import operator
import itertools
import sys
sys.path.append('scripts')
from settings import settings
from scipy import stats
from scipy.stats import ttest_ind

def print_table(lang_counts) : 
	for l, inavg, incnt, outavg, outcnt, locs, tot, sig  in lang_counts[:20]: 
		topin = sorted(locs['in'].iteritems(), key=operator.itemgetter(1), reverse=True)[:3]
		topinstr = ''
		for c,n in topin : 
			try : topinstr += '%s (%d) '%(cmap[c].capitalize(),n)
			except : topinstr += '%s (%d) '%(c,n)
		topout = sorted(locs['out'].iteritems(), key=operator.itemgetter(1), reverse=True)[:3]
		topoutstr = ''
		for c,n in topout : 
			try : topoutstr += '%s (%d) '%(cmap[c].capitalize(),n)
			except : topoutstr += '%s (%d) '%(c,n)
		params = (lmap[l].capitalize(),inavg,incnt,outavg,outcnt,topinstr,topoutstr)
		try : 
			if inavg > outavg : 
				if sig == '5' : print '%s & \\textbf{%.02f} (%d) ** & %.02f (%d) & %s & %s \\\\'%params
				elif sig == '10' : print '%s & \\textbf{%.02f} (%d) * & %.02f (%d) & %s & %s \\\\'%params
				else : print '%s & \\textbf{%.02f} (%d) & %.02f (%d) & %s & %s \\\\'%params
			else: 
				if sig == '5' : print '%s & %.02f (%d) & \\textbf{%.02f} (%d) ** & %s & %s\\\\'%params
				elif sig == '10' : print '%s & %.02f (%d) & \\textbf{%.02f} (%d) * & %s & %s\\\\'%params
				else : print '%s & %.02f (%d) & \\textbf{%.02f} (%d) & %s & %s\\\\'%params
		except : 
			try : print '%s & %s (%d) & %.02f (%d) & %s & %s\\\\'%params
			except : 
				try : print '%s & %.02f (%d) & %s (%d) & %s & %s\\\\'%params
				except : print 'BAHHHHHHHHH!'
	
#gu	BD,ZM,OM,TZ,KE,CA,ZA,US,MU,other,UK,IN,PK,SG
valid_regions = {line.strip().split()[0] : set(line.strip().split()[1].split(',')) for line in open('ref/ethnolouge').readlines()}	
lmap = {l.strip().split()[1] : l.strip().split()[0] for l in open('ref/lang2name.txt').readlines()}
cmap = {l.strip().split()[1] : l.strip().split()[0] for l in open('ref/countrynames').readlines()}

turker_locations = {}
#id	langs	country	survey	hitlang	yrseng	yrssrc
for line in csv.DictReader(open('data/turkers.tsv'), delimiter='\t') :
	cs = [c for c in line['country'].strip().split(':') if not c.strip() in ['', 'N/A']]
	if len(cs) > 0 : turker_locations[line['id']] = set(cs)

region_data = {}
loc_data = {}

def worker_in_region(worker, lang) : 
	if worker not in turker_locations : return -1
	if len(turker_locations[worker]) > 1 : return -1
	for loc in turker_locations[worker] : 
		if loc in valid_regions[lang] : return 0
	return 1

#lang	worker	num_hits	quality	quality_syn	num_langs	goog
for line in csv.DictReader(open('results/data/quality.turkers.txt'), delimiter='\t') :
	if float(line['goog']) >= settings['google_overlap_cutoff'] : continue

	worker = line['worker']
	lang = line['lang'] 
	use_worker = worker_in_region(worker,lang)
	if use_worker == -1 : continue #worker has too many locations reported 

	if lang not in region_data : region_data[lang] = {'in' : [], 'out' : []}
	if lang not in loc_data : loc_data[lang] = {'in' : {}, 'out' : {}}

	if use_worker == 0 : 
		region_data[lang]['in'].append(float(line['quality_syn']))
		for c in turker_locations[worker] : 
			if c not in loc_data[lang]['in'] : loc_data[lang]['in'][c] = 0
			loc_data[lang]['in'][c] += 1
	elif use_worker == 1 : 
		region_data[lang]['out'].append(float(line['quality_syn']))
		for c in turker_locations[worker] : 
			if c not in loc_data[lang]['out'] : loc_data[lang]['out'][c] = 0
			loc_data[lang]['out'][c] += 1

lang_counts = []
for l in region_data : 

	incnt = len(region_data[l]['in'])
	outcnt = len(region_data[l]['out'])

	try : inavg = sum(region_data[l]['in'])/len(region_data[l]['in'])
	except ZeroDivisionError: inavg = 'NA'
	try : outavg = sum(region_data[l]['out'])/len(region_data[l]['out'])
	except ZeroDivisionError: outavg = 'NA'

	is_significant = False
	try : 
		t,p = ttest_ind(region_data[l]['in'], region_data[l]['out'])
		if p < 0.05 : is_significant = '5'
		elif p < 0.10 : is_significant = '10'
		else : is_significant = 'X'
	except ZeroDivisionError: pass

	lang_counts.append((l, inavg, incnt, outavg, outcnt, loc_data[l], incnt+outcnt, is_significant))

print_table(sorted(lang_counts,key=operator.itemgetter(6),reverse=True))
