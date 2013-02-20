langs=[]
ext_langs=[]

import os

import codecs


for dirname, dirnames, filenames in os.walk('../dictionaries/all/'):
    # print path to all filenames.
    for filename in filenames:
        #print os.path.join(dirname, filename)
		#print filename.split(".")[1]
		langs.append(filename.split(".")[1])


for dirname, dirnames, filenames in os.walk('../dictionaries/external_dictionaries/'):
    # print path to all subdirectories first.
    for subdirname in dirnames:
		#print os.path.join(dirname, subdirname)
		#print subdirname
		ext_langs.append(subdirname)

print langs
print ext_langs

for lang in langs:
	print "---"
	print "processing: "+lang
	turk_dict={}
	ext_dict={}
	overlap=0
	match=0

	if not os.path.exists("../dictionaries/external_dictionaries/"+lang+"/"+lang+"-en"):
		print "no external dictionary, skipping"
		continue

	f = codecs.open("../dictionaries/all/dictionary."+lang, encoding='utf-8')
	for line in f:
		line=line.strip()
		#print line.split("	")[0], line.split("	")[1].strip(",").split(",")
		#print line
		if line == "no word is shown!!!," or line=="error in display," or line=="?," or line=="no word written to translate,":
			continue
		try:
			word, translations =line.split("	") 
			word=word.upper()
			turk_dict[word]=translations.strip(",").split(",")
		except:
			#glith in turk dictionary, skipping
			#print "glitch: ",line
			pass
		
	f = codecs.open("../dictionaries/external_dictionaries/"+lang+"/"+lang+"-en", encoding='utf-8')
	for line in f:
		line=line.strip()
		#print line.split("	")[0], line.split("	")[1].strip(",").split(",")
		#print line
		try:
			word, translations =line.split("	") 
			word=word.upper()
			ext_dict[word.strip()]=translations.strip(",").split(",")
		except:
			#glith in external dictionary, skipping
			#print "glitch: ",line
			pass
	
	for word in turk_dict.keys():
		if ext_dict.has_key(word):
			overlap=overlap+1
			for translation in turk_dict[word]:
				if translation==ext_dict[word][0]:
					match=match+1
		
	#for word in ext_dict.keys():
	#	print "|",word,"|"
	
	print "language: ", lang
	print "turk dict size: ", len(turk_dict)
	print "ext dict size: ", len(ext_dict)
	print "overlap: ", overlap
	print "match: ", match


	
