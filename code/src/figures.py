import re
import csv
import sys
import math
import numpy
import scipy
import string
import operator
import itertools
import dictionaries
from scipy import stats
from scipy.stats import norm
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

RAW_DIR = '../data/dictionary-data-dump-2012-11-13_15:11'
OUTPUT_DIR = 'output'

def select_by(data, col, value):
        dicts = dict()
        for d in data:
                if(data[d][col] == value):
                        dicts[d] = data[d]
        return dicts

def all_keys(path, attr):
        ret = set()
        data = csv.DictReader(open(path),delimiter='\t')
        for d in data:
                ll = d[attr].split(';')
                for l in ll:
                        ret.add(l)
        if('' in ret):
                ret.remove('')
        return list(ret)


def read_data(path):
        ret = dict()
        data = csv.DictReader(open(path),delimiter='\t')
        for d in data:
                ret[d['id']] = d
        return ret

def read_table_file(path):
        ret = dict()
        data = csv.DictReader(open(path),delimiter='\t')
        for d in data:
                ret[d['id']] = {'lang':d['lang'],'country':d['country'], 'hitlang': d['hitlang'], 'survey':d['survey']}
        return ret

def count_dicts(data, attr, mapname=False):
        langs = dict()
        for turker in data:
                ll = data[turker][attr].split(';')
                for l in ll:
                        if(re.match('\d+',l) or l == 'N/A'):
                                continue
                        if(l == '' or l == '-'):
                                continue
                        if l not in langs:
                                langs[l] = 0
                        langs[l] += 1
        return [(l,langs[l]) for l in langs]

def get_dicts(data):
        dicts = dict()
        for d in data:
                langs = data[d]['langs'].strip(';')
                ctry = data[d]['country'].strip(';')
                srvy = data[d]['survey'].strip(';').encode('ascii', 'ignore')
                dicts[d] = {'lang': langs, 'country': ctry, 'survey':srvy}
        return dicts

def reverse_lang_map(path):
        lang_data = {}
        for line in csv.DictReader(open(path)):
                lang = line['name']
                prefix = line['prefix']
                if(prefix not in lang_data):
                        lang_data[prefix] = re.sub('_',' ',lang)
        return lang_data

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

def conf_int_by_attr(attr):
	ret = dict()
	data = read_table_file('%s/byassign.voc.accepted'%OUTPUT_DIR)
	scores = all_avg_scores('%s/byassign.voc.quality.related'%OUTPUT_DIR)
	langs = all_keys('%s/byassign.voc.accepted'%OUTPUT_DIR, attr)
	avg = list()
	for l in langs:
		alist = select_by(data, attr, l).keys()
		avg += alist
		ci = avg_score(alist, scores)
		ret[l] = ci
	ci = avg_score(avg, scores)
	ret['avg'] = ci
	return ret

def hitlang_qual(cut=3000):
	assigns_by_lang = dict()
	qual_by_assign = dict()
	qual_by_lang = dict()
	avg_qual = list()
	for line in csv.DictReader(open('%s/byassign.voc.accepted'%OUTPUT_DIR), delimiter='\t'):
		lang = line['hitlang']
		if lang not in assigns_by_lang:
			assigns_by_lang[lang] = list()
		assigns_by_lang[lang].append(line['id'])
	for line in csv.DictReader(open('%s/byassign.voc.quality.related'%OUTPUT_DIR), delimiter='\t'):
		aid = line['id']
		q = line['avg']
		qual_by_assign[aid] = q
	for l in assigns_by_lang.keys():
		qual = list()
		for a in assigns_by_lang[l]:
			q = qual_by_assign[a]
			if not(q == 'N/A'):
				qual.append(float(q))
				avg_qual.append(float(q))
        		n, (smin, smax), sm, sv, ss, sk = stats.describe(qual)
        		moe = math.sqrt(sv)/math.sqrt(n) * 2.576
		qual_by_lang[l] = (sm, (sm - moe, sm + moe), n, moe)
        n, (smin, smax), sm, sv, ss, sk = stats.describe(avg_qual)
        moe = math.sqrt(sv)/math.sqrt(n) * 2.576
	qual_by_lang['avg'] = (sm, (sm - moe, sm + moe), n, moe)
	conf_int_graphs(sorted([(k,qual_by_lang[k]) for k in qual_by_lang], key=operator.itemgetter(1), reverse=True), cutoff=cut)

def two_way_split(attr1, attr2):
	ret = dict()
	data = read_table_file('%s/byassign.voc.accepted'%OUTPUT_DIR)
	scores = all_avg_scores('%s/byassign.voc.quality.related'%OUTPUT_DIR)
	first = all_keys('%s/byassign.voc.accepted'%OUTPUT_DIR, attr1)
	second = all_keys('%s/byassign.voc.accepted'%OUTPUT_DIR, attr2)
	for k in first:
		miniret = dict()
		alist = select_by(data, attr1, k)
		for kk in second:
			blist = select_by(alist, attr2, kk)
			miniret[kk] = blist 
		ret[k] = miniret
	return ret, scores

