#99682	pam	arung	nose	NA	3275:Nose
#1788	hi:en:	IN:	IN:	new:hi:	15:	5:23:
#['Italy',78],

import csv

pass1_turkers = set()

for line in open('data/pass-1').readlines() :
	_, _, _, _, _, workers = line.strip().split('\t',5)
	for wt in workers.split('\t'):
		w,t = wt.split(':',1)
		pass1_turkers.add(w)

cmap = {l.strip().split()[1] : l.strip().split()[0] for l in open('../ref/countrynames').readlines()}

country_counts = {}
tot = 0

for line in csv.DictReader(open('data/turkers.tsv'), delimiter='\t') :
	countries = [c for c in line['country'].split(':') if not c.strip() == '']
	if len(countries) > 1 : print countries; continue;
	for country in countries : 
		try : country = cmap[country]
		except : continue
		if country not in country_counts : country_counts[country] = 0
		if line['id'] in pass1_turkers : country_counts[country] += 1; tot += 1;

print tot

for l in sorted(country_counts.keys()) : 
	print "['%s',%d],"%(l,country_counts[l])
