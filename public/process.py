#!/usr/bin/env python
#-*- coding: utf-8 -*-

##############################################

from xml.sax.saxutils import escape as html_escape
import cgi
import sys
import os
from wmflabs import db
conn = db.connect("s52964__missingpages_p")

#Print header
print 'Content-type: text/html\n'

#Print header of html document
print """
<!DOCTYPE html>
<html lang="cs-cz">
        <head>
                <meta charset="utf-8" />
                <title>Chybějící stránky</title>
        </head>
        <body>
		<p><a href="index.html">Zpět</a>
"""
###############FUNCTIONS######################
#Print end header
def tail():
	print """
        </body>
	</html>
	"""
	quit()
def escape(html):
	"""Returns the given HTML with ampersands, quotes and carets encoded."""
	html_escape_table = {
		'"': "&quot;",
		"'": "&apos;"
	}
	return html_escape(html, html_escape_table)

#Parse webargs if present
if 'QUERY_STRING' in os.environ:
	nosql = False
	last = False
	QS = os.environ['QUERY_STRING']
	qs = cgi.parse_qs(QS)
	title = qs['title'][0]
	if qs['whatlinkshere'][0] == "yes":
		whatlinkshere = True
	else:
		whatlinkshere = False
	try:
		offset = int(qs['offset'][0])
	except:
		print "Špatně nastavený offset, nastavena 0"
		offset = 0
	if 'special' in qs:
		if qs['special'][0] == 'first':
			sql = 'SELECT title FROM missingPages ORDER BY title LIMIT ' + str(offset) + ', 100'
			nosql = True
		elif qs['special'][0] == 'last':
			sql = 'SELECT title FROM missingPages ORDER BY title DESC LIMIT ' + str(offset) + ', 100'
			nosql = True
			last = True
		else:
			print "<p>Nepodporovaná hodnota speciálního parametru</p>"
			tail()
#Parse args on cmdline or throw error
else:
	whatlinkshere = False
	offset = 0
	if len(sys.argv) > 1:
		title = sys.argv[1]
		if len(sys.argv) > 3:
			if sys.argv[2] == "yes":
				whatlinkshere = True
			else:
				whatlinkshere = False
			try:
				offset = int(sys.argv[3])
			except:
				print "Špatně nastavený offset, nastavena 0"
				offset = 0
		elif len(sys.argv) == 3:
			if sys.argv[2] == "yes":
				whatlinkshere = True
			else:
				whatlinkshere = False
		elif len(sys.argv) > 4:
			print "<p>Maximálně 5 parametrů</p>"
			tail()
	else:
		print "<p>Při spouštění z příkazové řádky musí být předány parametry</p>"
		tail()

#Init db conn
cur = conn.cursor()
#Set names to utf so we could use non-ascii chars
with cur:
	cur.execute("SET NAMES utf8;")

#Init db conn
cur = conn.cursor()
#Fetch all missing pages from db
with cur:
	if not nosql:
		sql = 'SELECT title FROM missingPages WHERE title NOT LIKE "%../%" AND title LIKE "' + title + '%" AND title NOT LIKE "%(copyvio)" ORDER BY title LIMIT ' + str(offset) + ', 100'
	cur.execute(sql)
	data = cur.fetchall()

#If no data fetched, print it and quit
if len(data) == 0:
	print '<p>Nebyly nalezeny žádné výsledky. <a href="index.html">Vraťte se</a> a zkuste jiný dotaz.'
	print """
	</body>
	</html>
	"""
	quit()

#If we have more than 100 results, set it to var
cur = conn.cursor()
with cur:
	sql = 'SELECT COUNT(*) FROM missingPages;'
	cur.execute(sql)
	count = cur.fetchall()[0]
if count > 100:
	more = True
else:
	more = False

#Print results
print '<ol start="'+str(offset+1)+'">'
if whatlinkshere:
	for row in data:
		print '<li><a href="https://cs.wikipedia.org/wiki/' + escape(row[0]) + '">' + escape(row[0]) + '</a> (<a href="https://cs.wikipedia.org/wiki/Special:WhatLinksHere/' + escape(row[0]) + '">odkazy</a>)</li>'
else: 
	for row in data:
		print '<li><a href="https://cs.wikipedia.org/wiki/' + escape(row[0]) + '">' + escape(row[0]) + '</a></li>'
print "</ol>"

#If we fetched more than 100 results, do something (see TODO)
if more:
	if last:
		if whatlinkshere:
			prevm = '<a href="process.py?title=' + escape(title) + '&special=last&whatlinkshere=yes&offset=' + str(offset-100) + '">následující</a>'
			nextm = '<a href="process.py?title=' + escape(title) + '&special=last&whatlinkshere=yes&offset=' + str(offset+100) + '">předchozí</a>'
		else:
			prevm = '<a href="process.py?title=' + escape(title) + '&special=last&whatlinkshere=no&offset=' + str(offset-100) + '">následující</a>'
			nextm = '<a href="process.py?title=' + escape(title) + '&special=last&whatlinkshere=no&offset=' + str(offset+100) + '">předchozí</a>'
	else:
		if whatlinkshere:
			prevm = '<a href="process.py?title=' + escape(title) + '&whatlinkshere=yes&offset=' + str(offset-100) + '">předchozí</a>'
			nextm = '<a href="process.py?title=' + escape(title) + '&whatlinkshere=yes&soffset=' + str(offset+100) + '">následující</a>'
		else:
			prevm = '<a href="process.py?title=' + escape(title) + '&whatlinkshere=no&offset=' + str(offset-100) + '">předchozí</a>'
			nextm = '<a href="process.py?title=' + escape(title) + '&whatlinkshere=no&offset=' + str(offset+100) + '">následující</a>'
	pprint = ""
	if (offset-100)<0:
		pass
	else:
		pprint += prevm
	if (offset+100)>count:
		pass
	else:
		pprint += "\t"
		pprint += nextm
	print pprint
tail()
