import re
import sys
import csv
import json
import string
import codecs

RAW_DIR = '../data/dictionary-data-dump-2012-11-13_15:11/'
OUTPUT_DIR = 'output'

def hits_language():
	hit_path = '%s/hits'%RAW_DIR
	language_path = '%s/languages'%RAW_DIR
        lang_data = {}
        for line in csv.DictReader(open(language_path)):
                lang = line['id']
                if(lang not in lang_data):
                        lang_data[lang] = lang
        hit_data = {}
        for line in csv.DictReader(open(hit_path)):
                hit = line['id']
                if(hit not in hit_data):
                        l =  line['language_id']
                        hit_data[hit] = lang_data[line['language_id']]
        return hit_data

def lang_map():
        lang_data = {}
        num_data = {}
        for line in csv.DictReader(open('%s/languages'%RAW_DIR)):
                lang = line['name'].lower()
                id = line['id']
                if(lang not in lang_data):
                        lang_data[lang] = line['prefix']
                if(id not in num_data):
                        num_data[id] = line['prefix']
        return num_data, lang_data

def country_map():
	ret = dict()
	for l in open('data-files/countrymap').readlines():
		ll = l.split('\t')
		ret[ll[0]] = ll[1].strip()
	return ret

def code_map():
	ret = dict()
	for l in open('data-files/countrycodemap').readlines():
		ll = l.split('\t')
		ret[ll[0]] = ll[1].strip()
	return ret

def map_country(c, countrymap, codemap):
	c = clean(c)
	if c in countrymap:
		c = countrymap[c]
	if c in codemap:
		return codemap[c]
	return 'N/A'

def list2str(lst):
	s = ''
	if len(lst) == 0:
		s = 'N/A;'
	for l in lst:
		s+=l+';'
	return s

def assign_workers(path, langs, idlist=None):
	countrymap = country_map()
        codemap = code_map()
        numlangmap, langmap = lang_map()
        data = {}
        for line in csv.DictReader(open(path)):
                worker = line['worker_id']
                assign = line['id']
		if( (not(idlist==None)) and (assign not in idlist) ):
			continue
                data[assign] = dict.fromkeys(['worker'])
		data[assign]['worker'] = worker
	return data
		
def assign_langs(path, langs, idlist=None):
	countrymap = country_map()
        codemap = code_map()
        numlangmap, langmap = lang_map()
        survey_data = {}
        for line in csv.DictReader(open(path)):
                worker = line['worker_id']
                assign = line['id']
		if( (not(idlist==None)) and (assign not in idlist) ):
			continue
                hit = line['hit_id']
                data = json.loads(line['result'])
                survey_keys = ['country','survey','lang', 'hitlang', 'yrseng', 'yrssrc']
                survey_data[assign] = dict.fromkeys(survey_keys)
		#COUNTRY DATA
		if('country' in data):
	       		survey_data[assign]['country'] = map_country(data['country'],countrymap,codemap)
		else:
	       		survey_data[assign]['country'] = 'N/A'
		if('survey_what_country' in data):
	       	     	survey_data[assign]['survey'] = map_country(data['survey_what_country'],countrymap,codemap)
		else:
	       		survey_data[assign]['survey'] = 'N/A'
		#LANGUAGE DATA
      		survey_data[assign]['hitlang'] = numlangmap[langs[hit]] 
		if('survey_is_native_english_speaker' in data): 
			if(data['survey_is_native_english_speaker']=='yes'): 
				survey_data[assign]['lang'] = langmap['english']
			else:
				survey_data[assign]['lang'] = 'N/A'
		if('survey_is_native_foreign_speaker' in data): 
			if(data['survey_is_native_foreign_speaker']=='yes'): 
				survey_data[assign]['lang'] = numlangmap[langs[hit]] 

		## ** assignments that don't trigger one of the above ifs end up as N/A in the final output. there are 1801 of these. ** #
		## ** i checked a few, and they are mostly because the question 'is xx your native language' doesn't appear in the ** #
		## ** data, not because they answer no to both questions. ** #

		if(survey_data[assign]['lang'] == None):
			survey_data[assign]['lang'] = 'N/A'
		if('survey_years_speaking_english' in data): 
			if(data['survey_years_speaking_english'].isdigit()):	
				survey_data[assign]['yrseng'] = int(data['survey_years_speaking_english'])	
			else:
				survey_data[assign]['yrseng'] = 'N/A'
		else:
	       		survey_data[assign]['yrseng'] = 'N/A'
		if('survey_years_speaking_foreign' in data): 
			if(data['survey_years_speaking_foreign'].isdigit()):	
				survey_data[assign]['yrssrc'] = int(data['survey_years_speaking_foreign'])	
			else:
				survey_data[assign]['yrssrc'] = 'N/A'
		else:
	       		survey_data[assign]['yrssrc'] = 'N/A'
        return survey_data

