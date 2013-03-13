import re
import csv
import sys
import math
import json
import codecs
import os.path
import operator
import itertools
from scipy import stats
import compile_data_from_raw as dat

RAW_DIR = '/home/steven/Documents/Ellie/Research/demographics/data/dictionary-data-dump-2012-11-13_15:11/'
DICT_PATH = '/home/steven/Documents/Ellie/Research/demographics/code.clean/translations.out'
CLPAIRS = '/home/steven/Documents/Ellie/Research/demographics/data/cl-pairs.csv'
OUTPUT_DIR = 'output'
DICT_DIR = 'dictionaries'

def read_valid_clpairs():
	codes, words = dat.lang_map()
	cmap = dat.code_map()
	valid_pairs = dict()
	for line in csv.DictReader(open(CLPAIRS)):
		lang = words[line['Input.language'].lower()]
		if not lang in valid_pairs:
			valid_pairs[lang] = dict()
		main = cmap[line['Answer.primary_country'].lower()]
		if not main in valid_pairs[lang]:
			valid_pairs[lang][main] = 0
		valid_pairs[lang][main] += 1
		for ctry in [cmap[c.lower()] for c in line['Answer.countries'].split('|') if not c=='']:
			if not ctry in valid_pairs[lang]:
				valid_pairs[lang][ctry] = 0
			valid_pairs[lang][ctry] += 1
	ret = dict()
	for p in valid_pairs:
		ret[p] = list()
		for pp in valid_pairs[p]:
			if valid_pairs[p][pp] >= 2:
				ret[p].append(pp)
	return ret
	
def write_invalid_clpairs():
	valid = read_valid_clpairs()
	outfile = open('%s/byassign.voc.invalidclpair'%OUTPUT_DIR, 'w')
	for line in csv.DictReader(open('%s/byassign.voc.accepted'%OUTPUT_DIR), delimiter='\t'):
		aid = line['id']
		if line['country'] == 'N/A':
			print aid
			continue
		if line['country'] not in valid[line['hitlang']]:
			outfile.write('%s\n'%aid)
	outfile.close()

def write_valid_clpairs():
	valid = read_valid_clpairs()
	outfile = open('%s/byassign.voc.validclpair'%OUTPUT_DIR, 'w')
	for line in csv.DictReader(open('%s/byassign.voc.accepted'%OUTPUT_DIR), delimiter='\t'):
		aid = line['id']
		if line['country'] in valid[line['hitlang']]:
			outfile.write('%s\n'%aid)
	outfile.close()

def yrs_list(cutoff):
	ret = list()
	for line in csv.DictReader(open('%s/byassign.voc.accepted'%OUTPUT_DIR), delimiter='\t'):
		aid = line['id']
		yrs = line['yrssrc']
		if(yrs == 'N/A'):
			continue
		if(float(yrs) >= cutoff):
			ret.append(aid)
	return ret

def word_map(path):
	words = dict()
	print 'reading vocab'
        for i,line in enumerate(codecs.open(path, encoding='utf-8').readlines()[1:]):
		if(i % 10000 == 0):
			print i
		comps = line.split(',')
		if(len(comps) > 1):
			wid = comps[0]
			word = comps[1]
			if wid not in words:
				words[wid] = word
	return words

#read raw assignment data and return a dictionary of {assign_id : [list of translations]}
#alist is a list of assignment ids used to restrict translations to only come from certain assignments
def get_translations_by_assign(path, alist=None):
        data = {}
	for line in csv.DictReader(open(path)):
                assign = line['id']
		if(not(alist == None) and (assign not in alist)):
			continue
                if(assign not in data):
                        data[assign] = list()
                results = json.loads(line['result'])
		for k in results:
			if re.match('word(.*)', k):
				data[assign].append((k, results[k]))
	return data