def clean_ints(data, cutoff=50, sorting=None):
	ret = list()
	for c in data:
		if(not(data[c] == None)):
			if(data[c][2] > cutoff):
					ret.append((c, data[c], data[c][2]))
	ret = sorted(ret, reverse=True) 
	return [(c[0], c[1]) for c in ret]

def conf_int_graphs(all_ci_dict, title='Graph', graph_avg=True, cutoff=3000):	
	ci_dict = [c for c in all_ci_dict if c[1][2] >= cutoff]
	yax = [c[1][0] for c in ci_dict]
	err = [c[1][3] for c in ci_dict]
        xax = range(len(ci_dict))
        names = [c[0] for c in ci_dict]
        plt.bar(xax, yax, 1, yerr=err, ecolor='black')
	if(graph_avg):
		bidx = names.index('avg')
		plt.bar(xax[bidx], yax[bidx], 1, color='r') 
        plt.xticks([x + 0.5 for x in xax], [n for n in names], rotation='vertical')
        plt.ylabel('')
	plt.ylim([0,max(yax)+.1])
	plt.xlim([0,len(ci_dict)])
        plt.title(title)
        plt.show()

def hit_map():
        lang_data = {}
        for line in csv.DictReader(open(ASSIGN_RAW)):
                assign = line['id']
                hit = line['hit_id']
                if(assign not in lang_data):
                        lang_data[assign] = hit
        return lang_data

def two_way_quality(attr1, attr2):
	breakdown = dict()
	tw, scores = two_way_split(attr1, attr2)
	for t in tw:
		breakdown[t] = dict()
		for tt in tw[t]:
			if(not(tt == 'None')):
				s = avg_score(tw[t][tt].keys(), scores)
				if(not(s==None)):
					breakdown[t][tt] = s
	return breakdown

def sort_data(data):
	tups = list()
	for lang in data:
		if('yes' in data[lang] and 'no' in data[lang]):
			ysz = data[lang]['yes'][2]
			nsz = data[lang]['no'][2]
			tups.append((ysz+nsz, lang, data[lang]))
	return [(t[1],t[2]) for t in sorted(tups, reverse=True)]

def compare_native_speakers():
	langs = all_keys('%s/byassign.voc.accepted'%OUTPUT_DIR, 'hitlang')
	quals = two_way_quality('hitlang','lang')
	graph_data = dict()	
	graph_data_clean = dict()	
	for l in langs:
		graph_data[l] = clean_ints(quals[l])
	for k in graph_data:
		new = dict()
		for i in graph_data[k]:
			if i[0] == k:
				new['yes'] = i[1]
			elif i[0] == 'en':
				new['no'] = i[1]
		graph_data_clean[k] = new
	return sort_data(graph_data_clean)

def compare_native_speakers_graph(ci_tups, title='Graph'):
	plots = list()
        names = [c[0] for c in ci_tups]
	yax_yes = [c[1]['yes'][0] for c in ci_tups] 
	yax_no = [c[1]['no'][0] for c in ci_tups]
	err_yes = [c[1]['yes'][3] for c in ci_tups]
	err_no = [c[1]['no'][3] for c in ci_tups]
        xax = range(len(names))
        plots.append(plt.bar(xax, yax_yes, .4, color='b', yerr=err_yes, ecolor='black'))
        plots.append(plt.bar([x + 0.4 for x in xax], yax_no, .4, color='r', yerr=err_no, ecolor='black'))
        plt.xticks([x + 0.4 for x in xax], [n for n in names], rotation='vertical')
        plt.ylabel('Average assignment quality')
	plt.ylim([0,1])
	plt.xlim([0,len(names)])
	plt.legend(plots, ('native', 'non-native'))
        plt.show()

def native_compare():
	data = compare_native_speakers()
	ttl='Translation quality for native vs. non-native speakers'
	compare_native_speakers_graph(data, title=ttl)

def count_turkers(attr):
	counts = count_dicts(get_dicts(read_data('%s/byturker.voc.onelang'%OUTPUT_DIR)),attr)
	mcounts = count_dicts(get_dicts(read_data('%s/byturker.voc.multlang'%OUTPUT_DIR)),attr)
	onelang = {c[0] : c[1] for c in counts}
	multlang = {c[0] : c[1] for c in mcounts}
	alllang = dict()
	for c in multlang:
		combined = multlang[c]
		if c in onelang:
			combined += onelang[c]
		alllang[c] = combined
	for c in onelang:
		if c not in multlang:
			alllang[c] = onelang[c]
	return alllang

