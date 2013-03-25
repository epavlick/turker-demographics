import sys
import csv
import math
import string
import operator
import itertools
import dictionaries
import compile_data_from_raw as dat

RAW_DIR = '/home/steven/Documents/Ellie/Research/demographics/data/dictionary-data-dump-2012-11-13_15:11'
OUTPUT_DIR = 'output'

goog_langs = ['el', 'eo', 'zh', 'af', 'vi', 'is', 'it', 'kn', 'cs', 'cy', 'ar', 'eu', 'et', 'gl', 'id', 'es', 'ru', 'az', 'nl', 'pt', 'tr', 'lv', 'lt', 'th', 'gu', 'ro', 'ca', 'pl', 'ta', 'fr', 'bg', 'ms', 'hr', 'de', 'da', 'fa', 'fi', 'hy', 'hu', 'ja', 'he', 'te', 'sr', 'sq', 'ko', 'sv', 'ur', 'sk', 'uk', 'sl', 'sw']

#map of assignment ID to turker ID
def turker_map(hittype='voc'):
        tmap = dict()
        for line in open('%s/byassign.workerids.%s'%(OUTPUT_DIR,hittype,)).readlines()[1:]:
                assign, worker = line.split()
                tmap[assign.strip()] = worker.strip()
        return tmap

#map of assignment ID to quality score of that assignment, or N/A 
def qual_map(path):
        qual_data = {}
        #for line in csv.DictReader(open('%s/byassign.voc.quality.exactmatch'%OUTPUT_DIR), delimiter='\t'):
        #for line in csv.DictReader(open('%s/byassign.googmatch'%OUTPUT_DIR), delimiter='\t'):
        for line in csv.DictReader(open(path), delimiter='\t'):
                assign = line['id']
                qual = line['avg']
                if(assign not in qual_data):
                        if qual == 'N/A':
                                qual_data[assign] = qual
                        else:
                                qual_data[assign] = float(qual)
        return qual_data

#map of word id to word
def word_map(get_lang=False):
	words = dict()
        for line in csv.DictReader(open('%s/dictionary'%RAW_DIR)):
		wid = line['id']
		lang = line['language_id']
		word = line['translation'].strip().lower()
		if wid not in words:
			if get_lang:
				orig = line['word'].strip().lower()
				words[wid] = (word, orig, lang)
			else:
				words[wid] = word
	return words

#map of pair id to word pair
def pair_map():
	pairs = dict()
        for line in csv.DictReader(open('%s/syn_hits_data'%RAW_DIR)):
		pid = line['id']
		word = line['translation'].strip().lower()
		syn = line['synonym'].strip().lower()
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

def get_goog_translations():
	trans = dict()
	for line in open('goog_trans').readlines():
		wid, word, tran, lang = line.strip().split('\t')
		trans[wid.strip()] = tran.strip()		
	return trans

#get a dictionary of word: list of acceptable synonyms. filter list of assignment ids used to restrict list of synonyms to come only from certain assignments
def read_all_syns(filter_list=None, use_related=True, exact_match_only=False):
	words = word_map()
	pairs = pair_map()
	syns = dict()
        for line in csv.DictReader(open('%s/syn_hits_results'%RAW_DIR)):
		if(not(filter_list == None) and (line['assignment_id'] not in filter_list)):
			continue
		if(use_related):
			use = (line['are_synonyms'] == 'yes') or (line['are_synonyms'] == 'related')
		else:
			use = (line['are_synonyms'] == 'yes')
		if(use):
			pair = pairs[line['pair_id']]
			syn = pair[1].strip().lower()
			if syn not in syns:
				syns[syn] = set()
				syns[syn].add(syn)
			if(not(exact_match_only)):
				syns[syn].add(pair[0].strip().lower())
	return syns

#get a dictionary of word: list of acceptable synonyms. filter list of assignment ids used to restrict list of synonyms to come only from certain assignments
def write_all_syns():
        words = word_map(get_lang=True)
        data = {}
	syns = dict()
	numlangmap, langmap = dat.lang_map()
        for word_id in words: 
		word, orig, lang = words[word_id]
		lang = numlangmap[lang]
                if lang not in syns:
			syns[lang] = list()
		syns[lang].append((orig,word))
	write_control_dicts(syns)

def write_control_dicts(data, file_prefix='controls/dictionary'):
        for lang in data:
                print lang
                dictfile = open('%s.%s'%(file_prefix,lang,), 'w')
                for word, trans in data[lang]:
                        dictfile.write('%s\t%s\n'%(word,trans,))
                dictfile.close()


