#!/bin/python

#format for external overlap file is
#source_word target_word 1=control_word 1=target_word_known 1=observed_in_mturk_data 1=in_external_dictionary

import re
import os
import sys

EXTERN_OVERLAP = '../../dictionaries/anni/externalOverlap'

def reg(s):
	return s.strip().lower()

if len(sys.argv) < 2:
	print 'USAGE: ./external_compare.py DICTIONARY_ROOT'
	print 'DICTIONARY_ROOT is directory containing dictionar.lang files to be validated'
	exit(0)

root_dir = sys.argv[1]

pair_scores = dict()

for dict_file in os.listdir(EXTERN_OVERLAP):
	if not re.match('dict.(.*)',dict_file): continue
	d, lang = dict_file.split('.')
	if lang not in pair_scores: pair_scores[lang] = dict()
	for line in open('%s/%s'%(EXTERN_OVERLAP,dict_file,)).readlines():
		src, tran, is_control, known_correct, observed, is_match, in_ext = line.strip().split('\t')
		if int(in_ext) == 1: pair_scores[lang][(reg(src),reg(tran))] = int(is_match)

lang_scores = dict()

for dict_file in os.listdir(root_dir):
	if not re.match('dictionary.(.*)',dict_file): continue
	d, lang = dict_file.split('.')
	if lang in pair_scores:
		if lang not in lang_scores: lang_scores[lang] = [0.0,0.0,0.0]
		for line in open('%s/%s'%(root_dir,dict_file,)).readlines():
			try: src, trans = line.strip().split('\t')
			except ValueError: continue
			for tran in trans.split(','):
				if not reg(tran) == '':
					try:
						lang_scores[lang][0] += pair_scores[lang][(reg(src), reg(tran))]
						lang_scores[lang][1] += 1
					except KeyError: lang_scores[lang][2] += 1

for lang, (match, tot, skipped) in lang_scores.iteritems():
	if tot == 0 : print '%s\t%.03f\t%d\t%d'%(lang, 0, tot, skipped)
	else: print '%s\t%.03f\t%d\t%d'%(lang, match/tot, tot, skipped)



