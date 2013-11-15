#!/bin/python
# -*- coding: utf-8 -*- 

# hit-id | lang | word | control_translation | google_transalation | worker_1_id | worker_1_response | worker_2_id | worker_2_response | ...

import sys
import operator

byassign = {}

idmap = {line.strip().split()[1] : line.strip().split()[0] for line in open('ref/approved-ids').readlines() + open('ref/rejected-ids').readlines()}

approved = set([idmap[line.strip().split()[1]] for line in open('ref/approved-ids').readlines()])
rejected = set([idmap[line.strip().split()[1]] for line in open('ref/rejected-ids').readlines()])

worker_map = {}

for line in sys.stdin:
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

		if aid not in byassign[lang] : byassign[lang][aid] = {'overlap_c' : 0, 'overlap_nc' : 0, 'total_c' : 0, 'total_nc' : 0}
		
		if goog.lower() == translation.lower() : 
			if control == 'NA' : byassign[lang][aid]['overlap_nc'] += 1	
			else : byassign[lang][aid]['overlap_c'] += 1	
		if control == 'NA' : byassign[lang][aid]['total_nc'] += 1	
		else : byassign[lang][aid]['total_c'] += 1	
		

print 'lang\tassign\tworker\tmatch-overall\tmatch-c\tmatch-nc\tnum-match-overall\tnum-match-c\tnum-match-nc\ttotal\tstatus'
for lang in byassign:
	for aid in byassign[lang]:
		if aid in approved : status = 'approved'
		elif aid in rejected : status = 'rejected'
		num_c = float(byassign[lang][aid]['overlap_c'])
		num_nc = float(byassign[lang][aid]['overlap_nc'])
		total_c = float(byassign[lang][aid]['total_c'])
		total_nc = float(byassign[lang][aid]['total_nc'])
		try : overall = (num_c+num_nc)/(total_c+total_nc)
		except ZeroDivisionError : overall = 0
		try : c = num_c/total_c
		except ZeroDivisionError : c = 0
		try : nc = num_nc/total_nc
		except ZeroDivisionError : nc = 0
		params = (lang,aid,worker_map[aid],overall,c,nc,num_c+num_nc,num_c,num_nc,total_c+total_nc,status)
		print '%s\t%s\t%s\t%.03f\t%.03f\t%.03f\t%.03f\t%.03f\t%.03f\t%.03f\t%s'%params