#parse the word id as it appears in mturk results and return word id as it appears in database 
def justid(wid):
	if re.match('(.*)-(.*)', wid):
		pieces = wid.split('-')
	else:
		pieces = wid.split(',')
	num = pieces[1]
	return (num[:len(num)-1].lstrip('0'), num[len(num)-1])

#take dictionary of {aid : list of translations} where translation list gives translations of word ids, and return 
#dictionary of {aid : list of translations} where translation list gives translations of actual words
def resolve_word_ids(data):
	retdict = dict()
	words = word_map('%s/vocabulary'%RAW_DIR)
	for a in data:
		retdict[a] = list()
		for wid,trans in data[a]:
			just_wid, iscontrol = justid(wid)	
			if iscontrol == '0':
				if just_wid in words:
					word = words[just_wid]
					retdict[a].append((word,trans))
	return retdict
			

def get_quality(path):
        data = {}
        for line in csv.DictReader(open(path)):
                assign = line['assignment_id']
                if(assign not in data):
                        data[assign] = {'tot_score':0, 'num_scores':0}
		this_score = line['quality']
		if(not this_score == ''):
			data[assign]['tot_score'] += float(this_score)    		
			data[assign]['num_scores'] += 1		
	return data

def write_avg_quals(data, fname):
	f = open(fname, 'w')
	f.write('%s\t%s\t%s\t%s\n' % ('id','total','syns','avg',))
	for k in data:
		if data[k][1] == 'N/A':
			f.write('%s\t%s\t%s\t%s\n' % (k,data[k][0],data[k][1],data[k][2],))
		else:
			f.write('%s\t%.04f\t%.04f\t%.04f\n' % (k,data[k][0],data[k][1],data[k][2],))
	f.close()

def all_avg_scores(path):
	scores = dict()
        for line in open(path).readlines():
		l = line.split('\t')
		try:
			scores[l[0]] = float(l[3].strip())
		except:
			continue
	return scores

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

def turker_qual_map():
        qual_data = {}
        for line in open('%s/byturker.voc.quality'%OUTPUT_DIR).readlines()[1:]:
                assign, qual = line.split()
                if(assign not in qual_data):
                        qual_data[assign] = float(qual)
        return qual_data

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

def hit_map():
        lang_data = {}
        for line in csv.DictReader(open('%s/assignments'%RAW_DIR)):
                assign = line['id']
                hit = line['hit_id']
                if(assign not in lang_data):
                        lang_data[assign] = hit
        return lang_data

def write_translations(data, fname):
	print 'writing dict file'
	outfile = codecs.open(fname, encoding='utf-8', mode='w', errors='ignore')
	for i,aid in enumerate(data):
		if(i%100 == 0):
			print i
		outfile.write('%s\t'%aid)
		for word,tran in data[aid]:
			try:
				outfile.write('%s:%s\t'%(word,re.sub('\n',' ',tran)))
			except UnicodeDecodeError:
				print 'unicode error, ignoring'
				outfile.write('<decode-err>\t')
		outfile.write('\n')
	outfile.close()

def turker_map():
	tmap = dict()
	for line in open('%s/byassign.workerids.voc'%OUTPUT_DIR).readlines()[1:]:
		assign, worker = line.split()
		tmap[assign.strip()] = worker.strip()
	return tmap		

def assign_dict():
	ret = dict()
	for line in csv.DictReader(open('%s/byassign.voc'%OUTPUT_DIR), delimiter='\t'):
		ret[line['id']] = line
	return ret

