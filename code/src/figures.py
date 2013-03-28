import re
import os
import os.path
import csv
import sys
import math
import numpy
import scipy
import string
import operator
import itertools
import dictionaries
from scipy import stats
from scipy.stats import norm
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

QC = '' #'.related'
OUTPUT_DIR = 'output'
RAW_DIR = '/home/steven/Documents/Ellie/Research/demographics/data/dictionary-data-dump-2012-11-13_15:11' 

#filter data and return only entries which have the specified value in the specified column
#e.g. only entries for which 'country' is 'IN'
def select_by(data, col, value):
        dicts = dict()
        for d in data:
                if(data[d][col] == value):
                        dicts[d] = data[d]
        return dicts

#get a list of all possible values of the specified attribute 
#e.g. if attr = 'country', get a list of all the values that appear in the column 'country'
def all_keys(path, attr):
        ret = set()
        data = csv.DictReader(open(path),delimiter='\t')
        for d in data:
                ll = d[attr].split(';')
                for l in ll:
                        ret.add(l)
        if('' in ret):
                ret.remove('')
        return list(ret)

#read in tsv data file at path and return as dictionary of dictionaries, keyed by 'id'
def read_data(path):
        ret = dict()
        data = csv.DictReader(open(path),delimiter='\t')
        for d in data:
                ret[d['id']] = d
        return ret

#read in tsv data file at path and return as dictionary of dictionaries, keyed by 'id'
#essentially the same as what is above, but slightly nicer format. mostly just here because
#I was combining code from multiple files and didn't want to rework little details
def read_table_file(path):
        ret = dict()
        data = csv.DictReader(open(path),delimiter='\t')
        for d in data:
                ret[d['id']] = {'lang':d['lang'],'country':d['country'], 'hitlang': d['hitlang'], 'survey':d['survey'], 'yrseng':d['yrseng'], 'yrssrc':d['yrssrc']}
        return ret

#return a dictionary counting the number of occurances of each value of attr
#e.g. if attr is 'country', a dictionary of {country : count}
def count_dicts(data, attr):
        langs = dict()
        for turker in data:
                ll = data[turker][attr].split(';')
                for l in ll:
                        if(re.match('\d+',l) or l == 'N/A'):
                                continue
                        if(l == '' or l == '-'):
                                continue
                        if l not in langs:
                                langs[l] = 0
                        langs[l] += 1
        return [(l,langs[l]) for l in langs]

#clean up data and return in format {id: {lang country survey}}
#I seem to have a lot of methods to do this kind of thing...
def get_dicts(data):
        dicts = dict()
        for d in data:
                langs = data[d]['langs'].strip(';')
                ctry = data[d]['country'].strip(';')
                srvy = data[d]['survey'].strip(';').encode('ascii', 'ignore')
                dicts[d] = {'lang': langs, 'country': ctry, 'survey':srvy}
        return dicts

#maps language prefix to language name
def reverse_lang_map(path):
        lang_data = {}
        for line in csv.DictReader(open(path)):
                lang = line['name']
                prefix = line['prefix']
                if(prefix not in lang_data):
                        lang_data[prefix] = re.sub('_',' ',lang)
        return lang_data

#takes path of quality output file (in form id	quality_score) and returns dict of {id : score}
#if turkers=True, id is a turker id, otherwise its an assignment id
def all_avg_scores(path, turkers=True):
	scores = dict()
        for line in open(path).readlines():
		l = line.split('\t')
		if(turkers):
			try:
				scores[l[0]] = float(l[1].strip())
			except:
				continue
		else:
			try:
				scores[l[0]] = float(l[3].strip())
			except:
				continue
	return scores

#given scores (a dictionary of all scores) and assign_list (a subset of ids), return the average score and 
#95% CI for the average over the ids in assign_list
def avg_score(assign_list, scores):
	dist = list()
	for a in assign_list:
		if a in scores:
			dist.append(scores[a])
	if(len(dist) == 0):
		return None
	n, (smin, smax), sm, sv, ss, sk = stats.describe(dist)
	moe = math.sqrt(sv)/math.sqrt(n) * 2.576
	return (sm, (sm - moe, sm + moe), n, moe)

#return a dict of {attr: quality estimate}
#e.g. if attr is 'country', returns something like {IN: quality estimate of IN, RU: quality estimate of RU...}
#quality estimates are average qualities over assignments
def conf_int_by_attr(attr):
	ret = dict()
	data = read_table_file('%s/byassign.voc.accepted'%OUTPUT_DIR)
	scores = all_avg_scores('%s/byassign.voc.quality%s'%(OUTPUT_DIR,QC,))
	langs = all_keys('%s/byassign.voc.accepted'%OUTPUT_DIR, attr)
	avg = list()
	for l in langs:
		alist = select_by(data, attr, l).keys()
		avg += alist
		ci = avg_score(alist, scores)
		ret[l] = ci
	ci = avg_score(avg, scores)
	ret['avg'] = ci
	return ret

#return a dict of {attr: quality estimate}
#e.g. if attr is 'country', returns something like {IN: quality estimate of IN, RU: quality estimate of RU...}
#quality estimates are average qualities over turkers 
def conf_int_by_attr_turker(attr):
        tmap = dictionaries.turker_map()
	ret = dict()
	data = read_table_file('%s/byassign.voc.accepted'%OUTPUT_DIR)
	scores = all_avg_scores('%s/byturker.voc.quality%s'%(OUTPUT_DIR,QC,))
	langs = all_keys('%s/byassign.voc.accepted'%OUTPUT_DIR, attr)
	tot = 0	
	avg = list()
	for l in langs:
		alist = select_by(data, attr, l).keys()
		num_assign = len(alist)
		tot += num_assign
		tlist = list(set([tmap[a] for a in alist]))
		avg += tlist
		ci = avg_score(tlist, scores)
		ret[l] = (ci[0], ci[1], num_assign, ci[3])
	ci = avg_score(avg, scores)
	ret['avg'] = ci
	print "tot", tot
	print "n/a", ret['N/A'][2]
	return ret

