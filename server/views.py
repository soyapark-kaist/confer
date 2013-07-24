import json, sys, re, hashlib, smtplib, base64, urllib


from django.http import *
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.core.context_processors import csrf
from django.core.validators import email_re
from django.db.utils import IntegrityError

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from algorithm.recommend import *
from models import *

p = os.path.abspath(os.path.dirname(__file__))
if(os.path.abspath(p+"/..") not in sys.path):
	sys.path.append(os.path.abspath(p+"/.."))





'''
@author: Anant Bhardwaj
@date: Feb 12, 2012
'''

kLogIn = "SESSION_LOGIN"
kConf = "SESSION_CONF"
kName = "SESSION_NAME"


r = Recommender()
offline_recs = None
try:
	offline_recs = json.loads(open('data/sigmod2013/similar_papers.json').read())
except:
	offline_recs = json.loads(open('/production/confer/data/sigmod2013/similar_papers.json').read())


'''
LOGIN/REGISTER
'''
def login_required(f):
    def wrap(request, *args, **kwargs):
        if kLogIn not in request.session.keys():
        	redirect_url = urllib.quote("/%s/%s" %(args[0], f.__name__))
        	return HttpResponseRedirect("/login?redirect_url=%s" %(redirect_url))
        return f(request, *args, **kwargs)
    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def login_form(request, redirect_url='/', errors=[]):
    c = {'redirect_url':redirect_url, 'errors':errors}
    c.update(csrf(request))
    return render_to_response('login.html', c)


def register_form(request, redirect_url='/', errors=[]):
    c = {'redirect_url':redirect_url, 'errors':errors}
    c.update(csrf(request))
    return render_to_response('register.html', c)


def login(request):
    redirect_url = '/'
    if('redirect_url' in request.GET.keys()):
    	redirect_url = request.GET['redirect_url']
    if request.method == "POST":
    	errors = []
        try:
            login_email = request.POST["login_email"]
            login_password = hashlib.sha1(request.POST["login_password"]).hexdigest()
            user = User.objects.get(email=login_email, password=login_password)
            request.session.flush()
            request.session[kLogIn] = user.email
            request.session[kName] = user.f_name
            return HttpResponseRedirect(request.POST['redirect_url'])
        except User.DoesNotExist:
        	try:
        		User.objects.get(email=login_email)
        		errors.append('Wrong password.')
        	except User.DoesNotExist:
        		errors.append("Couldn't locate account with email address: %s" %(login_email))
        	return login_form(request, redirect_url = redirect_url, errors = errors) 
        except:
            errors.append('Login failed.')
            return login_form(request, redirect_url = redirect_url, errors = errors)          
    else:
        return login_form(request, redirect_url)

def register(request):
    redirect_url = '/'
    if('redirect_url' in request.GET.keys()):
    	redirect_url = request.GET['redirect_url']
    if request.method == "POST":
    	errors = []
        try:
            error = False
            email = request.POST["email"]
            password = request.POST["password"]
            password2 = request.POST["password2"]
            f_name = request.POST["f_name"]
            l_name = request.POST["l_name"]
            if(email_re.match(email.strip()) == None):
            	errors.append("Invalid Email.")
            	error = True
            if(f_name.strip() == ""):
            	errors.append("Empty First Name.")
            	error = True
            if(l_name.strip() == ""):
            	errors.append("Empty Last Name.")
            	error = True
            if(password == ""):
            	errors.append("Empty Password.")
            	error = True
            if(password2 != password):
            	errors.append("Password and Confirm Password don't match.")
            	error = True

            if(error):
            	return register_form(request, redirect_url = redirect_url, errors = errors)
            hashed_password = hashlib.sha1(password).hexdigest()
            user = User(email=email, password=password, f_name=f_name, l_name=l_name)
            user.save()
            request.session.flush()
            request.session[kLogIn] = user.email
            request.session[kName] = user.f_name
            return HttpResponseRedirect(request.POST['redirect_url'])
        except IntegrityError:
            errors.append("Account already exists. Please Log In.")
            return register_form(request, redirect_url = redirect_url, errors = errors)
        except:
            errors.append("Some error happened while trying to create an account. Please try again.")
            return register_form(request, redirect_url = redirect_url, errors = errors)
    else:
        return register_form(request, redirect_url = redirect_url)