#return a dictionary of {language : {country : list of turkers who submitted HITs in that language}}
def count_turkers_verbose(path, qual_cutoff=None, strict=False, filter_list=None, match=True):
	all_dicts = dict()
	hitmap = hit_map()
	langids, langcodes = dat.lang_map()
        hitlangs = dat.hits_language()
	tmap = turker_map()
	quals = qual_map()
	assignmap = assign_dict()
	for assign in open(path).readlines():
		comps = assign.strip().split('\t')
		aid = comps[0]
		if aid == '' or aid not in assignmap:
			continue
  		#if match, filter_list is list of assignments to include, otherwise, filter_list is list of assignments to skip
                if(match):
                        list_pass = not(filter_list == None) and (aid not in filter_list)
                else:
                        list_pass = not(filter_list == None) and (aid in filter_list)
                if(list_pass):
                        continue
                #if strict, assignments must be greater than qual_cutoff to pass, otherwise, assignments can be greater or equal to qual_cutoff
                if(strict):
                        qual_pass = not(qual_cutoff == None) and (quals[aid] == 'N/A' or quals[aid] <= qual_cutoff)
                else:
                        qual_pass = not(qual_cutoff == None) and (quals[aid] == 'N/A' or quals[aid] < qual_cutoff)
		if qual_pass:
			print 'below cutoff', aid, quals[aid]
			continue
		alang = langids[hitlangs[hitmap[aid]]]
		country = assignmap[aid]['country']
		if not(alang in all_dicts):
			all_dicts[alang] = dict()
		if country not in all_dicts[alang]:
			all_dicts[alang][country] = list()
		all_dicts[alang][country].append(tmap[aid])
	return all_dicts

#return a dictionary of {language : list of turkers who submitted HITs in that language}
def count_turkers(path, qual_cutoff=None, strict=False, filter_list=None, match=True):
	all_dicts = dict()
	hitmap = hit_map()
	langids, langcodes = dat.lang_map()
        hitlangs = dat.hits_language()
	tmap = turker_map()
	quals = qual_map()
	for assign in open(path).readlines():
		comps = assign.strip().split('\t')
		aid = comps[0]
		if aid == '' or aid not in tmap:
			continue
  		#if match, filter_list is list of assignments to include, otherwise, filter_list is list of assignments to skip
                if(match):
                        list_pass = not(filter_list == None) and (aid not in filter_list)
                else:
                        list_pass = not(filter_list == None) and (aid in filter_list)
                if(list_pass):
                        continue
                #if strict, assignments must be greater than qual_cutoff to pass, otherwise, assignments can be greater or equal to qual_cutoff
                if(strict):
                        qual_pass = not(qual_cutoff == None) and (quals[aid] == 'N/A' or quals[aid] <= qual_cutoff)
                else:
                        qual_pass = not(qual_cutoff == None) and (quals[aid] == 'N/A' or quals[aid] < qual_cutoff)
		if(qual_pass):
			print 'below cutoff', aid, quals[aid]
			continue
		alang = langids[hitlangs[hitmap[aid]]]
		if not(alang in all_dicts):
			all_dicts[alang] = list()
		all_dicts[alang].append(tmap[aid])
	return {l: list(set(all_dicts[l])) for l in all_dicts}

#get estimated turker quality by language, returns dictionary of {language : {'num': # of correct QC words, 'denom': # of QC words} }
def get_language_dicts_quals_turkers(path, qual_cutoff=None, strict=False, filter_list=None, match=True):
	all_dicts = dict()
	tmap = turker_map()
	hitmap = hit_map()
	langids, langcodes = dat.lang_map()
        hitlangs = dat.hits_language()
	quals = qual_map()
	tquals = turker_qual_map()
	for assign in open(path).readlines():
		comps = assign.strip().split('\t')
		aid = comps[0]
		if(aid == '' or aid not in tmap):
			continue
		#if match, filter_list is list of assignments to include, otherwise, filter_list is list of assignments to skip
		if(match):
			list_pass = not(filter_list == None) and (aid not in filter_list)
		else:
			list_pass = not(filter_list == None) and (aid in filter_list)
		if(list_pass):
			continue
		#if strict, assignments must be greater than qual_cutoff to pass, otherwise, assignments can be greater or equal to qual_cutoff
		if(strict):
			qual_pass = not(qual_cutoff == None) and (quals[aid] == 'N/A' or quals[aid] <= qual_cutoff)
		else:
			qual_pass = not(qual_cutoff == None) and (quals[aid] == 'N/A' or quals[aid] < qual_cutoff)
		if(qual_pass):
			print 'below cutoff', aid, quals[aid]
			continue
		alang =  langids[hitlangs[hitmap[aid]]]
		if not(alang in all_dicts):
			all_dicts[alang] = {'num':0, 'denom':0}
		all_dicts[alang]['num'] += tquals[tmap[aid]]
		all_dicts[alang]['denom'] += 1
	return all_dicts

