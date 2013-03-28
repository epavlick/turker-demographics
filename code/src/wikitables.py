import re
import csv
import figures 

LANG_PATH = '/home/steven/Documents/Ellie/Research/demographics/data/dictionary-data-dump-2012-11-13_15:11/languages'

if __name__ == '__main__':
	lmap = figures.reverse_lang_map(LANG_PATH)
#	all_classes = { '>500k':[], '100k-500k':[], '50k-100k':[], '10k-50k':[], '<10k':[]}
	all_classes = { '>500k':[], '100k-500k':[], '10k-100k':[], '<10k':[]}
	our_langs = set([l.strip() for l in open('alllangs').readlines()])
	for line in csv.DictReader(open('wikicounts'), delimiter='\t'):
		lang = line['Wiki']
		num = int(re.sub(',','',line['Articles']))
		if lang in our_langs:
			if num > 500000:		
				all_classes['>500k'].append(lang)
			elif num > 100000:		
				all_classes['100k-500k'].append(lang)
#			elif num > 50000:		
#				all_classes['50k-100k'].append(lang)
			elif num > 10000:		
				print '%s_%d'%(lang,num)
				all_classes['10k-100k'].append(lang)
			else:		
				all_classes['<10k'].append(lang)
	for c in all_classes:
		print c
		for l in sorted(all_classes[c]):
			print '%s (%s)'%(lmap[l], l)
		print