#compile quality estimates by hit language, and graph the results
#quality estimates are averages over assignments, cut is minimum number of assignments needed for a hitlang
#to be included in the graph
def hitlang_qual(cut=3000):
	assigns_by_lang = dict()
	qual_by_assign = dict()
	qual_by_lang = dict()
	avg_qual = list()
	for line in csv.DictReader(open('%s/byassign.voc.accepted'%OUTPUT_DIR), delimiter='\t'):
		lang = line['hitlang']
		if lang not in assigns_by_lang:
			assigns_by_lang[lang] = list()
		assigns_by_lang[lang].append(line['id'])
	for line in csv.DictReader(open('%s/byassign.voc.quality%s'%(OUTPUT_DIR,QC,)), delimiter='\t'):
		aid = line['id']
		q = line['avg']
		qual_by_assign[aid] = q
	for l in assigns_by_lang.keys():
		print l
		qual = list()
		for a in assigns_by_lang[l]:
			q = qual_by_assign[a]
			if not(q == 'N/A'):
				qual.append(float(q))
				avg_qual.append(float(q))
        	n, (smin, smax), sm, sv, ss, sk = stats.describe(qual)
        	moe = math.sqrt(sv)/math.sqrt(n) * 2.576
		qual_by_lang[l] = (sm, (sm - moe, sm + moe), n, moe)
        n, (smin, smax), sm, sv, ss, sk = stats.describe(avg_qual)
        moe = math.sqrt(sv)/math.sqrt(n) * 2.576
	qual_by_lang['avg'] = (sm, (sm - moe, sm + moe), n, moe)
	conf_int_graphs(sorted([(k,qual_by_lang[k]) for k in qual_by_lang], key=operator.itemgetter(1), reverse=True), cutoff=cut)

#compile quality estimates by hit language, and graph the results
#quality estimates are averages over turkers, cut is minimum number of turkers needed for a hitlang
#to be included in the graph
def hitlang_qual_turker(cut=50):
        tmap = dictionaries.turker_map()
	assigns_by_lang = dict()
	qual_by_assign = dict()
	qual_by_lang = dict()
	avg_qual = list()
	for line in csv.DictReader(open('%s/byassign.voc.accepted'%OUTPUT_DIR), delimiter='\t'):
		lang = line['hitlang']
		if lang not in assigns_by_lang:
			assigns_by_lang[lang] = set()
		assigns_by_lang[lang].add(tmap[line['id']])
	for line in csv.DictReader(open('%s/byturker.voc.quality%s'%(OUTPUT_DIR,QC,)), delimiter='\t'):
		aid = line['id']
		q = line['avg']
		qual_by_assign[aid] = q
	for l in assigns_by_lang.keys():
		qual = list()
		for a in assigns_by_lang[l]:
			if a not in qual_by_assign:
				continue
			q = qual_by_assign[a]
			if not(q == 'N/A'):
				qual.append(float(q))
				avg_qual.append(float(q))
        	n, (smin, smax), sm, sv, ss, sk = stats.describe(qual)
        	moe = math.sqrt(sv)/math.sqrt(n) * 2.576
		qual_by_lang[l] = (sm, (sm - moe, sm + moe), n, moe)
        n, (smin, smax), sm, sv, ss, sk = stats.describe(avg_qual)
        moe = math.sqrt(sv)/math.sqrt(n) * 2.576
	qual_by_lang['avg'] = (sm, (sm - moe, sm + moe), n, moe)
	conf_int_graphs(sorted([(k,qual_by_lang[k]) for k in qual_by_lang], key=operator.itemgetter(1), reverse=True), cutoff=cut)

#compile exact match ratios and quality estimates by hit language, and graph the results
#quality estimates are averages over turkers, cut is minimum number of turkers needed for a hitlang
#to be included in the graph
def exact_match_qual(cut=50):
        tmap = dictionaries.turker_map()
	assigns_by_lang = dict()
	qual_by_assign = dict()
	match_by_assign = dict()
	qual_by_lang = dict()
	match_by_lang = dict()
	avg_qual = list()
	avg_match = list()
	for line in csv.DictReader(open('%s/byassign.voc.accepted'%OUTPUT_DIR), delimiter='\t'):
		lang = line['hitlang']
		if lang not in assigns_by_lang:
			assigns_by_lang[lang] = set()
		assigns_by_lang[lang].add(tmap[line['id']])
	for line in csv.DictReader(open('%s/byturker.voc.quality%s'%(OUTPUT_DIR,QC,)), delimiter='\t'):
		aid = line['id']
		q = line['avg']
		qual_by_assign[aid] = q
	for line in csv.DictReader(open('%s/byturker.voc.quality.exactmatch'%OUTPUT_DIR), delimiter='\t'):
		aid = line['id']
		q = line['avg']
		match_by_assign[aid] = q
	for l in assigns_by_lang.keys():
		qual = list()
		match = list()
		for a in assigns_by_lang[l]:
			if a not in qual_by_assign or a not in match_by_assign:
				continue
			q = qual_by_assign[a]
			m = match_by_assign[a]
			if not(q == 'N/A') and not(m=='N/A'):
				qual.append(float(q))
				match.append(float(m))
				avg_qual.append(float(q))
				avg_match.append(float(m))
        	n, (smin, smax), sm, sv, ss, sk = stats.describe(qual)
        	moe = math.sqrt(sv)/math.sqrt(n) * 2.576
		qual_by_lang[l] = (sm, (sm - moe, sm + moe), n, moe)
        	n, (smin, smax), sm, sv, ss, sk = stats.describe(match)
        	moe = math.sqrt(sv)/math.sqrt(n) * 2.576
		match_by_lang[l] = (sm, (sm - moe, sm + moe), n, moe)
        n, (smin, smax), sm, sv, ss, sk = stats.describe(avg_qual)
        moe = math.sqrt(sv)/math.sqrt(n) * 2.576
	qual_by_lang['avg'] = (sm, (sm - moe, sm + moe), n, moe)
        n, (smin, smax), sm, sv, ss, sk = stats.describe(avg_match)
        moe = math.sqrt(sv)/math.sqrt(n) * 2.576
	match_by_lang['avg'] = (sm, (sm - moe, sm + moe), n, moe)
	exact_match_graphs(sorted([(k,qual_by_lang[k],match_by_lang[k]) for k in qual_by_lang], key=operator.itemgetter(1), reverse=True), cutoff=cut)

