import re
import csv
import itertools
import operator
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import string

COUNTRIES = 'ref/countrycodemap'
RAW_DIR = '../data/dictionary-data-dump-2012-11-13_15:11/'
DICT_DIR = 'dictionaries'

def reverse_lang_map(path):
        lang_data = {}
        for line in csv.DictReader(open(path)):
                lang = line['name']
                prefix = line['prefix']
                if(prefix not in lang_data):
                        lang_data[prefix] = re.sub('_',' ',lang)
        return lang_data
	
def country_breakdown():
        dict_file='%s/clpair.turkerlists'%DICT_DIR
	data = dict()
	for line in open(dict_file).readlines():
		comps = line.split()
		lang = comps[0]
		breakdown = [(c.split(':')[0], int(c.split(':')[1])) for c in comps[1:]]
		data[lang] = breakdown
	return {k: data[k] for k in data if not k == 'total'}	

def dictionary_stats_turker():
        dict_files=['%s/nonclpair.numturkers'%DICT_DIR, '%s/clpair.numturkers'%DICT_DIR]
        data = dict()
        for line in open(dict_files[0]).readlines():
                lang, count = line.split()
                data[lang] = (float(count), 0)
        for line in open(dict_files[1]).readlines():
                lang, count = line.split()
                data[lang] = (data[lang][0], float(count))
	ret = list()
	for d in data:
		ret.append((d, data[d][0], data[d][1], data[d][0] + data[d][1]))
        return ret 

def dictionary_stats_turkerqual():
        dict_files=['%s/nonclpair.turkerqual.strict'%DICT_DIR, '%s/clpair.turkerqual.strict'%DICT_DIR]
        data = dict()
        for line in open(dict_files[0]).readlines():
                lang, count = line.split()
                data[lang] = (float(count), 0)
        for line in open(dict_files[1]).readlines():
                lang, count = line.split()
                data[lang] = (data[lang][0], float(count))
        return data

def summary_table_condensed():
	tquals = dictionary_stats_turkerqual()
	tdata = sorted(dictionary_stats_turker(), key=operator.itemgetter(3), reverse=True)[:20]
	cbreakdown = country_breakdown()
	langmap = reverse_lang_map('%s/languages'%RAW_DIR)
	countries = dict()
	for line in open(COUNTRIES).readlines():
		name, code = line.split()
		countries[code] = string.capitalize(name)
	countries['US'] = 'US'
	countries['UK'] = 'UK'
	countries['AE'] = 'UAE'
	countries['AE'] = 'UAE'
	print '\\begin{figure}[h]'
	print '\\footnotesize'
	print '\\begin{tabular}{llll}'
	print '\\multicolumn{4}{c}{Number of turkers per language}\\\\'
	print '\\hline\\hline'
	print '&\\multicolumn{2}{c}{Avg. turker quality (\\# Turkers)}&Primary locations\\\\'
	print '&In region&Out of region&of turkers in region\\\\'
	print '\\hline\\hline'
	for d in tdata:
		lang = d[0]
                nomatch, match= tquals[lang]
		total = int(d[3])
		numin = int(d[2])
		numout = int(d[1])
		cstring = ''
		all_countries = [pp for pp in sorted(cbreakdown[lang], key=operator.itemgetter(1), reverse=True) if not (pp[0] == 'N/A')]
		for p in all_countries[:3]:
			cstring += '%s (%d) '%(countries[p[0]],p[1],)
		if(match < nomatch):
			print '%s&%.03f (%d) &\\textbf{%.03f} (%d)&%s\\\\'%(langmap[lang],match,numin,nomatch,numout,cstring)
		elif(nomatch < match):
			print '%s&\\textbf{%.03f} (%d)&%.03f (%d)&%s\\\\'%(langmap[lang],match,numin,nomatch,numout,cstring)
	print '\\hline\\hline'
	print '\\end{tabular}'
	print '\\end{figure}'

if __name__ == '__main__':
	summary_table_condensed()

