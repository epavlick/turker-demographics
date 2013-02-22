import re
import csv
import math
import json
import codecs
import time
import datetime
import operator
import itertools
import dictionaries
import numpy as np
import matplotlib.pyplot as plt
import compile_data_from_raw as dat

HIT_PATH = '/home/steven/Documents/Ellie/Research/demographics/data/dictionary-data-dump-2012-11-13_15:11/hits'
LANG_PATH = '/home/steven/Documents/Ellie/Research/demographics/data/dictionary-data-dump-2012-11-13_15:11/languages'
RAW_ASSIGN = '/home/steven/Documents/Ellie/Research/demographics/data/dictionary-data-dump-2012-11-13_15:11/assignments'
TIME_PATH = '/home/steven/Documents/Ellie/Research/demographics/code/data-files/turker-tuples/assign-times'
#ASSIGN_PATH = '/home/steven/Documents/Ellie/Research/demographics/code/data-files/turker-tuples/byassign.voc'
ASSIGN_PATH = 'output/byassign.voc'

lang_order = ['ur', 'mk', 'te', 'ml', 'es', 'ro', 'tl', 'pl', 'mr', 'pt', 'hi', 'new', 'nl', 'ru', 'kn', 'ta', 'fr', 'ast', 'ar', 'ne', 'sr', 'vi', 'uk', 'gu', 'sh', 'jv', 'id', 'pam', 'it', 'no', 'pa', 'ms', 'hu', 'ceb', 'nn', 'be', 'ja', 'scn', 'bn', 'fi', 'de', 'bpy', 'lb', 'sw', 'el', 'sv', 'hr', 'ca', 'lt', 'war', 'bg', 'tr', 'gl', 'bcl', 'he', 'bs', 'eu', 'is', 'ga', 'da', 'sq', 'zh', 'ilo', 'eo', 'th', 'cs', 'af', 'sk', 'uz', 'ht', 'nap', 'sl', 'lv', 'ko', 'az', 'ka', 'sd', 'hy', 'so', 'su', 'wo', 'ps', 'fa', 'am', 'fy', 'br', 'cy', 'mg', 'bo', 'yo', 'io', 'pms', 'ku', 'nds', 'diq', 'wa']


def get_language_dicts(path, filter_list=None):
	all_dicts = dict()
	hitmap = dictionaries.hit_map()
	langids, langcodes = dat.lang_map()
        hitlangs = dat.hits_language()
	timemap = time_map()
	for assign in csv.DictReader(open(path), delimiter='\t'):
		aid = assign['id']
		if(aid == ''):
			continue
		if(not(filter_list == None) and (aid not in filter_list)):
			continue
		alang =  langids[hitlangs[hitmap[aid]]]
		if not alang in all_dicts:
			all_dicts[alang] = timemap[aid]
		tstart, tend = timemap[aid]
		all_dicts[alang] = (min(all_dicts[alang][0], tstart), max(all_dicts[alang][1], tend))
	return all_dicts

def time_map():
	tdict = dict()
	for line in open(TIME_PATH).readlines():
		aid, start, end = line.split('\t')
		start_t = datetime.datetime.strptime(start.strip(), "%Y-%m-%d %H:%M:%S")
		end_t = datetime.datetime.strptime(end.strip(), "%Y-%m-%d %H:%M:%S")
		tdict[aid] = (start_t, end_t)
	return tdict

def read_times():
	for line in open(TIME_PATH).readlines()[:5]:
		aid, start, end = line.split('\t')
		print start, end
		start_t = datetime.datetime.strptime(start.strip(), "%Y-%m-%d %H:%M:%S")
		end_t = datetime.datetime.strptime(end.strip(), "%Y-%m-%d %H:%M:%S")
		print min(end_t,start_t)

def write_all_times():
        out = open('assign-times', 'w')
        for line in csv.DictReader(open(RAW_ASSIGN)):
                aid = line['id']
                start = line['accept_time']
                end = line['submit_time']
                out.write('%s\t%s\t%s\n'%(aid,start,end,))
        out.close()

def get_total_time(data):
	for lang in sorted(data.iteritems(), key=operator.itemgetter(0)):
		print '%s\t%s'%(lang[0], str(lang[1][1] - lang[1][0]))

def format_for_graph(data):
	#ret = dict()
	ret = list()
	mindate = None
	for l in lang_order:
		lang = data[l]	
		begin = lang[0]
		if(mindate == None or begin < mindate):
			mindate = begin
	for l in lang_order:
		lang = data[l]	
		complete = str(lang[1] - lang[0]).split()[0]
		start = str(lang[0] - mindate).split()[0]
		try:
			i = int(start)
		except ValueError:
			start = 0
#		ret[l] = (str(lang[1] - lang[0]).split()[0], str(lang[0] - mindate).split()[0])
		#ret[l] = (int(complete), int(start))
		ret.append((l,int(complete), int(start), int(complete)+int(start)))
	return sorted(ret, key=operator.itemgetter(3)) 

def time_graph(data):
	num = len(data)
        ind = np.arange(num) #len(data.keys()))     # the x locations for the groups
        width = 0.8       # the width of the bars: can also be len(x) sequence
        lbls = [t[0] for t in data][:num]
	time_to_start = [t[2] for t in data][:num]
	time_to_complete = [t[1] for t in data][:num]
        plt.bar(ind, time_to_start, width, color='r') #, color=colors[i%len(colors)], bottom=cumsum)
        plt.bar(ind, time_to_complete, width, bottom=time_to_start)
        plt.yticks(fontsize='16')
        plt.xticks(ind+width/2, tuple(lbls) ,rotation='vertical', fontsize='16')
	plt.title('Time to complete all HITs')
	print time_to_start
	print time_to_complete
        plt.show()

if __name__ == '__main__':
#	write_all_times()
#	read_times()
	time_graph(format_for_graph(get_language_dicts(ASSIGN_PATH)))