#compile exact match ratios, google translate ratios,  and quality estimates by hit language, and graph the results
#quality estimates are averages over turkers, cut is minimum number of turkers needed for a hitlang
#to be included in the graph
def goog_match_qual(cut=50):
        tmap = dictionaries.turker_map()
	assigns_by_lang = dict()
	qual_by_assign = dict()
	match_by_assign = dict()
	goog_by_assign = dict()
	qual_by_lang = dict()
	match_by_lang = dict()
	goog_by_lang = dict()
	avg_qual = list()
	avg_match = list()
	avg_goog = list()
	for line in csv.DictReader(open('%s/byassign.voc.accepted'%OUTPUT_DIR), delimiter='\t'):
		lang = line['hitlang']
		if lang not in assigns_by_lang:
			assigns_by_lang[lang] = set()
		assigns_by_lang[lang].add(tmap[line['id']])
	for line in csv.DictReader(open('%s/byturker.voc.quality%s'%(OUTPUT_DIR,QC,)), delimiter='\t'):
		aid = line['id']
		q = line['avg']
		qual_by_assign[aid] = q
	for line in csv.DictReader(open('%s/byturker.voc.quality.exactmatch'%OUTPUT_DIR), delimiter='\t'):
		aid = line['id']
		q = line['avg']
		match_by_assign[aid] = q
	for line in csv.DictReader(open('%s/byturker.googmatch'%OUTPUT_DIR), delimiter='\t'):
		aid = line['id']
		q = line['avg']
		goog_by_assign[aid] = q
	for l in assigns_by_lang.keys():
		qual = list()
		match = list()
		goog = list()
		for a in assigns_by_lang[l]:
			if a not in qual_by_assign or a not in match_by_assign:
				continue
			q = qual_by_assign[a]
			m = match_by_assign[a]
			if a in goog_by_assign:
				g = goog_by_assign[a]
			else:
				g = None
			if not(q == 'N/A') and not(m=='N/A'):
				qual.append(float(q))
				match.append(float(m))
				avg_qual.append(float(q))
				avg_match.append(float(m))
				if g:
					goog.append(float(g))
					avg_goog.append(float(g))
				else:
					goog.append(None)
        	n, (smin, smax), sm, sv, ss, sk = stats.describe(qual)
        	moe = math.sqrt(sv)/math.sqrt(n) * 2.576
		qual_by_lang[l] = (sm, (sm - moe, sm + moe), n, moe)
        	n, (smin, smax), sm, sv, ss, sk = stats.describe(match)
        	moe = math.sqrt(sv)/math.sqrt(n) * 2.576
		match_by_lang[l] = (sm, (sm - moe, sm + moe), n, moe)
		if None in goog:
			goog_by_lang[l] = None
		else:
	        	n, (smin, smax), sm, sv, ss, sk = stats.describe(goog)
        		moe = math.sqrt(sv)/math.sqrt(n) * 2.576
			goog_by_lang[l] = (sm, (sm - moe, sm + moe), n, moe)
        n, (smin, smax), sm, sv, ss, sk = stats.describe(avg_qual)
        moe = math.sqrt(sv)/math.sqrt(n) * 2.576
	qual_by_lang['avg'] = (sm, (sm - moe, sm + moe), n, moe)
        n, (smin, smax), sm, sv, ss, sk = stats.describe(avg_match)
        moe = math.sqrt(sv)/math.sqrt(n) * 2.576
	match_by_lang['avg'] = (sm, (sm - moe, sm + moe), n, moe)
        n, (smin, smax), sm, sv, ss, sk = stats.describe(avg_goog)
        moe = math.sqrt(sv)/math.sqrt(n) * 2.576
	goog_by_lang['avg'] = (sm, (sm - moe, sm + moe), n, moe)
	goog_graphs(sorted([(k,qual_by_lang[k],match_by_lang[k], goog_by_lang[k]) for k in qual_by_lang], key=operator.itemgetter(1), reverse=True), cutoff=cut)