def logout(request):
    request.session.flush()
    if kLogIn in request.session.keys():
    	del request.session[kLogIn]
    if kName in request.session.keys():
    	del request.session[kName]
    return HttpResponseRedirect('/')




'''
EMAIL
'''

def send_email(addr, subject, msg_body):	
	email_subject = subject
	from_addr="confer@csail.mit.edu"
	to_addr = [addr, 'confer@csail.mit.edu']
	
	msg = MIMEMultipart()
	msg['From'] = 'Confer Team <confer@csail.mit.edu>'
	msg['To'] = ",".join(to_addr)
	msg['Subject'] = email_subject
	msg.attach(MIMEText(msg_body))	
	
	
	username = 'anantb'
	password = 'JcAt250486'
	smtp_conn = smtplib.SMTP_SSL('cs.stanford.edu', 465)
	#smtp_conn.ehlo()
	#smtp_conn.starttls()
	#smtp_conn.ehlo()
	smtp_conn.login(username, password)	
	#smtp_conn.set_debuglevel(True)	
	smtp_conn.sendmail(from_addr, to_addr, msg.as_string())
	smtp_conn.close() 



@csrf_exempt
def verify_email(request, login_email):
	email_plain = base64.b64decode(login_email)
	subject = "Welcome to Confer"
	email_encoded = login_email
	msg_body = """
	Dear %s,

	Thanks for registering! Please click the link below to start using Confer:

	http://confer.csail.mit.edu/verify/%s

	""" %(email_plain, email_encoded)
	send_email(email_plain, subject, msg_body)
	return HttpResponse(json.dumps({'status':'ok'}),  mimetype="application/json")


@csrf_exempt
def reset_email(request, login_email):
	email_plain = base64.b64decode(login_email)
	email_encoded = login_email
	subject = "myCHI password reset"
	msg_body = """
	Dear %s,

	Please click the link below to reset your myCHI password:

	http://mychi.csail.mit.edu/reset/%s

	""" %(email_plain, email_encoded)
	send_email(email_plain, subject, msg_body)
	return HttpResponse(json.dumps({'status':'ok'}),  mimetype="application/json")

@csrf_exempt
def verify(request, addr):
	login_email = base64.b64decode(addr)
	cursor = connection.cursor()
	cursor.execute("""SELECT id from pcs_authors where email1 like '%s' or 
					email2 like '%s' or email3 like '%s';""" %(login_email, login_email, login_email))
	data = cursor.fetchall()
	if(len(data) == 0):
		cursor.execute("""INSERT into pcs_authors (id, email1) values('%s', '%s');""" %(addr, login_email))
	
	return login_form(request, error = {'login_email':urllib.quote(base64.b64encode(login_email)), 'type': 'info', 'error': 'Thanks for verifying. Please enter your email and password.'})



@csrf_exempt
def reset(request, addr):
	login_email = base64.b64decode(addr)
	cursor = connection.cursor()
	cursor.execute("""UPDATE pcs_authors SET password = null where email1 like '%s' or 
					email2 like '%s' or email3 like '%s';""" %(login_email, login_email, login_email))	
	return login_form(request, error = {'login_email':urllib.quote(base64.b64encode(login_email)), 'type': 'info', 'error': 'Please enter a new password.'})
		



'''
PAGES
'''

def home(request):
	try:
		conferences = Conference.objects.all().values()
		return render_to_response('home.html', {'conferences':conferences})
	except:
		pass


def conf(request,conf):
	try:
		request.session[kConf] = conf
		Conference.objects.get(unique_name=conf)
		return HttpResponseRedirect('/%s/papers' %(conf))
	except:
		return HttpResponseRedirect('/')

@login_required
def papers(request, conf):
	try:
		Conference.objects.get(unique_name=conf)
		request.session[kConf] = conf
		return render_to_response('papers.html', {'conf':conf})
	except:
		return HttpResponseRedirect('/')
	
	

@login_required
def schedule(request, conf):
	try:
		Conference.objects.get(unique_name=conf)
		request.session[kConf] = conf
		return render_to_response('schedule.html', {'conf':conf})
	except:
		return HttpResponseRedirect('/')