def get_language_dicts_quals(path, qual_cutoff=None, strict=False, filter_list=None):
	all_dicts = dict()
	hitmap = hit_map()
	langids, langcodes = dat.lang_map()
        hitlangs = dat.hits_language()
	quals = qual_map()
	for assign in open(path).readlines():
		comps = assign.strip().split('\t')
		aid = comps[0]
		if(aid == ''):
			continue
		if(not(filter_list == None) and (aid not in filter_list)):
			continue
		if(not(qual_cutoff == None) and strict and (quals[aid] == 'N/A' or quals[aid] <= qual_cutoff)):
			print 'below cutoff', aid, quals[aid]
			continue
		if(not(qual_cutoff == None) and not(strict) and (quals[aid] == 'N/A' or quals[aid] < qual_cutoff)):
			print 'below cutoff', aid, quals[aid]
			continue
		alang =  langids[hitlangs[hitmap[aid]]]
		if not(alang in all_dicts):
			all_dicts[alang] = {'num':0, 'denom':0}
		all_dicts[alang]['num'] += quals[aid]
		all_dicts[alang]['denom'] += 1
	return all_dicts

def get_language_dicts(path, qual_cutoff=None, strict=False, filter_list=None, match=True):
	all_dicts = dict()
	tmap = turker_map()
	hitmap = hit_map()
	langids, langcodes = dat.lang_map()
        hitlangs = dat.hits_language()
	quals = qual_map()
	tquals = turker_qual_map()
	filtered = 0
	for cnt, assign in enumerate(open(path).readlines()):
		comps = assign.strip().split('\t')
		aid = comps[0]
		if cnt%1000 == 0:
			print aid
		if(aid == ''): # or aid not in tmap):
			continue
		#if match, filter_list is list of assignments to include, otherwise, filter_list is list of assignments to skip
		if(match):
			list_pass = not(filter_list == None) and (aid not in filter_list)
		else:
			list_pass = not(filter_list == None) and (aid in filter_list)
		if(list_pass):
			filtered += 1
			continue
		#if strict, assignments must be greater than qual_cutoff to pass, otherwise, can be greater or equal to qual_cutoff
		if(strict):
			qual_pass = not(qual_cutoff == None) and (quals[aid] == 'N/A' or quals[aid] <= qual_cutoff)
		else:
			qual_pass = not(qual_cutoff == None) and (quals[aid] == 'N/A' or quals[aid] < qual_cutoff)
		if(qual_pass):
			print 'below cutoff', aid, quals[aid]
			continue
		alang =  langids[hitlangs[hitmap[aid]]]
		if not alang in all_dicts:
			all_dicts[alang] = dict()
		for pair in comps[1:]:
			try:
				word = pair[:pair.index(':')]
				trans = pair[pair.index(':')+1:]
			except ValueError:
				print word
				continue
			if not(trans.strip() == ''):
				if not word in all_dicts[alang]:
					all_dicts[alang][word] = [trans.strip().lower()]
				else:
					all_dicts[alang][word].append(trans.strip().lower())
	print 'FILTERED %d ASSIGNMENTS'%filtered
	return all_dicts

def write_dicts_quals(data, filename='quals'):
	dictfile = open(filename, 'w')
	for lang in data:
		print lang
		qual = float(data[lang]['num']) / float(data[lang]['denom'])
		dictfile.write('%s\t%.04f\n'%(lang,qual,))
	dictfile.close()