#returns list of syn HIT assignments which passed their controls
#is_control=1 - synonyms control - yes, is_control=2 - non-synonyms control - no
#For control 1 answer must be yes, for control 2 answer should be no.
def get_syns_quality_by_assign(path, required_ctrl=1):
	syns, nonsyns = get_syn_lists()
	grades=dict()
	quals = list()
        for line in csv.DictReader(open(path)):
		aid = line['assignment_id']
		#grade all controls first
		if line['is_control'] == '1':		
			pair = line['pair_id']
			assignment_id=line['assignment_id']
			if(line['are_synonyms'] == 'yes' and pair in syns):
				if assignment_id in grades:
					grades[assignment_id]=grades[assignment_id]+1
				else:
					grades[assignment_id]=1
		if line['is_control'] == '2':		
			pair = line['pair_id']
			if(line['are_synonyms'] == 'no' and pair in nonsyns):
				if assignment_id in grades:
					grades[assignment_id]=grades[assignment_id]+1
				else:
					grades[assignment_id]=1

	#filter all assignment_id with both correct controls
	for assignment_id in grades:
		if grades[assignment_id]>=required_ctrl:
			quals.append(assignment_id) 
	return quals 

def get_syns_quality_by_turker(path,alist,qual_cutoff=0.7):
	grades=dict()
        tmap = turker_map(hittype='syn')
        for a in tmap:
		w = tmap[a]
		if w not in grades:
			grades[w] = {"num":0, "denom":0}
		#if the assignment passed controls, give the turker credit
		if a in alist:
			grades[w]["num"] += 1
		grades[w]["denom"] += 1
	approved_turkers = list()
	for w in grades:
		avg_score = float(grades[w]["num"])/grades[w]["denom"]
		if(avg_score > qual_cutoff):
			approved_turkers.append(w)
	return [a for a in tmap if tmap[a] in approved_turkers]
#	print sorted([float(grades[w]["num"])/grades[w]["denom"] for w in grades], reverse=True)

def write_syn_dict(syns, fname):
	outfile = open(fname, 'w')
	for w in syns:
		outfile.write('%s\t'%w)
		for s in syns[w]:
			outfile.write('%s\t'%s)
		outfile.write('\n')
	outfile.close()

#returns a dictionary of {assignment : # of controls attempted, # of controls correct, average performance on controls}
def get_quality_by_assign(path):
	gooda = get_syns_quality_by_assign('%s/syn_hits_results'%RAW_DIR)
	good = get_syns_quality_by_turker('%s/syn_hits_results'%RAW_DIR, gooda)
	syns = read_all_syns(filter_list=good, exact_match_only=False)
	words = word_map()
        data = {}
        for line in csv.DictReader(open(path)):
                assign = line['assignment_id']
		translation = line['translation']	
		word_id = line['word_id']	
                if(assign not in data):
                        data[assign] = {'total': 'N/A', 'syns': 'N/A'} 
		if word_id in words:
			word = words[word_id].strip().lower()
			if word in syns:
                        	if data[assign]['total'] == 'N/A':
                        		data[assign] = {'total': 0, 'syns': 0} 
				if translation in syns[word]:
					data[assign]['syns'] += 1
				data[assign]['total'] += 1
			else:
				print 'Could not find', word, 'in synonym dictionary. Skipping.'
		else:
			print 'Could not find', word_id, 'in word dictionary. Skipping'
	ret = dict()
	for a in data:
		if data[a]['total'] == 0:
			ret[a] = (data[a]['total'], data[a]['syns'], 0)				
		elif data[a]['total'] == 'N/A':
			ret[a] = (data[a]['total'], data[a]['syns'], 'N/A')				
		else:
			ret[a] = (data[a]['total'],data[a]['syns'],float(data[a]['syns'])/data[a]['total'])
	return ret

#returns a dictionary of {assignment : # of controls attempted, # of controls correct, average performance on controls}
def get_good_and_bad_translations(path):
	controls = dict()
	numlangmap, langmap = dat.lang_map()
	gooda = get_syns_quality_by_assign('%s/syn_hits_results'%RAW_DIR)
	good = get_syns_quality_by_turker('%s/syn_hits_results'%RAW_DIR, gooda)
	syns = read_all_syns(filter_list=good, exact_match_only=False)
	words = word_map(get_lang=True)
        data = {}
        for line in csv.DictReader(open(path)):
                assign = line['assignment_id']
		translation = line['translation'].strip().lower()	
		word_id = line['word_id']	
                if(assign not in data):
                        data[assign] = {'total': 'N/A', 'syns': 'N/A'} 
		if word_id in words:
			word, orig, lang = words[word_id]
			word = word.strip().lower()
                	lang = numlangmap[lang]
			if word in syns:
				if lang not in controls:
					controls[lang] = dict()
				if orig not in controls[lang]:
					controls[lang][orig] = {'pos':set(), 'neg':set()}
				if translation in syns[word]:
					controls[lang][orig]['pos'].add(translation)
				else:
					controls[lang][orig]['neg'].add(translation)
			else:
				print 'Could not find', word, 'in synonym dictionary. Skipping.'
		else:
			print 'Could not find', word_id, 'in word dictionary. Skipping'

	pos = dict()
	neg = dict()
	for lang in controls:
		pos[lang]=[(orig,string.join(controls[lang][orig]['pos'],',')) for orig in controls[lang] if len(controls[lang][orig]['pos'])>0]
		neg[lang]=[(orig,string.join(controls[lang][orig]['neg'],',')) for orig in controls[lang] if len(controls[lang][orig]['neg'])>0]
	write_control_dicts(pos, file_prefix='poscontrols/dictionary')
	write_control_dicts(neg, file_prefix='negcontrols/dictionary')

