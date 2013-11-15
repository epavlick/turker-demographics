#\begin{tabular}{lrlrlr}\hline\hline
#%Language&\# Turkers\\
#\hline
#English&592&	French&63&	Vietnamese&34\\
#Tamil&253&	Polish&61&	Macedonian&31\\
#Malayalam&219&	Urdu&56&	Cebuano&29\\
#Hindi&149&	Tagalog&54&	Swedish&26\\
#Spanish&131&	Marathi&48&	Bulgarian&25\\
#Telugu&87&	Russian&44&	Hungarian&23\\
#Chinese&86&	Italian&43&	Swahili&23\\
#Romanian&85&	Bengali&41&	Thai&22\\
#Portuguese&82&	Gujarati&39&	Catalan&22\\
#Arabic&74&	Hebrew&38&	Lithuanian&21\\
#Kannada&72&	Dutch&37&	Punjabi&21\\
#German&66&	Turkish&35&	Others &$\leq$20\\
#\hline\hline
#\end{tabular}

import csv
import operator
import itertools

def batch(iterable, n = 3):
   l = len(iterable)
   for ndx in range(0, l, n):
       yield iterable[ndx:min(ndx+n, l)]

def capitalize(s) : return s.capitalize()

def print_table(lang_counts) : 
	for l1,l2,l3 in batch(sorted(lang_counts.iteritems(), key=operator.itemgetter(1), reverse=True),n=3) :
		print '%s & %d & %s & %d & %s & %d \\\\'%(capitalize(l1[0]),l1[1],capitalize(l2[0]),l2[1],capitalize(l3[0]),l3[1])
	
		
pass1_turkers = set()

for line in open('data/pass-1').readlines() :
	_, _, _, _, _, workers = line.strip().split('\t',5)
	for wt in workers.split('\t'):
		w,t = wt.split(':',1)
		pass1_turkers.add(w)

lmap = {l.strip().split()[1] : l.strip().split()[0] for l in open('ref/lang2name.txt').readlines()}

lang_counts = {}
tot = 0

for line in csv.DictReader(open('data/turkers.tsv'), delimiter='\t') :
	langs = [c for c in line['langs'].split(':') if not c.strip() == '']
	if len(langs) > 1 : print langs; continue;
	for lang in langs : 
		try : lang = lmap[lang]
		except : continue
		if lang not in lang_counts : lang_counts[lang] = 0
		if line['id'] in pass1_turkers : lang_counts[lang] += 1; tot += 1;

#print tot
#for l in sorted(lang_counts.keys()) : 
#	print "%s,%d"%(l,lang_counts[l])
print_table(lang_counts)
