#!/usr/bin/python
import sys, os, operator, smtplib, re




from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText





def send_email(addr, subject, msg_body):	
	email_subject = subject
	from_addr="confer@csail.mit.edu"
	to_addr = [addr, 'confer@csail.mit.edu']
	
	msg = MIMEMultipart()
	msg['From'] = 'Confer Team <confer@csail.mit.edu>'
	msg['To'] = addr
	msg['Subject'] = email_subject
	msg.attach(MIMEText(msg_body))	

	smtp_conn = smtplib.SMTP_SSL('login', 25)
	smtp_conn.sendmail(from_addr, to_addr, msg.as_string())
	
	smtp_conn.close() 





def send_survey_email():
	f = open(sys.argv[1]).read()
	names = re.split('\n', f)
	subject = "Confer@CSCW 2014 -- your feedback would help us improve."
	for name in names:
		tokens = re.split(',', name.strip())
		tokens = map(lambda x: x.strip(), tokens)
		print tokens
		msg_body = """
Dear %s,

Hope you enjoyed using Confer at CSCW 2014! We would love to hear from you about your experience with Confer during the conference. Please share your comments and suggestions by completing this short survey:

https://docs.google.com/forms/d/1Vuc_tQsNwFtZ4k7b_Rumcaim7MM8hSPjw7uIdL6TSm8/viewform

We value your feedback and we look forward to serve you at future conferences! If you like, you can also contact us directly at confer@csail.mit.edu.

Best,
The Confer Team
confer@csail.mit.edu
		""" %(tokens[1])
		send_email(tokens[0], subject, msg_body)
		
	
	






def main():
	send_survey_email()
	

if __name__ == '__main__':
    main()