def write_data(data, name, headers):
        f = codecs.open(name,'w','utf-8')
        s = 'id\t'
        for t in headers:
                s += '%s\t'%t
        f.write(s+'\n')
        for d in data:
                s = '%s\t'%d
                for h in headers:
			ans = data[d][h]
                        s += '%s\t'%data[d][h]
               	f.write(s+'\n')
        f.close()

def write_turker_data(data, name, headers):
	f = codecs.open(name,'w','utf-8')
	s = 'id\t'
	for t in headers:
		s += '%s\t'%t
	f.write(s+'\n')
	for d in data:
		s = '%s\t'%d
		for dd in data[d]:
			s += '%s\t'%list2str(dd)
		f.write(s+'\n')
	f.close()

def get_assigns_by_type():
	sset = set()
        for line in csv.DictReader(open('%s/syn_hits_results'%RAW_DIR)):
		sset.add(line['assignment_id'])
	vset = set()
        for line in csv.DictReader(open('%s/voc_hits_results'%RAW_DIR)):
		vset.add(line['assignment_id'])
	return (sset, vset)

def clean(s):
        cleaned = s
	cleaned = s.encode('ascii', 'ignore').lower() 
	cleaned = re.sub('['+string.punctuation+']', '', cleaned) 
	cleaned = re.sub('\s+', '', cleaned)
        return cleaned

def assign_to_survey(path):
	ret = dict()
        for line in csv.DictReader(open(path), delimiter='\t'):
		aid = line['id']
		ret[aid] = line
	return ret

def worker_to_assign(path):
	ret = dict()
        for line in csv.DictReader(open(path), delimiter='\t'):
		worker = line['worker']
		if worker not in ret:
			ret[worker] = list()
		ret[worker].append(line['id'])
	return ret

def turker_langs(assignpath, workerpath, langs):
	countrymap = country_map()
	codemap = code_map()
	langmap = lang_map()
	workermap = worker_to_assign(workerpath)
	assignmap = assign_to_survey(assignpath)
        survey_data = {}
	for worker in workermap:
		survey_keys = ['country','survey','lang','hitlang', 'yrseng', 'yrssrc']
		survey_data[worker] = dict.fromkeys(survey_keys)
		for k in survey_keys:
			survey_data[worker][k] = set()	
		for assign in workermap[worker]:
			survey_data[worker]['country'].add(assignmap[assign]['country'])
			survey_data[worker]['survey'].add(assignmap[assign]['survey'])
			survey_data[worker]['hitlang'].add(assignmap[assign]['hitlang'])
			survey_data[worker]['lang'].add(assignmap[assign]['lang'])
			survey_data[worker]['yrseng'].add(assignmap[assign]['yrseng'])
			survey_data[worker]['yrssrc'].add(assignmap[assign]['yrssrc'])
        return survey_data

