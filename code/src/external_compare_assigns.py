#!/bin/python

#format for external overlap file is
#source_word target_word 1=control_word 1=target_word_known 1=observed_in_mturk_data 1=in_external_dictionary

import re
import os
import sys
import csv

EXTERN_OVERLAP = '../../dictionaries/anni/externalOverlap'
ASSIGNS = 'output/byassign.voc.accepted'

def reg(s):
	return s.strip().lower()

if len(sys.argv) < 2:
	print 'USAGE: ./external_compare.py TRANSLATIONS.OUT'
	print 'TRANSLATIONS.OUT is file containing the word-to-word translations received from each assignment'
	exit(0)

tout = sys.argv[1]

pair_scores = dict()

for dict_file in os.listdir(EXTERN_OVERLAP):
	if not re.match('dict.(.*)',dict_file): continue
	d, lang = dict_file.split('.')
	if lang not in pair_scores: pair_scores[lang] = dict()
	for line in open('%s/%s'%(EXTERN_OVERLAP,dict_file,)).readlines():
		src, tran, is_control, known_correct, observed, is_match = line.strip().split('\t')
		pair_scores[lang][(reg(src),reg(tran))] = int(is_match)

assign_pairs = dict()

for line in open(tout).readlines():
	t = line.strip().split('\t')
	assign_pairs[t[0]] = t[1:]

assign_scores = dict()

for line in csv.DictReader(open(ASSIGNS), delimiter='\t'):
	lang = line['hitlang']
	aid = line['id']
	if lang in pair_scores:
		if aid not in assign_pairs:
			print aid, 'skipped'
			continue
		if aid not in assign_scores: assign_scores[aid] = [0.0,0.0,0.0]
		for pair in assign_pairs[aid]:
			try : src, trans = pair.strip().split(':')
			except ValueError: 
				print pair, 'skipped'
				continue
			if not reg(tran) == '':
				try:
					assign_scores[aid][0] += pair_scores[lang][(reg(src), reg(tran))]
					assign_scores[aid][1] += 1
				except KeyError: assign_scores[aid][2] += 1 #word pair not in reference dictionaries

for lang, (match, tot, skipped) in assign_scores.iteritems():
	print '%s\t%.03f\t%d\t%d'%(lang, match/tot, tot, skipped)

