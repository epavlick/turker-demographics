import re
import csv
import itertools
import operator
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import string

COUNTRIES = 'ref/countrycodemap'
RAW_DIR = '/home/steven/Documents/Ellie/Research/demographics/data/dictionary-data-dump-2012-11-13_15:11'
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
        dict_file='%s/clpair.turkerlist'%DICT_DIR
        nondict_file='%s/nonclpair.turkerlist'%DICT_DIR
	data = dict()
	for line in open(dict_file).readlines():
		comps = line.split()
		lang = comps[0]
		breakdown = [(c.split(':')[0], int(c.split(':')[1])) for c in comps[1:]]
		data[lang] = breakdown
	nondata = dict()
	for line in open(nondict_file).readlines():
		comps = line.split()
		lang = comps[0]
		breakdown = [(c.split(':')[0], int(c.split(':')[1])) for c in comps[1:]]
		nondata[lang] = breakdown
	return ({k: data[k] for k in data if not k == 'total'},{k: nondata[k] for k in nondata if not k == 'total'})

def dictionary_stats_turker():
        dict_files=['%s/nonclpair.numturkers'%DICT_DIR, '%s/clpair.numturkers'%DICT_DIR]
        data = dict()
        for line in open(dict_files[0]).readlines():
                lang, count = line.split()
                data[lang] = (float(count), 0)
        for line in open(dict_files[1]).readlines():
                lang, count = line.split()
		if lang in data:
                	data[lang] = (data[lang][0], float(count))
	ret = list()
	for d in data:
		ret.append((d, data[d][0], data[d][1], data[d][0] + data[d][1]))
        return ret 

def dictionary_stats_turkerqual():
        dict_files=['%s/nonclpair.turkerqual'%DICT_DIR, '%s/clpair.turkerqual'%DICT_DIR]
        data = dict()
        for line in open(dict_files[0]).readlines():
                lang, count = line.split()
                data[lang] = (float(count), 0)
        for line in open(dict_files[1]).readlines():
                lang, count = line.split()
		if lang in data:
	                data[lang] = (data[lang][0], float(count))
        return data

def quality_scatter(title='Title'):
 	tquals = dictionary_stats_turkerqual()
        tdata = sorted(dictionary_stats_turker(), key=operator.itemgetter(3), reverse=True)
        names = list()
	xin = list(); yin = list();
	xout = list(); yout = list();
	cin = list(); cout = list();
  	for d in tdata:
		lang = d[0]
		names.append(lang)
                nomatch, match= tquals[lang]
                numout = int(d[1]); numin = int(d[2]);
		cin.append(numin);xin.append(numin);yin.append(match);
		cout.append(numout);xout.append(numout);yout.append(nomatch);
	points_to_label = ['RO', 'NG', 'AM', 'DZ','RU', 'UK', 'PK', 'IN','US','MY','MK','ES', 'ID', '100 turkers']
#       cmap = reverse_cntry_map('ref/countrynames')
#       cmap['100 turkers'] = '100 turkers'
#	names.append('100 turkers')
#	y.append(0.9)
#	x.append(50000)
#	turker_counts['100 turkers'] = 100
	labels = list();labelx = list();labely = list();
#	for nm in points_to_label:
#		idx = names.index(nm)
#		labels.append(cmap[nm])
#		labelx.append(x[idx])
#		labely.append(y[idx])
	plt.scatter(xin, yin, color='b', s=cin)
	plt.scatter(xout, yout, color='r', s=cout)
	plt.ylim([0,1])
	plt.xlim([0,350])
	plt.xlabel('Number of turkers', fontsize='14')
	plt.ylabel('Average quality', fontsize='14')
	plt.xticks(fontsize='16')
        plt.yticks(fontsize='16')
#        arrows = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0')
#        for label, x, y in zip(labels, labelx, labely):
#                plt.annotate(label,xy =(x,y),xytext=(20,10),textcoords='offset points',ha ='left',va='bottom',arrowprops=arrows, fontsize=14)
        plt.show()



if __name__ == '__main__':
	quality_scatter()
	#summary_table_condensed()