def lang_dups(data):
	none = dict()
	one = dict()
	more = dict()
	for t in data:	
		langs = list(data[t]['lang'])		
		ctry = list(data[t]['country'])		
		svy_ctry = list(data[t]['survey'])		
		hitlang = list(data[t]['hitlang'])		
		eng = list(data[t]['yrseng'])		
		src = list(data[t]['yrssrc'])		
		if 'N/A' in langs:
			langs.pop(langs.index('N/A'))
		if(len(langs) < 1):
			none[t] = [langs,ctry,svy_ctry,hitlang,eng,src]		
		if(len(langs) == 1):
			one[t] = [langs,ctry,svy_ctry,hitlang,eng,src]				
		if(len(langs) > 1):
			more[t] = [langs,ctry,svy_ctry,hitlang,eng,src]				
	return [none, one, more]

if __name__ == '__main__':
	
	langs = hits_language()
	
	if sys.argv[1] == 'assignments':
		#get list of assignments for voc hits and syn hits separately
		print "Extracting syn and voc assignment lists"
		ss, vs = get_assigns_by_type()
	
		print "compiling assignment data"
		## compile assignment data, full and by HIT type ##	
		sassigns = assign_langs('%s/assignments'%RAW_DIR, langs, idlist=ss)
		vassigns = assign_langs('%s/assignments'%RAW_DIR, langs, idlist=vs)
		assigns = assign_langs('%s/assignments'%RAW_DIR, langs, idlist=set(list(ss)+list(vs)))
	        write_data(sassigns,'%s/byassign.syn'%OUTPUT_DIR, ['lang','country','survey', 'hitlang', 'yrseng', 'yrssrc'])  
	        write_data(vassigns,'%s/byassign.voc'%OUTPUT_DIR, ['lang','country','survey', 'hitlang', 'yrseng', 'yrssrc'])  
	        write_data(assigns,'%s/byassign'%OUTPUT_DIR, ['lang','country','survey', 'hitlang', 'yrseng', 'yrssrc'])  
	
		print "compiling worker lists"
		## compile assignment worker lists, full and by HIT type ##	
		sassigns = assign_workers('%s/assignments'%RAW_DIR, langs, idlist=ss)
		vassigns = assign_workers('%s/assignments'%RAW_DIR, langs, idlist=vs)
		assigns = assign_workers('%s/assignments'%RAW_DIR, langs, idlist=set(list(ss)+list(vs)))
	        write_data(sassigns,'%s/byassign.workerids.syn'%OUTPUT_DIR,['worker'])
	        write_data(vassigns,'%s/byassign.workerids.voc'%OUTPUT_DIR,['worker'])
	        write_data(assigns,'%s/byassign.workerids'%OUTPUT_DIR,['worker'])

	if sys.argv[1] == 'turkers':
		print "compiling syn workers"
		# compile turker information for syn assignments
		data = turker_langs('%s/byassign.syn'%OUTPUT_DIR, '%s/byassign.workerids.syn'%OUTPUT_DIR, langs)
		write_turker_data(data,'%s/byturker.syn'%OUTPUT_DIR,['langs','country','survey','hitlang', 'yrseng', 'yrssrc'])	
		
		print "compiling voc workers"
		# compile turker information for voc assignments, dependent on number of reported langs
		data = turker_langs('%s/byassign.voc'%OUTPUT_DIR, '%s/byassign.workerids.voc'%OUTPUT_DIR, langs)
		n, o, m = lang_dups(data)
		write_turker_data(n,'%s/byturker.voc.nolang'%OUTPUT_DIR,['langs','country','survey','hitlang', 'yrseng', 'yrssrc'])	
		write_turker_data(o,'%s/byturker.voc.onelang'%OUTPUT_DIR,['langs','country','survey','hitlang', 'yrseng', 'yrssrc'])	
		write_turker_data(m,'%s/byturker.voc.multlang'%OUTPUT_DIR,['langs','country','survey','hitlang', 'yrseng', 'yrssrc'])	
