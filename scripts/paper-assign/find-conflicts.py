#!/usr/bin/python
import json
import traceback
from collections import OrderedDict

print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers

print "<TITLE>Conflicting Sessions</TITLE>"
parallelSessions = 3

conflicts = []
multi = []

try:
	with open('session-list.json', 'r') as content_file:
		sessions = content_file.read()
	with open('paper-list.json', 'r') as content_file:
		papers = content_file.read()
	sessionDict = json.loads(sessions,object_pairs_hook=OrderedDict)
	paperDict = json.loads(papers,object_pairs_hook=OrderedDict)
	sessionKeys = sessionDict["sessions"].keys()
	sessionSets = [sessionKeys[i:i+3] for i in range(0,len(sessionKeys),3)]
	for ss in sessionSets:
		authsSoFar = {}
		for s in ss:
			papers = sessionDict["sessions"][s]["papers"]
			for pid in papers:
				p = paperDict["papers"][pid]
				auths = p["authors"]
				for a in auths:
					if a["name"] in authsSoFar.keys():
						if (authsSoFar[a["name"]][0] == s):
							#print "<b>MULTIPLE PAPERS:</b>",a["name"]," HAS TWO PAPERS IN",s,"<br>"
							multi.append([a["name"],authsSoFar[a["name"]][0],authsSoFar[a["name"]][1],p["title"]])
						else:
							#print "<b>CONFLICT:</b>",a["name"]," IN TWO CONCURRENT SESSIONS (",s,"and",authsSoFar[a["name"]][0],")<br>"
							conflicts.append([a["name"],authsSoFar[a["name"]][0],authsSoFar[a["name"]][1],s,p["title"]])
					authsSoFar[a["name"]] = [s,p["title"]]
except Exception:
	traceback.print_exc()
	pass

print "<H2>PAPERS WITH SAME AUTHOR IN CONCURRENT SESSIONS</H2>\n"
print "<table class='conflictTable'><tr><th>Author<th>Session 1<th>Paper 1<th>Session 2<th>Paper 2\n"
for c in conflicts:
	print "<tr><td>%s<td>%s<td>%s<td>%s<td>%s\n" % (c[0],c[1],c[2],c[3],c[4])
print "</table>\n<H2>SESSIONS WITH MULTIPLE PAPERS WITH SAME AUTHOR</H2>\n"
print "<table class='conflictTable'><tr><th>Author<th>Session<th>Paper 1<th>Paper 2\n"
for m in multi:
	print "<tr><td>%s<td>%s<td>%s<td>%s\n" % (m[0],m[1],m[2],m[3])
print "</table>"