#write file containing language and number of turkers in that language
def write_dicts_turkers(data, filename='numturkers'):
	dictfile = open(filename, 'w')
	for lang in data:
		print lang
		num = len(list(set(data[lang])))
		dictfile.write('%s\t%.04f\n'%(lang,num,))
	dictfile.close()

def write_dicts(data, file_prefix='dictionaries/dictionary'):
	for lang in data:
		print lang
		dictfile = open('%s.%s'%(file_prefix,lang,), 'w')
		for word in data[lang]:
			dictfile.write('%s\t'%word)
			for trans in set(data[lang][word]):
				dictfile.write('%s,'%trans)
			dictfile.write('\n')
		dictfile.close()

#write file containing language id followed by list of XX:YYY pairs, where XX is a country and YYY is the number of turkers for the language from country XX				
def write_turker_lists(tlist, fname):
	out = open(fname , 'w')
	for l in tlist:
		out.write('%s\t'%l)
		for c in tlist[l]:
			out.write('%s:%d\t'%(c,len(list(set(tlist[l][c])))))
		out.write('\n')
	out.close()	

def id_list(path):
	idlist = list()
	for line in csv.DictReader(open(path), delimiter='\t'):
		idlist.append(line['id'].strip())
	return idlist

#clpair.numturkers  clpair.turkerqual  nonclpair.numturkers  nonclpair.turkerqual
def meta_data():
	totin = 0
	totout = 0
	inqual = 0
	outqual = 0
	indist = list()
	outdist = list()
	for count, qual in zip(open('%s/clpair.numturkers'%DICT_DIR).readlines(), open('%s/clpair.turkerqual'%DICT_DIR).readlines()):
		lang, num = count.strip().split('\t')
		lang, score = qual.strip().split('\t')
		num = int(float(num.strip()))
		score = float(score.strip())
		indist += [score] * num
		totin += num
		inqual += (num*score)		
	for count, qual in zip(open('%s/nonclpair.numturkers'%DICT_DIR).readlines(), open('%s/nonclpair.turkerqual'%DICT_DIR).readlines()):
		lang, num = count.strip().split('\t')
		lang, score = qual.strip().split('\t')
		num = int(float(num.strip()))
		score = float(score.strip())
		outdist += [score] * num
		totout += num
		outqual += (num*score)		
	i_n, (i_min, i_max), i_m, i_v, i_s, i_k = stats.describe(indist)
        i_moe = math.sqrt(i_v)/math.sqrt(i_n) * 2.576
	o_n, (o_mon, o_max), o_m, o_v, o_s, o_k = stats.describe(outdist)
        o_moe = math.sqrt(o_v)/math.sqrt(o_n) * 2.576
        print 'In region: %d Turkers, Avg. score %0.3f (%0.3f, %.03f)'%(i_n, i_m, i_m - i_moe, i_m + i_moe)
        print 'Out of region: %d Turkers, Avg. score %0.3f (%0.3f, %.03f)'%(o_n, o_m, o_m - o_moe, o_m + o_moe)
#	print 'Number of Turkers in region: %d' % totin
#	print 'Number of Turkers out of region: %d' % totout
#	print 'Avg. score of Turkers in region: %.03f' %(float(inqual) / totin)
#	print 'Avg. score of Turkers out of region: %.03f' %(float(outqual) / totout)

