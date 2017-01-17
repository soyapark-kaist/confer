#!/usr/bin/python
import sys, os, operator, smtplib

if __name__ == "__main__":
	p = os.path.abspath(os.path.dirname(__file__))
	if(os.path.abspath(p+"/..") not in sys.path):
		sys.path.append(os.path.abspath(p+"/.."))
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

from django.db import connection


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


'''
@author: anant bhardwaj
@date: Feb 12, 2013

script for preparing data in lenskit format
'''


def send_email(addr, subject, msg_body):	
	email_subject = subject
	from_addr="mychi@csail.mit.edu"
	to_addr = [addr]
	
	msg = MIMEMultipart()
	msg['From'] = 'myCHI <mychi@csail.mit.edu>'
	msg['To'] = addr
	msg['CC'] = 'mychi@csail.mit.edu'
	msg['Subject'] = email_subject
	msg.attach(MIMEText(msg_body))	

	smtp_conn = smtplib.SMTP_SSL('localhost', 25)
	smtp_conn.login(username, password)	
	
	smtp_conn.sendmail(from_addr, to_addr, msg.as_string())
	
	smtp_conn.close() 





def send_survey_email():
	subject = "ACM links and Bibtex export"
	cursor = connection.cursor()
	cursor.execute("select distinct login_id, given_name, family_name, email1 from logs, pcs_authors where pcs_authors.id = login_id LIMIT 5000 OFFSET 132;")
	data = cursor.fetchall()
	for row in data:
		name = row[3]
		if(row[1]!=None and row[2]!=None):
			name = str(repr(row[1] +' ' + row[2])).lstrip("u'").rstrip("'")
		msg_body = """
Dear %s,

Hope you enjoyed using myCHI at CHI 2013! To help you access and share your favorite papers, we have added two new features:

1. We have added ACM links to each paper so that you can easily download your favorite papers.
2. We have added BibTeX export for your favorite papers so you can easily reference them and share them with others.

We would love to hear from you about your experience with myCHI this year. Please share your comments and suggestions by completing this short survey:

https://docs.google.com/forms/d/1z_dTPMUoQHnT-M3R0HHozQqTrPnAQP1IapAsTYvAQ-U/viewform

We look forward to serve you at future conferences! If you like, you can also contact us directly at mychi@csail.mit.edu.

Best,
The myCHI team
http://mychi.mit.csail.edu

		""" %(name)
		send_email(row[3], subject, msg_body)
	
	






def main():
	send_survey_email()
	

if __name__ == '__main__':
    main()
