#!/usr/bin/python

import cgi, cgitb, requests, json, unicodedata

form = cgi.FieldStorage()
query = form.getvalue('query')
agg = form.getvalue('Agg')

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

#BLEKKO
endpoint= 'http://blekko.com/?q='+ blekko_query + '+/json+/ps=10&auth=f4c8acf3'

r = requests.get(endpoint)
j= r.json()

blekko=[]
for i in j['RESULT']:
	blekko.append(i['url'])

#GOOGLE

endpoint= 'https://www.googleapis.com/customsearch/v1?key=AIzaSyA2ULv8aRUlKy2XKKBi1VjCWTi8zQxGtNs&cx=003443407933899782589%3Ahd1inenzhnc&q='+goo_query+'&alt=json'

r = requests.get(endpoint)
k = r.json()

goo=[]
for i in k['items']:
	goo.append(i['link'])
	
#BING

key='ytZAPqEk6j25+YaJrFPf5fX4WbE6GumW+RK6hLKHcK0'

# &$top=10 number results return ie 10
endpoint='https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/Web?Query=%27'+bing_query+'%27&$top=10&$format=json'

r = requests.get(endpoint,auth=(key,key))
l = r.json()

bing=[]
for i in l['d']['results']:
	bing.append(i['Url'])
	
#Strip function for common name

def remover (list):
    for i in range(len(list)):
            list[i]=list[i].replace('https','')
            list[i]=list[i].replace('http','')
            list[i]=list[i].replace('://','')
            list[i]=list[i].replace('www.','')
    return

remover(blekko)
remover(goo)
remover(bing)

#create dicts with common name full url and scores

maxscore =100.
i=0
blek_info= {}
for item in j['RESULT']:
	blek_info[blekko[i]]=[item['url'],(maxscore-i),item['url_title'],item['snippet']]
	i= i+1

i=0
goo_info={}
for item in k['items']:
	goo_info[goo[i]]=[item['link'],(maxscore-i),item['htmlTitle'],item['snippet']]
	i =i+1

i=0
bing_info={}
for item in l['d']['results']:
	bing_info[bing[i]]=[item['Url'],(maxscore-i),item['Title'],item['Description']]
	i =i+1

#compare results and aggregate scores into final list then sort list by score

final=[]
for key in goo_info:
	if key in goo_info and key in blek_info and key in bing_info:
		scores= goo_info[key][1]+blek_info[key][1]+bing_info[key][1]
		scores = scores*3
		final.append([goo_info[key][0],scores,goo_info[key][2],goo_info[key][3]])
		del blek_info[key], bing_info[key]
	elif key in goo_info and key in blek_info:
		scores= goo_info[key][1]+blek_info[key][1]
		scores = scores*2
		final.append([goo_info[key][0],scores,goo_info[key][2],goo_info[key][3]])
		del blek_info[key]
	elif key in goo_info and key in bing_info:
		scores= goo_info[key][1]+bing_info[key][1]
		scores = scores*2
		final.append([goo_info[key][0],scores,goo_info[key][2],goo_info[key][3]])
		del bing_info[key]		
	else:
		final.append([goo_info[key][0],goo_info[key][1],goo_info[key][2],goo_info[key][3]])

for key in blek_info:
	if key in blek_info and key in bing_info:
		scores= blek_info[key][1]+bing_info[key][1]
		scores = scores*2
		final.append([blek_info[key][0],scores,blek_info[key][2],blek_info[key][3]])
		del bing_info[key]
	else:
		final.append([blek_info[key][0],blek_info[key][1],blek_info[key][2],blek_info[key][3]])

for key in bing_info:
	final.append([bing_info[key][0],bing_info[key][1],bing_info[key][2],bing_info[key][3]])				

final.sort(key=lambda list: list[1])
final.reverse()

print "Content-Type: text/html; charset=utf-8\n\n"

print"""
<!DOCTYLE html>

<html>
<head>
	<title> Trio - Results Agg On </title>
	<link rel=\"stylesheet\" href=\"../stylesheet_res_agg.css\" /> 
</head>

<body>
	<div id ="wrapper">
		<h1> Trio </h1>
		<div id="search">
						<form action="forwarding.cgi" method="get">
								<div class=search_param>	Enter Query: <input type="text" name="query"> 
																											<input type="submit" value="submit" />	
								</div>
								<div class=search_filters>	Aggregation:<input type="radio" name="Agg" checked="yes" value="on">On
																												<input type="radio" name="Agg" value="off">Off 
																						&nbsp|&nbsp Expand Query:<input type="radio" name="epan" value="on">On
																												 <input type="radio" name="epan" checked="yes" value="off">Off 
																					  &nbsp|&nbsp Expand factor:<select name ="nterms">
																																				<option value=1>1</option>
																																				<option value=2>2</option>
																																				<option value=3>3</option>
																																				<option value=4>4</option>
																																				<option value=5>5</option>
																																			</select>
								</div>
						</form>
		</div>
		
		<div id="res_wrap">
			
				<div id="results">
					<p>Aggregated Results for %s</p>
							<ol>
""" % query

for i in range(len(final)):
	print	"<li><a href=\"%s\">%s</a></li>" % (final[i][0], unicodedata.normalize('NFKD',final[i][2]).encode('ascii','ignore'))
	print "<p class=\"listpara\"> %s</p>"  % (unicodedata.normalize('NFKD',final[i][3]).encode('ascii','ignore'))

print"""
							</ol>
				</div>
		</div>		
	</div>
</body>
</html>
"""