#returns a dict of {attr1: {attr2: list of assignments}}
#e.g. if attr1 = 'country' and attr2 = 'language', returns a dict of scores keyed by assignment_id and a dictionary of form 
#{IN : {hi: [{assign_id : {}], ta:X[], en: [], ...}, 'RU':{hi: [], ta: [], en: [], ...}}
def two_way_split(attr1, attr2):
	ret = dict()
	data = read_table_file('%s/byassign.voc.accepted'%OUTPUT_DIR)
	scores = all_avg_scores('%s/byassign.voc.quality%s'%(OUTPUT_DIR,QC,), turkers=False)
	first = all_keys('%s/byassign.voc.accepted'%OUTPUT_DIR, attr1)
	second = all_keys('%s/byassign.voc.accepted'%OUTPUT_DIR, attr2)
	for k in first:
		miniret = dict()
		alist = select_by(data, attr1, k)
		for kk in second:
			blist = select_by(alist, attr2, kk)
			miniret[kk] = blist 
		ret[k] = miniret
	return ret, scores

#take the output of two_way_quality and put in form {attr : messy_tuple_of_quality_metrics} and transform into list of tuples
#of (attr, quality) sorted by n (number of assignments or number of turkers)
def clean_ints(data, cutoff=50, sorting=None):
	ret = list()
	for c in data:
		if(not(data[c] == None)):
			if(data[c][2] > cutoff):
					ret.append((c, data[c], data[c][2]))
	ret = sorted(ret, reverse=True) 
	return [(c[0], c[1]) for c in ret]

#stacked bar graph of proportion of exact matches and proportion of synonymn matches
def exact_match_graphs(all_ci_dict, title='Graph', graph_avg=True, cutoff=3000):	
	ci_dict = [c for c in all_ci_dict if c[1][2] >= cutoff]
	yax = [c[1][0] for c in ci_dict]
	yax2 = [c[2][0] for c in ci_dict]
	err = [c[1][3] for c in ci_dict]
	err2 = [c[2][3] for c in ci_dict]
        xax = range(len(ci_dict))
        names = [c[0] for c in ci_dict]
        plt.bar(xax, yax, 1, ecolor='black',color='g')
        plt.bar(xax, yax2, 1, ecolor='black',color='b')
	if(graph_avg):
		bidx = names.index('avg')
		plt.bar(xax[bidx], yax[bidx], 1, color='y') 
		plt.bar(xax[bidx], yax2[bidx], 1, color='r') 
        plt.xticks([x + 0.5 for x in xax], [n for n in names], rotation='vertical')
        plt.ylabel('')
	plt.ylim([0,max(yax)+.1])
	plt.xlim([0,len(ci_dict)])
	plt.savefig('figures/exact-match-bar.pdf')

#stacked bar graph of proportion of exact matches and proportion of synonymn matches
#side by side with proportion of google translate matches
def goog_graphs(all_ci_dict, title='Graph', graph_avg=True, cutoff=3000):	
	width = .8
	ci_dict = [c for c in all_ci_dict if (c[1][2] >= cutoff and not(c[3] == None))]
	yax = [c[1][0] for c in ci_dict]
	yax2 = [c[2][0] for c in ci_dict]
	yax3 = [c[3][0] for c in ci_dict]
	err = [c[1][3] for c in ci_dict]
	err2 = [c[2][3] for c in ci_dict]
	err3 = [c[3][3] for c in ci_dict]
#	yax3 = list()
#	err3 = list()
#	for c in ci_dict:
#		if c[3] == None:
#			print c
#			yax3.append(0)
#			err3.append(0)
#		else:
#			yax3.append(c[3][0])
#			err3.append(c[3][3])
        xax = range(len(ci_dict))
        names = [c[0] for c in ci_dict]
        plt.bar(xax, yax, width/2, ecolor='black',color='#60AFFE')
        plt.bar(xax, yax2, width/2, ecolor='black',color='b')
        plt.bar([x+width/2 for x in xax], yax3, width/2, ecolor='black',color='g')
#	if(graph_avg):
#		bidx = names.index('avg')
#		plt.bar(xax[bidx], yax[bidx], 1, color='y') 
#		plt.bar(xax[bidx], yax2[bidx], 1, color='r') 
#		plt.bar(xax[bidx], yax3[bidx], 1, color='m') 
        plt.xticks([x + 0.5 for x in xax], [n for n in names], rotation='vertical')
        plt.ylabel('')
	plt.ylim([0,max(yax)+.1])
	plt.xlim([0,len(ci_dict)])
	plt.savefig('figures/google-match-bar.pdf')

#bar graph with error bars
def conf_int_graphs(all_ci_dict, title='Graph', graph_avg=True, cutoff=3000):	
	ci_dict = [c for c in all_ci_dict if c[1][2] >= cutoff]
	yax = [c[1][0] for c in ci_dict]
	err = [c[1][3] for c in ci_dict]
        xax = range(len(ci_dict))
        names = [c[0] for c in ci_dict]
        plt.bar(xax, yax, 1, yerr=err, ecolor='black')
	if(graph_avg):
		bidx = names.index('avg')
		plt.bar(xax[bidx], yax[bidx], 1, color='r') 
        plt.xticks([x + 0.5 for x in xax], [n for n in names], rotation='vertical')
        plt.ylabel('')
	plt.ylim([0,max(yax)+.1])
	plt.xlim([0,len(ci_dict)])
	plt.savefig('figures/hitlang-bar.pdf')

#mapping of assign_id to hit_id
def hit_map():
        lang_data = {}
        for line in csv.DictReader(open(ASSIGN_RAW)):
                assign = line['id']
                hit = line['hit_id']
                if(assign not in lang_data):
                        lang_data[assign] = hit
        return lang_data

