#!/usr/bin/python

import cgi, cgitb

form = cgi.FieldStorage()
agg =form.getvalue("Agg")
query = form.getvalue("query")
epan=form.getvalue("epan")
numterms=form.getvalue("nterms")

if epan=='on':
	import requests, pprint, string, itertools, unicodedata
	#Need to open stopwords files  and strip out \n
	s=open('stopwords.txt','r')
	stopwords=list(s)
	for i  in range(len(stopwords)):
		if '\n' in stopwords[i]:
			stopwords[i]=stopwords[i].replace('\n','')
	goo_query=query
	bing_query=query
	blekko_query=query
	#AND query (default)
	if 'AND' in query:
		bing_query = query.replace(' AND ', '%20')
		goo_query = goo_query.replace(' AND ','+')
		blekko_query = blekko_query.replace(' AND ','+')
	if 'NOT' in query:
		goo_query = goo_query.replace('NOT ', '%2D')
		blekko_query = blekko_query.replace('NOT ', '%2D')
	if 'OR' in query:
		blekko_query=blekko_query.replace(' OR ','+')
	bing_query= bing_query.replace (' ', '%20')
	goo_query= goo_query.replace(' ', '+')
	blekko_query= blekko_query.replace(' ', '+')
	bl_endpoint= 'http://blekko.com/?q='+ blekko_query + '+/json+/ps=10&auth=f4c8acf3'
	ra = requests.get(bl_endpoint)
	j= ra.json()
	#GOOGLE
	g_endpoint= 'https://www.googleapis.com/customsearch/v1?key=AIzaSyA2ULv8aRUlKy2XKKBi1VjCWTi8zQxGtNs&cx=003443407933899782589%3Ahd1inenzhnc&q='+goo_query+'&alt=json'
	rb = requests.get(g_endpoint)
	k = rb.json()
	#BING
	key='ytZAPqEk6j25+YaJrFPf5fX4WbE6GumW+RK6hLKHcK0'
	# &$top=10 number results return ie 10
	bi_endpoint='https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/Web?Query=%27'+bing_query+'%27&$top=10&$format=json'
	rc = requests.get(bi_endpoint,auth=(key,key))
	l = rc.json()
	#Sort out snippets
	snippets=[]
	for i in k['items']:
		snippets.append(i['snippet'])
	for i in l['d']['results']:
		snippets.append(i['Description'])
	for i in j['RESULT']:
		snippets.append(i['snippet'])
	for i in range(len(snippets)):
		snippets[i]=snippets[i].lower()
		snippets[i]=snippets[i].replace('<strong>','')	
		snippets[i]=snippets[i].replace('</strong>','')
		snippets[i]=snippets[i].replace('&#39;','\'')
		snippets[i]=snippets[i].split()
	snippets=list(itertools.chain.from_iterable(snippets))
	for i in range(len(snippets)):
		snippets[i]=unicodedata.normalize('NFKD', snippets[i]).encode('ascii','ignore')
		snippets[i]=snippets[i].translate(None, string.punctuation)
	#strip punct and stop and stem as above
	while '' in snippets:
		snippets.remove('')
	#stopword removal
	for i in range(len(stopwords)):
		while stopwords[i] in snippets:
			snippets.remove(stopwords[i])
	#count items in snippets and sort by score
	kterms = [(x, snippets.count(x)) for x in set(snippets)]
	kterms = sorted(kterms, key=lambda x: x[1], reverse =True)
	#get top five that don't match query tokenise query and remove from kterms
	t_query=query.lower()
	t_query=t_query.split()
	kterms=[x for x in kterms if x[0] not in t_query]
	q_expand_list=[x[0] for x in kterms[:int(numterms)]]
	for i in range(len(q_expand_list)):
		query=query+' '+q_expand_list[i]

if agg=='off':
	print "Location:http://inismean.ucd.ie/~04549309/cgi/results_parse.cgi?query=%s&Agg=off" %query
 
if agg=='on':
	 	print "Location:http://inismean.ucd.ie/~04549309/cgi/results_parse_agg.cgi?query=%s&Agg=on" %query 

print "Content-Type: text/html; charset=utf-8\n\n"