@login_required
def paper(request, conf):
	try:
		request.session[kConf] = conf
		return render_to_response('paper.html', 
		{'conf':conf})
	except:
		return HttpResponseRedirect('/')



def get_registration(login, conf):
	try:
		user = User.objects.get(email = login)
		conference = Conference.objects.get(unique_name = conf)
		try:
			registration = Registration.objects.get(user = user, conference = conference)
			return registration
		except Registration.DoesNotExist:
			registration = Registration(user = user, conference = conference)
			registration.save()
			return registration
	except:
		print sys.exc_info()
		return None


@csrf_exempt
@login_required
def data(request):
	recs = []
	likes = []
	login = request.session[kLogIn]
	error = False
	msg = 'OK'
	try:
		conf = request.session[kConf]
		registration = get_registration(login, conf)
		data = None
		try:
			data = Likes.objects.get(registration = registration)
		except:
			data = Likes(registration = registration, likes = json.dumps([]))
			data.save()
		l = data.likes
		if(l!=None):
			likes.extend(json.loads(l))
		else:
			data.likes = json.dumps([])
			data.save()
		#print likes
		if(len(likes)>0):
			recs = compute_recs(likes)
		#print recs
	except:
		error = True
		e_type, value, tb = sys.exc_info()
		msg = value.message
	return HttpResponse(json.dumps({
			'login_id': login,
			'login_name': request.session[kName],
			'recs':recs, 
			'likes':likes,
			'error': error,
			'msg':msg
			}), mimetype="application/json")



def compute_recs(papers):
	recs = {}
	sorted_recs = []
	try:
		for paper in papers:
			r = offline_recs[paper]
			for p in r:
				id = p.keys()[0]
				if(id in papers):
					continue
				if((id in recs) and (recs[id]>p[id])):
					pass
				else:				
					recs[id]=p[id]
		sorted_recs = sorted(recs.keys(), key=operator.itemgetter(1))
	except:
		#print sorted_recs
		return sorted_recs[0:20]



@csrf_exempt
def get_recs(request):
	try:
		papers = json.loads(request.POST["papers"])
		recs = []
		#recs = r.get_item_based_recommendations(papers)
		return HttpResponse(json.dumps(recs), mimetype="application/json")
	except:
		return HttpResponse(json.dumps({'error':True}), mimetype="application/json")



def insert_log(registration, action, data=None):
	if(data):
		l = Logs(registration = registration, action = action, data= data)
		l.save()
	else:
		l = Logs(registration = registration, action = action)
		l.save()




@csrf_exempt
def log(request, action):
	try:
		login = request.session[kLogIn]
		conf = request.session[kConf]
		registration = get_registration(login, conf)
		insert_log(registration, action)
		return HttpResponse(json.dumps({'error':False}), mimetype="application/json")
	except:
		print sys.exc_info()
		return HttpResponse(json.dumps({'error':True}), mimetype="application/json")



@csrf_exempt
def like(request, like_str):
	login = request.session[kLogIn]
	likes = []
	res = {}
	error = False
	msg = "OK"
	try:
		papers = json.loads(request.POST["papers"])
		conf = request.session[kConf]
		registration = get_registration(login, conf)
		data = None
		insert_log(registration, like_str, papers)
		try:
			data = Likes.objects.get(registration = registration)
			likes.extend(json.loads(data.likes))
		except:
			data = Likes(registration = registration, likes = json.dumps([]))
			data.save()		
		
		for paper_id in papers:
			if(like_str=='star' and (paper_id not in likes) and paper_id != ''):
				likes.append(paper_id)
			if(like_str=='unstar' and (paper_id in likes) and paper_id != ''):
				likes.remove(paper_id)

		l = list(set(likes))		
		data.likes = json.dumps(l)
		data.save()
		recs = []
		if(len(likes)>0):
			recs = compute_recs(likes)		
	except:
		error = True
		e_type, value, tb = sys.exc_info()
		msg = value.message
	return HttpResponse(json.dumps({'recs':recs, 'likes':l, 'error':error, 'msg':msg}), mimetype="application/json")




