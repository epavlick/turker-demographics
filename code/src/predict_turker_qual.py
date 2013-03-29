import os
import re
import csv
import sys
import string
import random
import os.path
import argparse
import operator

import pickle
import dictionaries

import math
import numpy
import scipy
from scipy import stats
from scipy.stats import norm

from sklearn.cross_validation import KFold
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import cross_val_score
from sklearn.linear_model import LogisticRegression

DATA_DIR = 'output'
tmap = dictionaries.turker_map()

def pr(clf, X, Y):
        """Print precision, recall, and accuracie for error detection classifier"""
        tp = 0.0
        fp = 0.0
        tn = 0.0
        fn = 0.0
        total = 0.0
        for x,y in zip(X,Y):
                total += 1
                yhat = clf.predict(x)
                if y == 0:
                        if yhat == 0: tn += 1
                        elif yhat == 1: fp += 1
                elif y == 1:
                        if yhat == 0: fn += 1
                        elif yhat == 1: tp += 1
        a =  (tp + tn) / total
	if (tp + fp) == 0: p = 0
	else: p = tp / (tp + fp)
        if (tp + fn) == 0: r = 0
        else: r = tp / (tp + fn)
        print 'Guessed Positive: %.03f\tGuessed Negative: %.03f'%(tp+fp,tn+fn)
        print 'Total Positive: %.03f\tTotal Negative: %.03f'%(tp+fn,tn+fp)
        print 'Precision: %.03f\tRecall: %.03f\tAccuracy: %.03f'%(p,r,a,)



def cv_clf(X, Y):
        """Prints 3fold cross validation accuracie of SVM on labels Y and features X"""
        res = cross_val_score(LogisticRegression(), X, Y)
	return res

def train_clf(X, Y):
        """Trains SVM on features X and labels Y"""
        #params = [{'C':[.01, .1, 1, 10, 100], 'kernel':['linear', 'poly', 'rbf']}]
        #clf = GridSearchCV(SVC(), params, refit=True)
        clf = LogisticRegression()
        clf.fit(X, Y)
        #print clf.best_params_
        return clf

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

def get_xy():
	exmpls = list()
	scs = scores()
	cl = cl_list()	
	noncl = noncl_list()	
	natlang = natlang_list()	
	non_natlang = natlang_list(match=False)	
	#yrseng = yrseng_vals()	
	yrseng = yrseng_list()	
	nonyrseng = yrseng_list(less=True)	
	for s in scs:
		clmatch = None
		if s in cl: clmatch = 1
		elif s in noncl: clmatch = 0
		nat = None
		if s in natlang: nat = 1
		elif s in non_natlang: nat = 0
		yrs = None
		if s in yrseng: yrs = 1
		elif s in nonyrseng: yrs = 0
		#if s in yrseng: yrs = yrseng[s]
		if not(clmatch == None or nat == None or yrs == None):
			exmpls.append((scs[s], clmatch, nat, yrs))
	Y = [t[0] for t in exmpls]
	X = [[t[1], t[2], t[3]] for t in exmpls]
	sortxy = sorted(zip(Y, X))
	return [xy[0] for xy in sortxy], [xy[1] for xy in sortxy]

if __name__ == '__main__':
	Y, X = get_xy()
	for cutoff in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
		YY = [int(y > cutoff) for y in Y]
		print cutoff, sum(YY),
		YY = [int(y < cutoff) for y in Y]
		print sum(YY)
	print
	for cutoff in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
		YY = [int(y > cutoff) for y in Y]
		sz = min(sum(YY), len(YY) - sum(YY))
		print sz
		Xt = X[:sz] + X[len(X) - sz:]
		Yt = YY[:sz] + YY[len(YY) - sz:]
		#equalize distribution between classes
		clf = train_clf(Xt, Yt)
		print clf.coef_
	        #pickle.dump(clf, open('turker_clf', 'w'))
		r = cv_clf(Xt,Yt)	
		print cutoff, r, sum(r)/len(r)
		pr(clf,Xt,Yt)
		print