#returns a dict of {attr1: {attr2 : quality estimate}}
#e.g. if attrs are country and language , returns dict of form
#{IN : {hi: XX, ta:XX, en: XX, ...}, 'RU':{hi: XX, ta: XX, en: XX, ...}}
def two_way_quality(attr1, attr2):
	breakdown = dict()
	tw, scores = two_way_split(attr1, attr2)
	for t in tw:
		breakdown[t] = dict()
		for tt in tw[t]:
			if(not(tt == 'None')):
				s = avg_score(tw[t][tt].keys(), scores)
				if(not(s==None)):
					breakdown[t][tt] = s
	return breakdown

#sort the native/non native data by total number of turkers
def sort_data(data):
	tups = list()
	for lang in data:
		if('yes' in data[lang] and 'no' in data[lang]):
			ysz = data[lang]['yes'][2]
			nsz = data[lang]['no'][2]
			tups.append((ysz+nsz, lang, data[lang]))
	return [(t[1],t[2]) for t in sorted(tups, reverse=True)]

#return dictionary of {language : {yes : quality estimate of native speakers, no : quality estimate of nonnative speakers}}
#quality estimates by assignments
def compare_native_speakers():
	langs = all_keys('%s/byassign.voc.accepted'%OUTPUT_DIR, 'hitlang')
	quals = two_way_quality('hitlang','lang')
	graph_data = dict()	
	graph_data_clean = dict()	
	for l in langs:
		graph_data[l] = clean_ints(quals[l])
	for k in graph_data:
		print k, graph_data[k]
		new = dict()
		for i in graph_data[k]:
			if i[0] == k:
				new['yes'] = i[1]
			elif i[0] == 'en':
				new['no'] = i[1]
		graph_data_clean[k] = new
	return sort_data(graph_data_clean)

def native_compare_bar_graph(quals, cutoff=50):
	ret = list()
	all_yes = list()
	all_no = list()
        for hl in quals:
		yes = list()
        	no = list()
                for nl in quals[hl]:
                        if nl == hl:
                                for tid, yrs, q in quals[hl][nl]:
                                       	yes.append(q)
                        else:
                                for tid, yrs, q in quals[hl][nl]:
                                        no.append(q)
		ldict = dict()
		if(len(yes) > cutoff and len(no) > cutoff):
			all_yes += yes
			all_no += no
#			print 'bargraph\t%s\t%d\t%d'%(hl,len(yes),len(no),), sum(yes) / len(yes), sum(no) / len(no)
			n, (smin, smax), sm, sv, ss, sk = stats.describe(yes)
        	       	moe = math.sqrt(sv)/math.sqrt(n) * 2.576
               		ldict['yes'] = (sm, (sm - moe, sm + moe), n, moe)
			n, (smin, smax), sm, sv, ss, sk = stats.describe(no)
               		moe = math.sqrt(sv)/math.sqrt(n) * 2.576
               		ldict['no'] = (sm, (sm - moe, sm + moe), n, moe)
			ret.append((hl, ldict))
		else:
#			print 'Not enough speakers for %s. Skipping.'%hl
			continue
	print 'all yes', sum(all_yes) / len(all_yes)
	print 'all no', sum(all_no) / len(all_no)
	compare_native_speakers_graph(ret)	


#return dictionary of {language : {yes : quality estimate of native turkers, no : quality estimate of nonnative turkers}}
def compare_native_turkers(cutoff=10):
#gu {'gu': {'267409': {'lang': 'gu', 'country': 'IN', 'yrssrc': '18', 'hitlang': 'gu', 'survey': 'IN', 'yrseng': '10'}...
	langs = all_keys('%s/byassign.voc.accepted'%OUTPUT_DIR, 'hitlang')
	lists, throwout = two_way_split('hitlang','lang')
	scores = all_avg_scores('%s/byturker.voc.quality.new%s'%(OUTPUT_DIR,QC,))
	tmap = dictionaries.turker_map()
	quals = dict()
	#for each hit lang, for each native lang, get a list of (turkerid, yrs, qual)
	for hl in lists:
		quals[hl] = dict()
		for nl in lists[hl]:
			quals[hl][nl] = set()
			for assign in lists[hl][nl]:
				turker = tmap[assign]
				yrs = lists[hl][nl][assign]['yrseng']
				try:
		                        yrs = float(yrs)
                		except ValueError:
				#	print 'Unknown years English for turker %s. Skipping'%turker
                        		continue
				try:
					qual = scores[turker]
				except KeyError:
					print 'No quality for turker %s. Skipping'%turker
					continue
				quals[hl][nl].add((turker, yrs, qual))
	
	native_compare_bar_graph(quals, cutoff=cutoff)
	#combine across languages to get a aggregate list of ('native': list of tuples, 'nonnative': list of tuples)
	native = list()
	non = list()
	for hl in quals:
		yes = list()
		no = list()
                for nl in quals[hl]:
			if nl == hl:
	                	for tup in quals[hl][nl]:
					yes.append(tup)
			else:
	                	for tup in quals[hl][nl]:
					no.append(tup)
		if len(yes) > cutoff and len(no) > cutoff:
			y = sum([t[2] for t in yes])
			n = sum([t[2] for t in no])
			#print 'linegraph\t%s\t%d\t%d'%(hl,len(yes),len(no),), y / len(yes), n / len(no)
			native += yes
			non += no
	#get confidence intervals for each bucket
	native_graph_data = list()
	nonnative_graph_data = list()
	all_yes = list()
	all_no = list()
	for y, qs in bucket_lists(native):
		all_yes += qs
		n, (smin, smax), sm, sv, ss, sk = stats.describe(qs)
        	moe = math.sqrt(sv)/math.sqrt(n) * 2.576
		native_graph_data.append((y, (sm, (sm - moe, sm + moe), n, moe)))
	for y, qs in bucket_lists(non):
		all_no += qs
		n, (smin, smax), sm, sv, ss, sk = stats.describe(qs)
        	moe = math.sqrt(sv)/math.sqrt(n) * 2.576
		nonnative_graph_data.append((y, (sm, (sm - moe, sm + moe), n, moe)))
	print 'all yes', sum(all_yes) / len(all_yes)
	print 'all no', sum(all_no) / len(all_no)
	native_compare_line_graph(native_graph_data, nonnative_graph_data)

