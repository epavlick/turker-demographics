import re
import sys
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

OUTPUT_DIR = 'output'
RAW_DIR = '/home/steven/Documents/Ellie/Research/demographics/data/dictionary-data-dump-2012-11-13_15:11/'

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
	print "Reading data"
	tdict = dict()
	for line in open('%s/byassign.times'%OUTPUT_DIR).readlines():
		aid, start, end = line.split('\t')
		start_t = datetime.datetime.strptime(start.strip(), "%Y-%m-%d %H:%M:%S")
		end_t = datetime.datetime.strptime(end.strip(), "%Y-%m-%d %H:%M:%S")
		tdict[aid] = (start_t, end_t)
	return tdict

def write_all_times():
        out = open('%s/byassign.times'%OUTPUT_DIR, 'w')
        for line in csv.DictReader(open('%s/assignments'%RAW_DIR)):
                aid = line['id']
                start = line['accept_time']
                end = line['submit_time']
                out.write('%s\t%s\t%s\n'%(aid,start,end,))
        out.close()

def get_total_time(data):
	for lang in sorted(data.iteritems(), key=operator.itemgetter(0)):
		print '%s\t%s'%(lang[0], str(lang[1][1] - lang[1][0]))

def format_for_graph(data):
	print "Formatting data"
	ret = list()
	mindate = None
	for l in data.keys(): 
		lang = data[l]	
		begin = lang[0]
		if(mindate == None or begin < mindate):
			mindate = begin
	for l in data.keys():
		lang = data[l]	
		complete = lang[1] - lang[0]
		start = lang[0] - mindate
		ret.append((l,complete, start, start+complete))
	return sorted(ret, key=operator.itemgetter(3)) 

def time_bar(data):
	num = len(data)
        ind = np.arange(num) 
        width = 0.8       
        lbls = [t[0] for t in data][:num]
	time_to_start = [t[2].days for t in data][:num]
	time_to_complete = [t[1].days for t in data][:num]
        plt.bar(ind, time_to_start, width, color='r') 
        plt.bar(ind, time_to_complete, width, bottom=time_to_start)
        plt.yticks(fontsize='16')
        plt.xticks(ind+width/2, tuple(lbls) ,rotation='vertical', fontsize='16')
	plt.title('Time to complete all HITs')
        plt.show()

def format_for_time_series(data):
	print "More formatting data"
	hitmap = dictionaries.hit_map()
	langids, langcodes = dat.lang_map()
        hitlangs = dat.hits_language()
	all_times = dict()
	for aid, complete, start, total in data:	
		lang = langids[hitlangs[hitmap[aid]]]
		if lang not in all_times:
			all_times[lang] = list()
		all_times[lang].append(total)
	try:
		all_times.pop('en')
	except KeyError:
		pass
	return all_times

def time_series(data, num=40):
	SEC_PER_DAY = 86400
	x = list()
	y = list()
	names = list()
	sort_order = [t[0] for t in sorted(data.iteritems(), key=lambda t : max(t[1]))]
	for i,lang in enumerate(sort_order[:num]):
		names.append(lang)
		x += [t.total_seconds() for t in data[lang]]
		y += [5+(i*5)]*len(data[lang])
	plt.scatter(x,y,marker='|')
	plt.xlim([0,max(x)+5])
	plt.ylim([0,max(y)+5])
        plt.yticks(sorted(list(set(y))), tuple(names))
	xmax = int(math.ceil(max(x)))
	max_days = int(math.ceil(max(x)/SEC_PER_DAY))
        plt.xticks(range(0,xmax,5*SEC_PER_DAY), range(0,max_days,5))
        plt.xlabel('Time in days')
	plt.show()

def fancy_time_series(data, num=40):
	SEC_PER_DAY = 86400
	x = list()
	y = list()
	names = list()
	sort_order = [t[0] for t in sorted(data.iteritems(), key=lambda t : max(t[1]))]
	print sort_order
	for i,lang in enumerate(sort_order[:num]):
		names.append(lang)
		x += [t.total_seconds() for t in data[lang]]
		y += [5+(i*5)]*len(data[lang])
	tot = len(y)
	for i, (xx, yy) in enumerate(zip(x,y)):
		if i % 1000 == 0: print (float(i)/tot) , xx, yy
		plt.plot([xx, xx], [yy, yy+1], color = 'b')
#	plt.scatter(x,y,marker='|')
	plt.xlim([0,max(x)+5])
	plt.ylim([0,max(y)+5])
        plt.yticks(sorted(list(set(y))), tuple(names))
	xmax = int(math.ceil(max(x)))
	max_days = int(math.ceil(max(x)/SEC_PER_DAY))
        plt.xticks(range(0,xmax,5*SEC_PER_DAY), range(0,max_days,5))
        plt.xlabel('Time in days')
	plt.savefig('completetime.pdf')
	#plt.show()

if __name__ == '__main__':
	if(len(sys.argv) < 2 or sys.argv[1] == 'help'):
                print '---USAGE---'
                print './completetime.py extract: extract start and complete times by assignment and write to OUTPUT_DIR/byassign.times'
                print './completetime.py bar: boring bar graph'
                print './completetime.py series: way more cool series graph'
                exit(0)

        do = sys.argv[1]
        if(do == 'extract'):
		write_all_times()
        if(do == 'bar'):
		time_bar(format_for_graph(get_language_dicts('%s/byassign.voc.accepted'%OUTPUT_DIR)))
        if(do == 'series'):
		#time_series(format_for_time_series(format_for_graph(time_map())))
		fancy_time_series(format_for_time_series(format_for_graph(time_map())), num=40)