if __name__ == '__main__':
	
	if(len(sys.argv) < 2):
		print '---USAGE---' 
	#	print 'full_data: NOT DEBUGGED' 
	#	print 'by_region: compare in-region and out-of-region dictionaries' 
		print 'choose either (if neither, run for all):' 
		print '\tmatch: run for in-region (default)' 
		print '\tnonmatch: run for out-of-region' 
		print 'choose one of:' 
		print '\tdictionaries: compile word-to-word dictionaries' 
		#print '\tdict_qual: estimate quality of dictionaries' 
		print '\tturker_qual: estimate quality of workers' 
		print '\tturker_counts: get counts of workers' 
		print '\tmeta_stats: get overall in/out region stats' 
		exit(0)

	#check if raw translation files have alread been processed. if not, process them	
	if not(os.path.exists(DICT_PATH)):
		print '%s does not exist. Reloading translation data from raw. This will take forever and ever.'%DICT_PATH
		assign_list = id_list('%s/byassign.voc.accepted'%OUTPUT_DIR)
		write_translations(resolve_word_ids(get_translations_by_assign('%s/assignments'%RAW_DIR, alist=assign_list)), DICT_PATH)
	
	#extract dictionaries with no restrictions
	if('full_data' in sys.argv):	
		print "NOT DEBUGGED"
		exit(0)
	
	#extract data by cl pairs
#	if('by_region' in sys.argv):	
	if not os.path.exists('%s/byassign.voc.validclpair'%OUTPUT_DIR):
		write_valid_clpairs()
	if not os.path.exists('%s/byassign.voc.invalidclpair'%OUTPUT_DIR):
		write_invalid_clpairs()
	if('nonmatch' in sys.argv):
		base='%s/nonclpair'%DICT_DIR
		mtch = True #False
		clpairs = [l.strip() for l in open('%s/byassign.voc.invalidclpair'%OUTPUT_DIR).readlines()]
	elif('match' in sys.argv):
		base='%s/clpair'%DICT_DIR
		mtch = True
		clpairs = [l.strip() for l in open('%s/byassign.voc.validclpair'%OUTPUT_DIR).readlines()]
	else:
		base='%s/all'%DICT_DIR
		mtch = True
		valid = [l.strip() for l in open('%s/byassign.voc.validclpair'%OUTPUT_DIR).readlines()]
		invalid = [l.strip() for l in open('%s/byassign.voc.invalidclpair'%OUTPUT_DIR).readlines()]
		clpairs = valid + invalid
	if('dictionaries' in sys.argv):
		prefix='%s/dictionary'%base
		print 'writing data to %s'%prefix
		dicts = get_language_dicts(DICT_PATH, qual_cutoff=0, strict=False, filter_list=clpairs)
		write_dicts(dicts, file_prefix=prefix)
	if('dict_qual' in sys.argv):
		print "NOT DEBUGGED"
		exit(0)
		prefix='%s.qual'%base
		dicts = get_language_dicts_quals(DICT_PATH, qual_cutoff=0, strict=False, filter_list=clpairs)
		write_dicts_quals(dicts, file_prefix=prefix) 
	if('turker_qual' in sys.argv):
		print "Estimating turker quality by language"
		prefix='%s.turkerqual'%base
		dicts = get_language_dicts_quals_turkers(DICT_PATH, qual_cutoff=0, strict=False,  filter_list=clpairs, match=mtch)
		write_dicts_quals(dicts, filename=prefix)
	if('turker_counts' in sys.argv):
		print "Counting number of turkers per language"
		prefix='%s.numturkers'%base
		tdata = count_turkers(DICT_PATH, qual_cutoff=0, strict=False,  filter_list=clpairs, match=mtch)
		write_dicts_turkers(tdata, filename=prefix)
		prefix='%s.turkerlist'%base
		tdatav = count_turkers_verbose(DICT_PATH, qual_cutoff=0, strict=False,  filter_list=clpairs, match=mtch)
		write_turker_lists(tdatav, prefix)
	if('meta_stats' in sys.argv):
		print "Overall statistics for in and out of region turkers"
		meta_data()

#	langlist = yrs_list(5)
#	write_dicts(get_language_dicts(DICT_PATH, qual_cutoff=0, strict=False, filter_list=langlist), file_prefix='dictionaries/yrs/dictionary')
