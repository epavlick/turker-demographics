#!/bin/python

import csv

RAW_DIR = '/home/steven/Documents/Ellie/Research/demographics/data/dictionary-data-dump-2012-11-13_15:11'
CLPAIRS = 'ref/cl-pairs.csv'

def lang_map():
        lang_data = {}
        num_data = {}
        for line in csv.DictReader(open('%s/languages'%RAW_DIR)):
                lang = line['name'].lower()
                lid = line['id']
                if(lang not in lang_data):
                        lang_data[lang] = line['prefix']
                if(lid not in num_data):
                        num_data[lid] = line['prefix']
        return num_data, lang_data

def code_map():
	ret = dict()
	for l in open('ref/countrycodemap').readlines():
		ll = l.split('\t')
		ret[ll[0]] = ll[1].strip()
	return ret

def get_valid_pairs():
        codes, words = lang_map()
        cmap = code_map()
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

pairs = get_valid_pairs() 

for lang in pairs: 
	
	print lang+'\t'+','.join(pairs[lang])	