def reverse_cntry_map(path):
        lang_data = {}
        for line in open(path).readlines():
		l = line.split()
                country = l[0].strip()
                code = l[1].strip()
                if(code not in lang_data):
                        lang_data[code] = country
        return lang_data

def quality_scatter(attr, title='Title', points_to_label=None):
	points_to_label = ['VN', 'RO', 'NG', 'AM', 'DZ','RU', 'UK', 'ET', 'PK', 'IN','US','MY','MK','ES', 'ID', '100 turkers']
	attr = 'country'
	cmap = reverse_cntry_map('data-files/cleancountrycodemap')
	cmap['100 turkers'] = '100 turkers'
	ci = conf_int_by_attr(attr)
	turker_counts = count_turkers(attr)
	names = list()
	x = list()
	y = list()
	e = list()
	for c in ci:
		if(c in turker_counts and not(ci[c] == None) and (len(ci[c]) > 3)):
			names.append(c)
			y.append(ci[c][0])
			e.append(ci[c][3])
			x.append(ci[c][2])
	names.append('100 turkers')
	y.append(0.9)
	x.append(50000)
	turker_counts['100 turkers'] = 100
        labels = list()
	labelx = list()
	labely = list()
	for nm in points_to_label:
		idx = names.index(nm)
                labels.append(cmap[nm])
                labelx.append(x[idx])
                labely.append(y[idx])
	area = [turker_counts[n] for i,n in enumerate(names)]
	plt.scatter(x, y, s=area)
	plt.xscale('log')
	plt.xlim([.1,1000000])
	plt.ylim([0,1])
	plt.xlabel('Number of assignments', fontsize='16')
	plt.ylabel('Average quality', fontsize='16')
	plt.xticks(fontsize='16')
	plt.yticks(fontsize='16')
	arrows = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0')
	for label, x, y in zip(labels, labelx, labely):
        	plt.annotate(label,xy =(x,y),xytext=(20,-20),textcoords='offset points',ha ='left',va='bottom',arrowprops=arrows, fontsize=16)
	plt.show()

def assign_and_turker_plot(tuples):
        points_to_label=['ur','mk','te','ml','ro','es','pl','tl','mr','pt','hi','nl','new','ar','ru','jv','kn','ta','fr','sr']
        langmap = reverse_lang_map('%s/languages'%RAW_DIR)
        datax = [t[1][0] for t in tuples]
        datay = [t[1][1] for t in tuples]
        labels = list()
        labelx = list()
        labely = list()
        for t in tuples:
                if t[0] in points_to_label:
                        labels.append(t[0])
                        labelx.append(t[1][0])
                        labely.append(t[1][1])
        plt.subplots_adjust(bottom = 0.1)
        plt.scatter(datax, datay, marker = 'o')
        plt.ylabel('Number of turkers')
        plt.ylim([0,350])
        plt.xlabel('Number of assignments')
        plt.xlim([0,4000])
        plt.rc('xtick', labelsize=40)
        plt.rc('ytick', labelsize=40)
	arrows = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0')
        for label, x, y in zip(labels, labelx, labely):
                plt.annotate(label,xy=(x,y),xytext=(-10,10),textcoords='offset points',ha='right',va='bottom',arrowprops=arrows,fontsize=20)
        plt.show()

def one_lang_assigns():
        onelang_turkers = [l['id'] for l in csv.DictReader(open('%s/byturker.voc.onelang'%OUTPUT_DIR), delimiter='\t')]
        tmap = dictionaries.turker_map()
        assigns = dict()
        for line in csv.DictReader(open('%s/byassign.voc.accepted'%OUTPUT_DIR), delimiter='\t'):
                if tmap[line['id']] in onelang_turkers:
                        l = line['hitlang']
                        if l not in assigns:
                                assigns[l] = 0
                        assigns[l] += 1
        return assigns


def assign_and_turker_table(onelang=True):
        hitlangs = dict()
        if(onelang):
                assigns = one_lang_assigns()
                turkers = get_turker_dict()
        else:
                assigns = get_assign_dict()
                turkers = get_turker_dict(onelang=False)
        for c in assigns:
                hitlangs[c] = [assigns[c],0]
        turkers = get_turker_dict()
        for c in turkers:
                if c not in hitlangs:
                        continue
                hitlangs[c][1] = turkers[c]
        return sorted(hitlangs.iteritems(), key=operator.itemgetter(1), reverse=True)

def get_assign_dict():
        assigns = dict()
        for line in csv.DictReader(open('%s/byassign.voc.accepted'%OUTPUT_DIR), delimiter='\t'):
                l = line['hitlang']
                if l not in assigns:
                        assigns[l] = 0
                assigns[l] += 1
        return assigns

