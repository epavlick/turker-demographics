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
	assigns = [l.strip() for l in open('%s/byassign.voc.validclpair'%DATA_DIR).readlines()]
	return [tmap[a] for a in assigns]

def noncl_list():
	assigns = [l.strip() for l in open('%s/byassign.voc.invalidclpair'%DATA_DIR).readlines()]
	return [tmap[a] for a in assigns]

def natlang_list(match=True):
	turkers = list()
        for line in csv.DictReader(open('%s/byassign.voc.accepted'%DATA_DIR), delimiter='\t'):
		a = line['id']
		if match:
			use = line['lang'] == line['hitlang']
		else:
			use = not(line['lang'] == line['hitlang'])
		if use:
			turkers.append(tmap[a])
	return turkers

def yrseng_vals(cutoff = 10):
	turkers = dict()
        for line in csv.DictReader(open('%s/byassign.voc.accepted'%DATA_DIR), delimiter='\t'):
		a = line['id']
		try:
			yrs = int(line['yrseng'])
			turkers[tmap[a]] = yrs
		except ValueError:
			continue
	return turkers 

def yrseng_list(cutoff = 10, less=False):
	turkers = list()
        for line in csv.DictReader(open('%s/byassign.voc.accepted'%DATA_DIR), delimiter='\t'):
		a = line['id']
		try:
			if less: use = (int(line['yrseng']) < cutoff)
			else: use = (int(line['yrseng']) >= cutoff)
			if use:
				turkers.append(tmap[a])
		except ValueError:
			continue
	return turkers 

def full_list():
	s = scores()
	score_dist = [s[t] for t in s]
	return score_dist

def format_for_matlab():
	ret = list()
	scs = scores()
	cl = cl_list()	
	noncl = noncl_list()	
	natlang = natlang_list()	
	non_natlang = natlang_list(match=False)	
	yrseng = yrseng_list()	
	nonyrseng = yrseng_list(less=True)	
	for s in scs:
		clmatch = 'na'
		if s in cl: clmatch = 'cl'
		elif s in noncl: clmatch = 'noncl'
		nat = 'na'
		if s in natlang: nat = 'natspkr'
		elif s in non_natlang: nat = 'nonnatspkr'
		yrs = 'NaN'
#		if s in yrseng: yrs = yrseng[s]
		if s in yrseng: yrs = 'yrs>10'
		elif s in nonyrseng : yrs = 'yrs<10'
		if not (yrs == 'NaN' or nat == 'na' or clmatch == 'na'):
#		if not (nat == 'na' or clmatch == 'na'):
			ret.append((scs[s], clmatch, nat, yrs))
	return ret

def print_for_matlab(tups, threshold=0.7):
	y = [int(t[0]>threshold) for t in tups]
	g1 = [t[1] for t in tups]
	g2 = [t[2] for t in tups]
	g3 = [t[3] for t in tups]
	print 'y=', y
	print 'g1 = {',
	for g in g1:
		print "'%s';"%g,
	print '};'
	print 'g2 = {',
	for g in g2:
		print "'%s';"%g,
	print '};'
	print 'g3 = {',
	for g in g3:
		print "'%s';"%g,
	print '};'
	

if __name__ == '__main__':
	print_for_matlab(format_for_matlab())
