import sys
import gzip

DICT_PATH = '/home/steven/Documents/Ellie/Research/demographics/repo/dictionaries/'

def get_external_dictionary(lang):
	d = dict()
	for line in gzip.open('%s/external_dictionaries/%s/%s-en.gz'%(DICT_PATH,lang,lang,)).readlines():
		l = line.strip().split()	
		if len(l) > 1:
			d[l[0].decode('utf-8').lower()] = l[1].decode('utf-8').lower()
	return d

def get_control_dictionary(lang):
	d = list()
	for line in open('%s/ellie/controls/wiki/dictionary.%s'%(DICT_PATH,lang,)).readlines():
		l = line.strip().split()	
		d.append((l[0].lower(),l[1].lower()))
	return d

def get_synonym_dictionary(lang, non=False):
	d = list()
	try:
		if non: p = '%s/ellie/controls/turker/neg/dictionary.%s'%(DICT_PATH,lang,)
		else: p = '%s/ellie/controls/turker/pos/dictionary.%s'%(DICT_PATH,lang,)
		for line in open(p).readlines():
			l = line.strip().split()	
			if len(l) > 1:
				for t in l[1].split(','):	
					d.append((l[0].lower(),t.lower()))
		return d
	except IOError:
		return None	

def get_dictionary(path):
	d = list()
	try:
		for line in open(path).readlines():
			l = line.strip().split()	
			if len(l) > 1:
				for t in l[1].split(','):	
					d.append((l[0].lower(),t.lower()))
		return d
	except IOError:
		return None	

def validate(query, ref):
	match = 0.0; total = 0.0; not_found = 0.0; 
	for (word, trans) in query:
		if word in ref:
			if trans == ref[word]:
				match += 1
			total += 1
		else:
			not_found += 1
	if total == 0: ret = (0, total, not_found)
	else: ret = (match/total, total, not_found)
	return ret

if __name__ == '__main__':

	langs = ['az','bg','bn','bs','cy','es','fa','hi','id','lv','ms','ne','pl','ro','ru','sk','so','sq','sr','ta','tr','uk','ur']
	
	if(sys.argv[1] == 'controls'):
		out = open('dict_validation.%s.out'%sys.argv[2], 'w')
		for lang in langs:
			print lang
			if sys.argv[2] == 'c' : c = get_control_dictionary(lang) 
			elif sys.argv[2] == 's' : c = get_synonym_dictionary(lang) 
			elif sys.argv[2] == 'ns' : c = get_synonym_dictionary(lang, non=True) 
			elif sys.argv[2] == 'sc' : 
				c = get_synonym_dictionary(lang)
				cc = get_control_dictionary(lang)
				if c is not None and cc is not None: c += cc
			elif sys.argv[2] == 'ncl': 
				p = '%s/ellie/nonclpair/dictionary.%s'%(DICT_PATH,lang,)
				c = get_dictionary(p)
			elif sys.argv[2] == 'cl': 
				p = '%s/ellie/clpair/dictionary.%s'%(DICT_PATH,lang,)
				c = get_dictionary(p)
			if c is None:
				continue
			d = get_external_dictionary(lang)
			v = validate(c,d)
			out.write('%s\t%.03f\t%d\t%d\n'%(lang,v[0],v[1],v[2])) 
		out.close()

	if(sys.argv[1] == 'quals'):
		for cut in [0.00,0.10,0.20,0.30,0.40,0.50,0.60,0.70,0.80,0.90]:
			bigout = open('dict_validation.%.02f.big.out'%cut, 'w')
			smallout = open('dict_validation.%.02f.small.out'%cut, 'w')
			for lang in langs:
				print lang
				c = get_dictionary('dictionaries/qual-cutoff/%.02f/dictionary.%s'%(cut,lang,))
				if c is None:
					continue
				d = get_external_dictionary(lang)
				v = validate(c,d)
				bigout.write('%s\t%.03f\t%d\t%d\n'%(lang,v[0],v[1],v[2])) 
				smallout.write('%s\t%.03f\n'%(lang,v[0],)) 
			bigout.close()
			smallout.close()
