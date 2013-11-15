#!/bin/python
# -*- coding: utf-8 -*- 

# hit-id | lang | word | control_translation | google_transalation | worker_1_id | worker_1_response | worker_2_id | worker_2_response | ...
# hit-id | word | synonym | control_judgement | worker_1_id | worker_1_judgement | ...

import sys
import csv
import operator
from settings import settings

byassign = {}

ids = open('ref/approved-ids').readlines()+open('ref/rejected-ids').readlines()

idmap = {line.strip().split()[1]: line.strip().split()[0] for line in ids}
approved = set([idmap[line.strip().split()[1]] for line in open('ref/approved-ids').readlines()])
rejected = set([idmap[line.strip().split()[1]] for line in open('ref/rejected-ids').readlines()])

gmatch = csv.DictReader(open('results/data/googmatch.turkers.txt'), delimiter='\t')
worker_gmatch = {line['worker']: float(line['match']) for line in gmatch}

worker_map = {}
synonyms = {}

CUTOFF = settings['synonym_control_cutoff']

#first pass to determine which synonym graders to trust
worker_scores = {}
for line in open('data/pass-2').readlines():
	hitid, word, synonym, control_judgement, judgements = line.strip().split('\t',4)
	if control_judgement == 'NA' : continue
	for j in judgements.split('\t'):
		worker, judgement = j.split(':')
		if worker not in worker_scores: worker_scores[worker] = {'correct' : 0.0, 'total' : 0.0}
		if judgement == control_judgement : worker_scores[worker]['correct'] += 1	
		worker_scores[worker]['total'] += 1	

approved_workers = [worker for worker in worker_scores if (worker_scores[worker]['correct']/worker_scores[worker]['total']) > CUTOFF]

for line in open('data/pass-2').readlines():
	hitid, word, synonym, control_judgement, judgements = line.strip().split('\t',4)
	if word.lower() not in synonyms : synonyms[word.lower()] = set()
	for j in judgements.split('\t'):
		worker, judgement = j.split(':')
		if worker in approved_workers:
			if judgement == 'yes' : synonyms[word.lower()].add(synonym.lower())

for line in open('data/pass-1').readlines():
	hitid, lang, word, control, goog, responses = line.split('\t', 5)
	for response in responses.split('\t'):
		t = response.strip().split(':')
		if len(t) > 1 : 
			worker = t[0]
			translation = t[1]
		else:
			worker = t[0]
			translation = ''
		
		taid = '%s-%s'%(hitid, worker)
		aid = idmap[taid]

		worker_map[aid] = worker

		if lang not in byassign: byassign[lang] = {}

		if aid not in byassign[lang]: byassign[lang][aid] = {
			'correct': 0, 
			'correct_syn': 0, 
			'total': 0, 
		}
		
		if control == 'NA' : continue

		control = control.lower()
		
		if control == translation.lower() : 
			byassign[lang][aid]['correct'] += 1	
		if (control == translation.lower()) or (control in synonyms and translation.lower() in synonyms[control]):
			byassign[lang][aid]['correct_syn'] += 1	
		
		byassign[lang][aid]['total'] += 1

print 'lang\tassign\tworker\toverall\toverall-syn\tnum-correct\tnum_syn\tnum-total\tstatus'
for lang in byassign:
	for aid in byassign[lang]:
		if aid in approved : status = 'approved'
		elif aid in rejected : status = 'rejected'
		try : overall = float(byassign[lang][aid]['correct'])/(byassign[lang][aid]['total'])
		except ZeroDivisionError : overall = 0
		try : overall_syn = float(byassign[lang][aid]['correct_syn'])/(byassign[lang][aid]['total'])
		except ZeroDivisionError : overall_syn = 0
		worker = worker_map[aid]

		if worker_gmatch[worker] >= settings['google_overlap_cutoff'] : continue

		num_correct = byassign[lang][aid]['correct']
		num_syn = byassign[lang][aid]['correct_syn']
		num_total = byassign[lang][aid]['total']
		params = (lang,aid,worker,overall,overall_syn,num_correct,num_syn,num_total,status)
		print '%s\t%s\t%s\t%.03f\t%.03f\t%.03f\t%.03f\t%.03f\t%s'%params

