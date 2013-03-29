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

DATA_DIR = 'output'
tmap = dictionaries.turker_map()

def scores():
        scores = dict()
        for line in open('%s/byturker.voc.quality.new'%DATA_DIR).readlines():
                l = line.split('\t')
		try:
	                scores[l[0]] = float(l[1].strip())
		except ValueError:
			print 'Error', l
			continue
        return scores

def cl_list():
	s = scores()
	assigns = [l.strip() for l in open('%s/byassign.voc.validclpair'%DATA_DIR).readlines()]
	score_dist = list()
	for a in assigns:
		t = tmap[a]
		if t in s:
			score_dist.append(s[t])
	return score_dist

def noncl_list():
	s = scores()
	assigns = [l.strip() for l in open('%s/byassign.voc.invalidclpair'%DATA_DIR).readlines()]
	score_dist = list()
	for a in assigns:
		t = tmap[a]
		if t in s:
			score_dist.append(s[t])
	return score_dist

def natlang_list(match=True):
	s = scores()
	score_dist = list()
        for line in csv.DictReader(open('%s/byassign.voc.accepted'%DATA_DIR), delimiter='\t'):
		a = line['id']
		if match:
			use = line['lang'] == line['hitlang']
		else:
			use = not(line['lang'] == line['hitlang'])
		if use:
			t = tmap[a]
			if t in s:
				score_dist.append(s[t])
	return score_dist

def yrseng_list(cutoff = 10):
	s = scores()
	score_dist = list()
        for line in csv.DictReader(open('%s/byassign.voc.accepted'%DATA_DIR), delimiter='\t'):
		a = line['id']
		if line['yrseng'] >= cutoff:
			t = tmap[a]
			if t in s:
				score_dist.append(s[t])
	return score_dist

def full_list():
	s = scores()
	score_dist = [s[t] for t in s]
	return score_dist

def anova(lists):
	base = lists['all']
	print 'all', stats.describe(base)
	for l in lists:
		if not l == 'all':
			print l, stats.describe(lists[l])
			print stats.f_oneway(base, lists[l])

def print_for_matlab():
	s = scores()
	turkers = dict()
	cl = [l.strip() for l in open('%s/byassign.voc.validclpair'%DATA_DIR).readlines()]
	noncl = [l.strip() for l in open('%s/byassign.voc.invalidclpair'%DATA_DIR).readlines()]
	

if __name__ == '__main__':
	lists = dict()
	lists['all'] = full_list()	
	lists['cl'] = cl_list()	
	lists['noncl'] = noncl_list()	
	lists['natlang'] = natlang_list()	
	lists['non_natlang'] = natlang_list(match=False)	
	lists['yrseng'] = yrseng_list()	
	anova(lists)

