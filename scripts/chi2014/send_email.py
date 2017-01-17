#!/usr/bin/python
import sys, os, operator, smtplib, re




from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText





def send_email(addr, subject, msg_body):	
	email_subject = subject
	from_addr="confer@csail.mit.edu"
	to_addr = [addr]
	
	msg = MIMEMultipart()
	msg['From'] = 'Confer Team <confer@csail.mit.edu>'
	msg['To'] = addr
	msg['Subject'] = email_subject
	msg.attach(MIMEText(msg_body))	
	
	smtp_conn = smtplib.SMTP_SSL('localhost', 25)	
	smtp_conn.sendmail(from_addr, to_addr, msg.as_string())
	
	smtp_conn.close() 





def send_survey_email():
	f = open(sys.argv[1]).read()
	names = re.split('\n', f)
	subject = "Confer@CHI 2014 -- make interesting connections!"
	for name in names:
		tokens = re.split(',', name.strip())
		tokens = map(lambda x: x.strip(), tokens)
		print tokens
		msg_body = """
Dear %s,

We're pleased that you're using Confer to mark the papers you want to see at CHI 2014.  Did you know Confer can also introduce you to *people* you ought to meet while you're there?  Confer has identified a number of individuals whose paper selections suggest that they share your research interests.  If you enable Confer's meetups feature, these people will be able to find you and introduce themselves!  Just go to http://confer.csail.mit.edu/chi2014/meetups and enable the meetups feature to start making some interesting connections at CHI 2014.

Best,
The Confer Team
confer@csail.mit.edu
		""" %(tokens[1])
		send_email(tokens[0], subject, msg_body)
		
	
	






def main():
	send_survey_email()
	

if __name__ == '__main__':
    main()
