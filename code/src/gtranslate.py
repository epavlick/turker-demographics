import sys
import csv
import math
import codecs
import operator
import itertools
import compile_data_from_raw as dat
from apiclient.discovery import build
from settings import settings

RAW_DIR = '../data/dictionary-data-dump-2012-11-13_15:11/'
OUTPUT_DIR = 'output'

supported_langs = ['af', 'sq', 'ar', 'be', 'bg', 'ca', 'zh', 'zh', 'hr', 'cs', 'da', 'nl', 'en', 'et', 'eo', 'fi', 'fr', 'gl', 'de', 'el', 'he', 'hi', 'hu', 'is', 'id', 'ga', 'it', 'ja', 'ko', 'lv', 'lt', 'mk', 'ms', 'fa', 'pl', 'pt', 'ro', 'ru', 'sr', 'sk', 'sl', 'es', 'sw', 'sv', 'th', 'tr', 'uk', 'vi', 'cy', 'hy', 'az', 'eu', 'ka', 'gu', 'kn', 'la', 'ta', 'te', 'ur', ]

#map of word id to word
def write_word_list(fname):
	out = open(fname, 'w')
        for line in csv.DictReader(open('%s/vocabulary'%RAW_DIR)):
		wid = line['id']
		word = line['word']
		lang = line['language_id']
		out.write('%s\t%s\t%s\n'%(wid, word, numlangmap[lang],))
	out.close()

def translate_word_list(inname, outname):
	out=codecs.open(outname,mode='w',encoding='utf-8')
	done = [i.strip() for i in open('tids').readlines()]
	service = build('translate','v2',developerKey=settings["google_translate_key"])
	for line in open(inname).readlines():
		try:
		  	wid, w, lang = line.strip().split()
		except ValueError:
			continue
		# Build a service object for interacting with the API. Visit
		# the Google APIs Console <http://code.google.com/apis/console>
		# to get an API key for your own application.
		if(wid in done):
			continue
 
		word=unicode(w, 'utf-8')

		if lang.strip() in supported_langs:
			print w
			translation= service.translations().list(source=lang.strip(),target='en',q=[word.strip()]).execute()['translations'][0]['translatedText']
			out.write("%s\t%s\t%s\t%s\n"%(wid,word,translation,lang,))
 
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

def write_syn_dict(syns, fname):
	outfile = open(fname, 'w')
	for w in syns:
		outfile.write('%s\t'%w)
		for s in syns[w]:
			outfile.write('%s\t'%s)
		outfile.write('\n')
	outfile.close()

def write_avg_quals(data, fname):
	f = open(fname, 'w')
	f.write('%s\t%s\t%s\t%s\n' % ('id','total','syns','avg',))
	for k in data:
		if data[k][1] == 'N/A':
			f.write('%s\t%s\t%s\t%s\n' % (k,data[k][0],data[k][1],data[k][2],))
		else:
			f.write('%s\t%.04f\t%.04f\t%.04f\n' % (k,data[k][0],data[k][1],data[k][2],))
	f.close()

if __name__ == '__main__':
	#write_word_list('dict')
	translate_word_list('input4', 'translated_dictionary_5')



