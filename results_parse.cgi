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
	
bing_query = bing_query.replace(' ', '%20')
goo_query = goo_query.replace(' ', '+')
blekko_query = blekko_query.replace(' ', '+')

#BLEKKO
endpoint= 'http://blekko.com/?q='+ blekko_query + '+/json+/ps=10&auth=f4c8acf3'

r = requests.get(endpoint)
j= r.json()


#GOOGLE

endpoint= 'https://www.googleapis.com/customsearch/v1?key=AIzaSyA2ULv8aRUlKy2XKKBi1VjCWTi8zQxGtNs&cx=003443407933899782589%3Ahd1inenzhnc&q='+goo_query+'&alt=json'

r = requests.get(endpoint)
k = r.json()

#BING

key='ytZAPqEk6j25+YaJrFPf5fX4WbE6GumW+RK6hLKHcK0'

# &$top=10 number results return ie 10
endpoint='https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/Web?Query=%27'+bing_query+'%27&$top=10&$format=json'

r = requests.get(endpoint,auth=(key,key))
l = r.json()

print "Content-Type: text/html; charset=utf-8\n\n"


print"""
<!DOCTYPE html>
<html>
<head>
	<title> Trio - Results Agg Off </title>
	<link rel=\"stylesheet\" href=\"../stylesheet_res_no_agg.css\" /> 
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
			
			<div id="goo">
					<!-- Goo results -->
					<p>Google Results for "%s"</p>
						<ol>
""" % query

for i in k['items']:
	print "<li> <a href=\"%s\">%s</a> </li>" % (i['link'], unicodedata.normalize('NFKD', i['htmlTitle']).encode('ascii','ignore'))
	print "<p class=\"listpara\"> %s</p>"  % (unicodedata.normalize('NFKD', i['snippet']).encode('ascii','ignore'))
		
print"""
						</ol>
			</div>
			
			<div id="bing">
					<!--bing res-->
					<p>Bing Results for "%s"</p>
					<ol>
""" % query

for i in l['d']['results']:
	print "<li> <a href=\"%s\">%s</a> </li>" % (i['Url'], unicodedata.normalize('NFKD', i['Title']).encode('ascii','ignore'))
	print "<p class=\"listpara\"> %s</p>"  % (unicodedata.normalize('NFKD', i['Description']).encode('ascii','ignore'))
	
print"""
					</ol>
			</div>
		
			<div id="blek">
					<!--blek res -->
					<p>Blekko Results for "%s"</p>
					<ol>
""" % query

for i in j['RESULT']:
	print "<li> <a href=\"%s\">%s</a> </li>" % (i['url'], unicodedata.normalize('NFKD',i['url_title']).encode('ascii','ignore'))
	print "<p class=\"listpara\"> %s</p>"  % (unicodedata.normalize('NFKD', i['snippet']).encode('ascii','ignore'))

print"""	
					</ol>
			</div>
		</div>		
	</div>
</body>
</html>
""" 