#returns a dictionary of {assignment : # of controls attempted, # of controls correct, average performance on controls}
def get_goog_match_by_assign(path):
        matches = get_goog_translations()
        words = word_map()
        data = {}
	numlangmap, langmap = dat.lang_map()
	hitlangs = dat.hits_language()
	hits = dictionaries.hit_map()
        for line in csv.DictReader(open(path)):
                assign = line['assignment_id']
                translation = line['translation']
                word_id = line['word_id']
                if(assign not in data):
                        data[assign] = {'total': 'N/A', 'syns': 'N/A'}
		assign_lang = numlangmap[hitlangs[hits[assign]]]
		if(assign_lang not in goog_langs):
			print "Skipping lang",  assign_lang, "not supported by google"
			continue
                if word_id in matches: 
			if data[assign]['total'] == 'N/A': 
				data[assign] = {'total': 0, 'syns': 0} 
			if translation.strip().lower() == matches[word_id].strip().lower(): 
				data[assign]['syns'] += 1
                        data[assign]['total'] += 1
#                else:
 #                       print 'Could not find', assign, word_id, 'in google dictionary. Skipping'
        ret = dict()
        for a in data:
                if data[a]['total'] == 0:
                        ret[a] = (data[a]['total'], data[a]['syns'], 0)
                elif data[a]['total'] == 'N/A':
			print a, "is N/A"
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
def quality_by_turker(fname, path):
	out = open(fname, 'w')
        all_turkers = dict()
        tmap = turker_map()
        quals = qual_map(path)
        for assign in tmap:
		worker = tmap[assign]
                q = quals[assign]
  		if(assign == '' or assign not in tmap):
                        continue
		if q == 'N/A':
			continue
		if not(worker in all_turkers):
                        all_turkers[worker] = {'num':0, 'denom':0}
                all_turkers[worker]['num'] += float(q)
                all_turkers[worker]['denom'] += 1
	for t in all_turkers:
		out.write('%s\t%.04f\n'%(t, all_turkers[t]['num']/all_turkers[t]['denom'],))
	out.close()

def turker_qual_map():
        qual_data = {}
        for line in open('%s/byturker.voc.quality.new'%OUTPUT_DIR).readlines()[1:]:
                assign, qual = line.split()
                if(assign not in qual_data):
                        qual_data[assign] = float(qual)
        return qual_data

#get the average quality per turker and write to a file
def quality_by_lang(fname, path):
	out = open(fname, 'w')
        all_langs= dict()
        tmap = turker_map()
        quals = turker_qual_map()
	for nlang in ['nolang', 'onelang', 'multlang']:
	        for turker in csv.DictReader('%s/byturker.voc.%s'%(OUTPUT_DIR,nlang,)):
			worker = tmap[assign]
                	q = quals[assign]
  			if(assign == '' or assign not in tmap):
                	        continue
			if q == 'N/A':
				continue
			if not(worker in all_turkers):
                	        all_turkers[worker] = {'num':0, 'denom':0}
                	all_turkers[worker]['num'] += float(q)
                	all_turkers[worker]['denom'] += 1
	for t in all_turkers:
		out.write('%s\t%.04f\n'%(t, all_turkers[t]['num']/all_turkers[t]['denom'],))
	out.close()

#get the average quality per turker and write to a file
def googmatch_by_turker(fname, path):
	out = open(fname, 'w')
        all_turkers = dict()
        tmap = turker_map()
        quals = qual_map(path)
        for assign in tmap:
		worker = tmap[assign]
                q = quals[assign]
  		if(assign == '' or assign not in tmap):
                        continue
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
	if sys.argv[1] == 'assignments': 
		write_avg_quals(get_quality_by_assign('%s/voc_hits_results'%RAW_DIR), '%s/byassign.voc.quality.new'%OUTPUT_DIR)
	if sys.argv[1] == 'turker':
		quality_by_turker('%s/byturker.voc.quality.new'%OUTPUT_DIR, '%s/byassign.voc.quality.new'%OUTPUT_DIR)
	if sys.argv[1] == 'goog':
		write_avg_quals(get_goog_match_by_assign('%s/voc_hits_results'%RAW_DIR), '%s/byassign.googmatch'%OUTPUT_DIR)
		googmatch_by_turker('%s/byturker.googmatch'%OUTPUT_DIR,'%s/byassign.googmatch'%OUTPUT_DIR)
	if sys.argv[1] == 'controls':
#		write_all_syns()
		get_good_and_bad_translations('%s/voc_hits_results'%RAW_DIR)