#a method everyone should run before they die. divide list of (turkerid, yrs, qual) tuples into n k-year buckets. throw out N/As for years 
def bucket_lists(tuple_list, k=5, n=10):
	buckets = list()
	for i in range(0,n*k, k):
		buckets.append(list())
	buckets.append(list())
	for tid, yrs, qual in tuple_list:
		bkt = int(yrs / k)
		if bkt > n : bkt = n
		buckets[bkt].append(qual)
	ret = list()
	for i, l in enumerate(buckets):
		ret.append((i*k, l))
	return ret

#side by side bar of native/non native speaker quality
def compare_native_speakers_graph(ci_tups, title='Graph'):
	plots = list()
        names = [c[0] for c in ci_tups]
	yax_yes = [c[1]['yes'][0] for c in ci_tups] 
	yax_no = [c[1]['no'][0] for c in ci_tups]
	err_yes = [c[1]['yes'][3] for c in ci_tups]
	err_no = [c[1]['no'][3] for c in ci_tups]
        xax = range(len(names))
        plots.append(plt.bar(xax, yax_yes, .4, color='b', yerr=err_yes, ecolor='black'))
        plots.append(plt.bar([x + 0.4 for x in xax], yax_no, .4, color='r', yerr=err_no, ecolor='black'))
        plt.xticks([x + 0.4 for x in xax], [n for n in names], rotation='vertical')
        plt.ylabel('Average assignment quality')
	plt.ylim([0,1])
	plt.xlim([0,len(names)])
	plt.legend(plots, ('native', 'non-native'))
	plt.show()
#	plt.savefig('native-compare-bar.pdf')

#side by side bar of native/non native speaker quality
def native_compare():
	data = compare_native_speakers()
	ttl='Translation quality for native vs. non-native speakers'
	compare_native_speakers_graph(data, title=ttl)

#dictionary of {attr: # turkers}
#e.g. if attr is lang, dictionary is like {'hi': # hi speakers, 'ta': # ta speakers, ... }
#recounts turkers who report multiple languages
def count_turkers(attr):
	counts = count_dicts(get_dicts(read_data('%s/byturker.voc.onelang'%OUTPUT_DIR)),attr)
	mcounts = count_dicts(get_dicts(read_data('%s/byturker.voc.multlang'%OUTPUT_DIR)),attr)
	onelang = {c[0] : c[1] for c in counts}
	multlang = {c[0] : c[1] for c in mcounts}
	alllang = dict()
	for c in multlang:
		combined = multlang[c]
		if c in onelang:
			combined += onelang[c]
		alllang[c] = combined
	for c in onelang:
		if c not in multlang:
			alllang[c] = onelang[c]
	return alllang

#map of country code to country name
def reverse_cntry_map(path):
        lang_data = {}
        for line in open(path).readlines():
		l = line.split()
                country = l[0].strip()
                code = l[1].strip()
                if(code not in lang_data):
                        lang_data[code] = country
        return lang_data

def native_compare_line_graph(native, nonnative):
#(y, (sm, (sm - moe, sm + moe), n, moe))
	names = [n[0] for n in native]
	x = range(len(names))
	y = [n[1][0] for n in native]
	e = [n[1][3] for n in native]
	ny = [nn[1][0] for nn in nonnative]
	ne = [nn[1][3] for nn in nonnative]
	for z in zip(zip(y, [n[1][2] for n in native]), zip(ny, [nn[1][2] for nn in nonnative])):
		print z
	#plt.errorbar(x, y, yerr=e, color='b', linestyle='-', marker='o')
	#plt.errorbar(x, ny, yerr=ne, color='r', linestyle='-', marker='o')
	plt.errorbar(x, y, yerr=e, color='b', marker='o')
	plt.errorbar(x, ny, yerr=ne, color='r', marker='o')
	plt.xticks(x, names)
	plt.title('Native vs. nonnative speaker quality by # of years speaking English')
	plt.show()
	y = [n[1][2] for n in native]
	ny = [nn[1][2] for nn in nonnative]
	plt.plot(x, y, color='b', marker='o')
	plt.plot(x, ny, color='r', marker='o')
	plt.xticks(x, names)
	plt.title('Number of native vs. nonnative turkers by # of years speaking English')
	plt.show()

#scatter plot of quality against # assignments, bubbles sized by # turkers
def quality_scatter(title='Title'):
	#points_to_label = ['VN', 'RO', 'NG', 'AM', 'DZ','RU', 'UK', 'ET', 'PK', 'IN','US','MY','MK','ES', 'ID', '100 turkers']
	points_to_label = ['RO', 'NG', 'AM', 'DZ','RU', 'UK', 'PK', 'IN','US','MY','MK','ES', 'ID', '100 turkers']
	attr = 'country'
	cmap = reverse_cntry_map('ref/countrynames')
	cmap['100 turkers'] = '100 turkers'
