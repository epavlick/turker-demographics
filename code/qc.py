import sys
import csv
import math
import numpy
import scipy
import operator
import itertools
from scipy import stats
from scipy.stats import norm
import matplotlib.pyplot as plt

RAW_DIR = '../data/dictionary-data-dump-2012-11-13_15:11/'
OUTPUT_DIR = 'output'

def turker_map():
        tmap = dict()
        for line in open('%s/byassign.workerids.voc'%OUTPUT_DIR).readlines()[1:]:
                assign, worker = line.split()
                tmap[assign.strip()] = worker.strip()
        return tmap

def qual_map():
        qual_data = {}
        for line in csv.DictReader(open('%s/byassign.voc.quality'%OUTPUT_DIR), delimiter='\t'):
                assign = line['id']
                qual = line['avg']
                if(assign not in qual_data):
                        if qual == 'N/A':
                                qual_data[assign] = qual
                        else:
                                qual_data[assign] = float(qual)
        return qual_data

#map of word id to word
def word_map():
	words = dict()
        for line in csv.DictReader(open('%s/dictionary'%RAW_DIR)):
		wid = line['id']
		word = line['translation']
		if wid not in words:
			words[wid] = word
	return words

#map of pair id to word pair
def pair_map():
	pairs = dict()
        for line in csv.DictReader(open('%s/syn_hits_data'%RAW_DIR)):
		pid = line['id']
		word = line['translation']
		syn = line['synonym']
		if pid not in pairs:
			pairs[pid] = (word,syn)
	return pairs

#return (list of pair ids that are know synonyms, list of pair ids that are known nonsynonyms)
def get_syn_lists():
	syns = list()
	nonsyns = list()
        for line in csv.DictReader(open('%s/synonyms'%RAW_DIR)):
		syns.append(line['id'])
        for line in csv.DictReader(open('%s/non_synonyms'%RAW_DIR)):
		nonsyns.append(line['id'])
	return (syns, nonsyns)

#get a dictionary of word: list of acceptable synonyms. filter list of assignment ids used to restrict list of synonyms to come only from certain assignments
def read_all_syns(filter_list=None):
	words = word_map()
	pairs = pair_map()
	syns = dict()
        for line in csv.DictReader(open('%s/syn_hits_results'%RAW_DIR)):
		if(not(filter_list == None) and (line['assignment_id'] not in filter_list)):
			continue
		if(line['are_synonyms'] == 'yes'):
			pair = pairs[line['pair_id']]
			syn = pair[1]
			if syn not in syns:
				syns[syn] = set()
			syns[syn].add(pair[0])
	return syns

#returns list of syn HIT assignments which passed their controls
def get_syns_quality_by_assign(path):
	syns, nonsyns = get_syn_lists()
	quals = list()
        for line in csv.DictReader(open(path)):
		aid = line['assignment_id']
		if line['is_control'] == '1':		
			pair = line['pair_id']
			if(line['are_synonyms'] == 'yes' and pair in syns):
				quals.append(aid) 
			elif(line['are_synonyms'] == 'no' and pair in nonsyns):
				quals.append(aid) 
	return quals 

#returns a dictionary of {assignment : # of controls attempted, # of controls correct, average performance on controls}
def get_quality_by_assign(path):
	good = get_syns_quality_by_assign('%s/syn_hits_results'%RAW_DIR)
	syns = read_all_syns(filter_list=good)
	words = word_map()
        data = {}
        for line in csv.DictReader(open(path)):
                assign = line['assignment_id']
		translation = line['translation']	
		word_id = line['word_id']	
                if(assign not in data):
                        data[assign] = {'total': 'N/A', 'syns': 'N/A'} 
		if word_id in words:
			word = words[word_id]
			if word in syns:
                        	if data[assign]['total'] == 'N/A':
                        		data[assign] = {'total': 0, 'syns': 0} 
				if translation in syns[word]:
					data[assign]['syns'] += 1
				data[assign]['total'] += 1
	ret = dict()
	for a in data:
		if data[a]['total'] == 0:
			ret[a] = (data[a]['total'], data[a]['syns'], 0)				
		elif data[a]['total'] == 'N/A':
			ret[a] = (data[a]['total'], data[a]['syns'], 'N/A')				
		else:
			ret[a] = (data[a]['total'],data[a]['syns'],float(data[a]['syns'])/data[a]['total'])
	return ret

#write quality data to a file
def write_avg_quals(data, fname):
	f = open(fname, 'w')
	f.write('%s\t%s\t%s\t%s\n' % ('id','total','syns','avg',))
	for k in data:
		if data[k][1] == 'N/A':
			f.write('%s\t%s\t%s\t%s\n' % (k,data[k][0],data[k][1],data[k][2],))
		else:
			f.write('%s\t%.04f\t%.04f\t%.04f\n' % (k,data[k][0],data[k][1],data[k][2],))
	f.close()

#get the average quality per turker and write to a file
def quality_by_turker(fname):
	out = open(fname, 'w')
        all_turkers = dict()
        tmap = turker_map()
        quals = qual_map()
        for assign in tmap:
		worker = tmap[assign]
                q = quals[assign]
		if q == 'N/A':
			continue
		if not(worker in all_turkers):
                        all_turkers[worker] = {'num':0, 'denom':0}
                all_turkers[worker]['num'] += float(q)
                all_turkers[worker]['denom'] += 1
	for t in all_turkers:
		out.write('%s\t%.04f\n'%(t, all_turkers[t]['num']/all_turkers[t]['denom'],))
	out.close()

if __name__ == '__main__':
	if sys.argv[1] == 'assign': 
		write_avg_quals(get_quality_by_assign('%s/voc_hits_results'%RAW_DIR), '%s/byassign.voc.quality'%OUTPUT_DIR)
	if sys.argv[1] == 'turker':
		quality_by_turker('%s/byturker.voc.quality'%OUTPUT_DIR)