def get_turker_dict(onelang=True):
        turkers = dict()
        if(onelang):
                nmlist = ['onelang']
        else:
                nmlist = ['nolang', 'onelang', 'multlang']
        for num in nmlist:
                for line in csv.DictReader(open('%s/byturker.voc.%s'%(OUTPUT_DIR,num,)), delimiter='\t'):
                        l = line['hitlang']
                        for ll in l.split(';'):
                                ll = ll.strip()
                                if ll == '' or ll == 'N/A':
                                        continue
                                if ll not in turkers:
                                        turkers[ll] = 0
                                turkers[ll] += 1
        return turkers

def natlang_pie(tuples):
        langs = reverse_lang_map('%s/languages'%RAW_DIR)
        langs['other'] = 'Other'
        tuples.reverse()
        plt.ax = plt.axes([0.1, 0.1, 0.8, 0.8])
        labels = [t[0] for t in tuples]
        fracs = [t[1] for t in tuples]
        explode=tuple([0.05]*len(fracs))
        colors=('b', 'g', 'r', 'c', 'm', 'y', 'w', '#FF6600')
        patches, texts, autotexts = plt.pie(fracs, labels=labels, explode=explode, colors=colors, autopct='%1.1f', shadow=False, pctdistance=0.9, labeldistance=1.1)
        proptease = fm.FontProperties()
        proptease.set_size('medium')
        plt.setp(autotexts, fontproperties=proptease)
        plt.setp(texts, fontproperties=proptease)
        plt.show()

def natlang_table():
        natlangs = dict()
        for line in csv.DictReader(open('%s/byturker.voc.onelang'%OUTPUT_DIR), delimiter='\t'):
                for lang in line['langs'].split(';'):
                        lang = lang.strip()
                        if lang == '':
                                continue
                        if lang not in natlangs:
                                natlangs[lang] = 0
                        natlangs[lang] += 1
        return sorted(natlangs.iteritems(), key=operator.itemgetter(1), reverse=True)

def clean_tuples(tuples):
        clean = list()
        other = 0
        for lang, count in tuples:
                if count > 20:
                        clean.append((lang,count))
                else:
                        other += count
        clean.append(('other', other))
        return clean

def pie_chart_table(tups):
        tot = 0
        langmap = reverse_lang_map('%s/languages'%RAW_DIR)
        langmap['other'] = 'Other'
        print '\\begin{figure}[h]'
        print '\\begin{tabular}{cc}\hline\hline'
        print 'Language&\\# Turkers\\\\'
        print '\\hline'
        for lang, count in tups:
                tot += count
                print '%s&%d\\\\'%(langmap[lang],count,)
        print '\\hline\\\hline'
        print '\\end{tabular}'
        print '\\end{figure}'

def print_data_for_map():
        COUNTRIES = 'ref/countrycodemap'
        countries = dict()
        for line in open(COUNTRIES).readlines():
                name, code = line.split()
                countries[code] = string.capitalize(name)
        full = dict()
        o = count_dicts(get_dicts(read_data('%s/byturker.voc.onelang'%OUTPUT_DIR)),'country')
        n = count_dicts(get_dicts(read_data('%s/byturker.voc.nolang'%OUTPUT_DIR)),'country')
        m = count_dicts(get_dicts(read_data('%s/byturker.voc.multlang'%OUTPUT_DIR)),'country')
        for lang, c in o:
                if not lang in full:
                        full[lang] = 0
                full[lang] += c
        for lang, c in n:
                if not lang in full:
                        full[lang] = 0
                full[lang] += c
        for lang, c in m:
                if not lang in full:
                        full[lang] = 0
                full[lang] += c
        for ctry, count in full.iteritems():
                print "['%s',%d],"%(countries[ctry],count,)

if __name__ == '__main__':
	if(len(sys.argv) < 2 or sys.argv[1] == 'help'):
                print '---USAGE---'
                print './figures.py assign_turk_scatter : scatter of # turkers vs. # assignments, points labeled by country'
		print './figures.py hitlang_qual : bar chart of quality by HIT language'
                print './figures.py quality_scatter : scatter of # turkers vs. quality, bubbles sized by # turkers'
                print './figures.py native_compare : side-by-side bar of native vs. non-native speaker quality'
                print './figures.py natlang_pie : pie chart'
                print './figures.py natlang_table : pie chart as table'
                print './figures.py map: print data for googlecharts map'
                exit(0)

	plot = sys.argv[1]
	if(plot == 'hitlang_qual'):
		hitlang_qual()
	if(plot == 'quality_scatter'):
		quality_scatter()
	if(plot == 'native_compare'):
		native_compare()
        if(plot == 'assign_turk_scatter'):
                assign_and_turker_plot(assign_and_turker_table())
        if(plot == 'natlang_pie'):
        	natlang_pie(clean_tuples(natlang_table()))
        if(plot == 'natlang_table'): 
		pie_chart_table(clean_tuples(natlang_table()))
        if(plot == 'map'): 
	        print_data_for_map()