#	ci = conf_int_by_attr(attr)
	ci = conf_int_by_attr_turker(attr)
	turker_counts = count_turkers(attr)
	names = list()
	x = list()
	y = list()
	e = list()
	for c in ci:
		if(c in turker_counts and not(ci[c] == None) and (len(ci[c]) > 3)):
			names.append(c)
			y.append(ci[c][0])
			e.append(ci[c][3])
			x.append(ci[c][2])
	names.append('100 turkers')
	y.append(0.9)
	x.append(50000)
	turker_counts['100 turkers'] = 100
        labels = list()
	labelx = list()
	labely = list()
	for nm in points_to_label:
		idx = names.index(nm)
                labels.append(cmap[nm])
                labelx.append(x[idx])
                labely.append(y[idx])
	area = [turker_counts[n] for i,n in enumerate(names)]
	plt.scatter(x, y, s=area)
	plt.xscale('log')
	plt.xlim([.1,1000000])
	plt.ylim([0,1])
	plt.xlabel('Number of assignments', fontsize='14')
	plt.ylabel('Average quality', fontsize='14')
	plt.xticks(fontsize='16')
	plt.yticks(fontsize='16')
	arrows = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0')
	for label, x, y in zip(labels, labelx, labely):
        	plt.annotate(label,xy =(x,y),xytext=(20,10),textcoords='offset points',ha ='left',va='bottom',arrowprops=arrows, fontsize=12)
	plt.savefig('quality-scatter.pdf')

#scatter plot of # assignments against # turkers
def assign_and_turker_plot(tuples):
        points_to_label=['ur','mk','te','ml','ro','es','pl','tl','mr','pt','hi','nl','new','ar','ru','jv','kn','ta','fr','sr']
        langmap = reverse_lang_map('%s/languages'%RAW_DIR)
        datax = [t[1][0] for t in tuples]
        datay = [t[1][1] for t in tuples]
        labels = list()
        labelx = list()
        labely = list()
        for t in tuples:
                if t[0] in points_to_label:
                        labels.append(t[0])
                        labelx.append(t[1][0])
                        labely.append(t[1][1])
        plt.subplots_adjust(bottom = 0.1)
        plt.scatter(datax, datay, marker = 'o')
        plt.ylabel('Number of turkers')
        plt.ylim([0,350])
        plt.xlabel('Number of assignments')
        plt.xlim([0,4000])
        plt.rc('xtick', labelsize=40)
        plt.rc('ytick', labelsize=40)
	arrows = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0')
        for label, x, y in zip(labels, labelx, labely):
                plt.annotate(label,xy=(x,y),xytext=(-10,10),textcoords='offset points',ha='right',va='bottom',arrowprops=arrows,fontsize=20)
	plt.savefig('figures/assign-turk-scatter.pdf')

#get dictionary of {hitlang : # assignments} which includes only accepted assignments for which the turker only reported one language
def one_lang_assigns():
        onelang_turkers = [l['id'] for l in csv.DictReader(open('%s/byturker.voc.onelang'%OUTPUT_DIR), delimiter='\t')]
        tmap = dictionaries.turker_map()
        assigns = dict()
        for line in csv.DictReader(open('%s/byassign.voc.accepted'%OUTPUT_DIR), delimiter='\t'):
                if tmap[line['id']] in onelang_turkers:
                        l = line['hitlang']
                        if l not in assigns:
                                assigns[l] = 0
                        assigns[l] += 1
        return assigns

#return a dictionary of {hitlang: (# assignments, # turkers)
def assign_and_turker_table(onelang=True):
        hitlangs = dict()
	asum = 0
	tsum = 0
        if(onelang):
                assigns = one_lang_assigns()
                turkers = get_turker_dict()
        else:
                assigns = get_assign_dict()
                turkers = get_turker_dict(onelang=False)
        for c in assigns:
                hitlangs[c] = [assigns[c],0]
		asum += assigns[c]
        turkers = get_turker_dict()
        for c in turkers:
                if c not in hitlangs:
                        continue
                hitlangs[c][1] = turkers[c]
		tsum += turkers[c]
	print 'assigns: %d turkers: %d'%(asum, tsum, )
        return sorted(hitlangs.iteritems(), key=operator.itemgetter(1), reverse=True)

#get number of assignments per hit language in dict of {hitlang : assignment count}
def get_assign_dict():
        assigns = dict()
        for line in csv.DictReader(open('%s/byassign.voc.accepted'%OUTPUT_DIR), delimiter='\t'):
                l = line['hitlang']
                if l not in assigns:
                        assigns[l] = 0
                assigns[l] += 1
        return assigns

#return a dictionary of {hitlang : number of turkers} 
#if onelang=True, consider only the turkers who self-reported one native language consistantly
def get_turker_dict(onelang=True):
        turkers = dict()
        if(onelang):
                nmlist = ['onelang']
        else:
                nmlist = ['nolang', 'onelang', 'multlang']
        for num in nmlist:
                for line in csv.DictReader(open('%s/byturker.voc.%s'%(OUTPUT_DIR,num,)), delimiter='\t'):
                        l = line['hitlang']
                        for ll in l.split(';'):
                                ll = ll.strip()
                                if ll == '' or ll == 'N/A':
                                        continue
                                if ll not in turkers:
                                        turkers[ll] = 0
                                turkers[ll] += 1
        return turkers

#pie chart of turkers' native languages
def natlang_pie(tuples):
        langs = reverse_lang_map('%s/languages'%RAW_DIR)
        langs['other'] = 'Other'
        tuples.reverse()
        plt.ax = plt.axes([0.1, 0.1, 0.8, 0.8])
        labels = [t[0] for t in tuples]
        fracs = [t[1] for t in tuples]
        explode=tuple([0.05]*len(fracs))
        colors=('b', 'g', 'r', 'c', 'm', 'y', 'w', '#FF6600')
        patches, texts, autotexts = plt.pie(fracs, labels=labels, explode=explode, colors=colors, autopct='%1.1f', shadow=False, pctdistance=0.9, labeldistance=1.1)
        proptease = fm.FontProperties()
        proptease.set_size('medium')
        plt.setp(autotexts, fontproperties=proptease)
        plt.setp(texts, fontproperties=proptease)
	plt.savefig('figures/natlang-pie.pdf')

#return statistics on turkers' native languages as a list of (language, count) tuples
def natlang_table():
        natlangs = dict()
        for line in csv.DictReader(open('%s/byturker.voc.onelang'%OUTPUT_DIR), delimiter='\t'):
                for lang in line['langs'].split(';'):
                        lang = lang.strip()
                        if lang == '':
                                continue
                        if lang not in natlangs:
                                natlangs[lang] = 0
                        natlangs[lang] += 1
        return sorted(natlangs.iteritems(), key=operator.itemgetter(1), reverse=True)

#group language counts less than 20 into an 'other' category
def clean_tuples(tuples):
        clean = list()
        other = 0
        for lang, count in tuples:
                if count > 20:
                        clean.append((lang,count))
                else:
                        other += count
        clean.append(('other', other))
        return clean

#print by-language statistics as an ugly latex table
def pie_chart_table(tups):
        tot = 0
        langmap = reverse_lang_map('%s/languages'%RAW_DIR)
        langmap['other'] = 'Other'
        print '\\begin{figure}[h]'
        print '\\begin{tabular}{cc}\hline\hline'
        print 'Language&\\# Turkers\\\\'
        print '\\hline'
        for lang, count in tups:
                tot += count
                print '%s&%d\\\\'%(langmap[lang],count,)
        print '\\hline\\\hline'
        print '\\end{tabular}'
        print '\\end{figure}'

#print out country counts in format to be pasted into html file for geomap
def print_data_for_map():
        COUNTRIES = 'ref/countrycodemap'
        countries = dict()
        for line in open(COUNTRIES).readlines():
                name, code = line.split()
                countries[code] = string.capitalize(name)
        full = dict()
        o = count_dicts(get_dicts(read_data('%s/byturker.voc.onelang'%OUTPUT_DIR)),'country')
        n = count_dicts(get_dicts(read_data('%s/byturker.voc.nolang'%OUTPUT_DIR)),'country')
        m = count_dicts(get_dicts(read_data('%s/byturker.voc.multlang'%OUTPUT_DIR)),'country')
        for lang, c in o:
                if not lang in full:
                        full[lang] = 0
                full[lang] += c
        for lang, c in n:
                if not lang in full:
                        full[lang] = 0
                full[lang] += c
        for lang, c in m:
                if not lang in full:
                        full[lang] = 0
                full[lang] += c
        for ctry, count in full.iteritems():
                print "['%s',%d],"%(countries[ctry],count,)

def anova():
	dist = list()
	for a in assign_list:
		if a in scores:
			dist.append(scores[a])
		if(len(dist) == 0):
 			return None
	n, (smin, smax), sm, sv, ss, sk = stats.describe(dist)
	moe = math.sqrt(sv)/math.sqrt(n) * 2.576
	return (sm, (sm - moe, sm + moe), n, moe)


if __name__ == '__main__':
	if(len(sys.argv) < 2 or sys.argv[1] == 'help'):
                print '---USAGE---'
		print './figures.py all: all figures'
		print './figures.py hitlang_qual : bar chart of quality by HIT language'
		print './figures.py exact_match: bar chart of quality by HIT language, side by side bars of overall quality and % exact matches'
		print './figures.py goog: bar chart of quality by HIT language, side by side bars of overall quality and % google matches'
                print './figures.py quality_scatter : scatter of # turkers vs. quality, bubbles sized by # turkers'
               # print './figures.py native_compare : side-by-side bar of native vs. non-native speaker quality'
                print './figures.py assign_turk_scatter : scatter of # turkers vs. # assignments, points labeled by country'
                print './figures.py natlang_pie : pie chart'
                print './figures.py natlang_table : pie chart as table'
                print './figures.py map: print data for googlecharts map'
                exit(0)

	plot = sys.argv[1]
	if(plot == 'all'):
		if not os.path.exists('./figures'): os.mkdir('figures')
		print 'hitlang bar'
		hitlang_qual_turker()
		plt.clf()
		print 'exact match bar'
		exact_match_qual()
		plt.clf()
		print 'google match bar'
		goog_match_qual()
		plt.clf()
		print 'quality scatter'
		quality_scatter()
		plt.clf()
		print 'assign/turker scatter'
                assign_and_turker_plot(assign_and_turker_table())
		plt.clf()
		print 'pie chart'
        	natlang_pie(clean_tuples(natlang_table()))
		plt.clf()
	if(plot == 'hitlang_qual'):
	#	hitlang_qual()
		hitlang_qual_turker()
	if(plot == 'exact_match'):
		exact_match_qual()
	if(plot == 'goog'):
		goog_match_qual()
	if(plot == 'quality_scatter'):
		quality_scatter()
	if(plot == 'native_compare_bar'):
		native_compare()
	if(plot == 'native_compare_line'):
		compare_native_turkers()
        if(plot == 'assign_turk_scatter'):
                assign_and_turker_plot(assign_and_turker_table())
        if(plot == 'natlang_pie'):
        	natlang_pie(clean_tuples(natlang_table()))
        if(plot == 'natlang_table'): 
		pie_chart_table(clean_tuples(natlang_table()))
        if(plot == 'map'): 
	        print_data_for_map()
	if(plot == 'anova'):
		anova()





