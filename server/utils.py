import hashlib, smtplib, json

from server.models import *
from Crypto.Cipher import AES
from Crypto import Random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from collections import defaultdict

'''
@author: Anant Bhardwaj
@date: Sep 22, 2013
'''

kKey = 'confer'

def encrypt_text (plain_text):
  key = hashlib.sha256(kKey).digest()
  iv = Random.new().read(AES.block_size)
  cipher = AES.new(key, AES.MODE_CFB, iv)
  crypt_text = (iv + cipher.encrypt(plain_text)).encode('hex')
  return crypt_text

def decrypt_text (crypt_text):
  iv_len = AES.block_size
  key = hashlib.sha256(kKey).digest()
  iv = crypt_text.decode('hex')[:iv_len]
  cipher = AES.new(key, AES.MODE_CFB, iv)
  plain_text = cipher.decrypt(crypt_text.decode('hex'))[iv_len:]
  return plain_text

def send_email (addr, subject, msg_body): 
  email_subject = subject
  from_addr="confer@csail.mit.edu"
  to_addr = [addr, 'confer@csail.mit.edu']
  
  msg = MIMEMultipart()
  msg['From'] = 'Confer Team <confer@csail.mit.edu>'
  msg['To'] = ",".join(to_addr)
  msg['Subject'] = email_subject
  msg.attach(MIMEText(msg_body))

  smtp_conn = smtplib.SMTP('localhost', 25)
  smtp_conn.sendmail(from_addr, to_addr, msg.as_string())
  smtp_conn.close()


def insert_log (registration, action, data=None):
  if(data):
    l = Logs(registration = registration, action = action, data= data)
    l.save()
  else:
    l = Logs(registration = registration, action = action)
    l.save()


def get_registration (login, conf):
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

def get_similar_people (login, conf, meetups=False, app=None):
  likes = {}
  similarity = []
  user = User.objects.get(email = login)
  conference = Conference.objects.get(unique_name=conf)
  registrations = Registration.objects.filter(conference=conference)
  for r in registrations:
    r_valid = False
    if meetups and r.user.meetups_enabled:
      r_valid = True
    elif app:
      try:
        perm = Permission.objects.get(user=r.user, app=app)
        if perm.access:
          r_valid= True
      except Permission.DoesNotExist:
        pass
    else:
      r_valid = False

    if r_valid:
      try:        
        r_likes = Likes.objects.get(registration=r)
        likes[r.user] = {
            'id': r.user.id,
            'name': r.user.f_name + ' ' + r.user.l_name,
            'email': r.user.email,
            'friendly': r.user.friendly,
            'meetups_enabled': r.user.meetups_enabled,
            'papers': set(json.loads(r_likes.likes))
        }
      except Likes.DoesNotExist:
        pass

  for person in likes:  
    p_likes = likes[person]
    common_likes = len(likes[user]['papers'].intersection(p_likes['papers']))
    
    if common_likes > 4 and person!= user:
      similarity.append({
          'id': p_likes['id'],
          'name': p_likes['name'],
          'email': p_likes['email'],
          'friendly': p_likes['friendly'],
          'common_likes': common_likes
      })

  similarity = sorted(similarity, key=lambda k: k['common_likes'], reverse=True)
  return similarity[:20]


def get_favorites (login, conf):
  people_you_favorited = []
  people_favorited_you = []
  user = User.objects.get(email = login)
  conference = Conference.objects.get(unique_name=conf)
  registrations = Registration.objects.filter(conference=conference)
  
  registration = Registration.objects.get(user=user, conference=conference)
  user_likes = Likes.objects.get(registration=registration)


  you_favorited = AList.objects.filter(registration=registration)
  favorited_you = AList.objects.filter(user_starred=user)

  for person in you_favorited:
    try:
      r = Registration.objects.get(user=person.user_starred, conference=conference)
      p_likes = Likes.objects.get(registration=r)
      people_you_favorited.append({
          'id': person.user_starred.id,
          'name': person.user_starred.f_name + ' ' + person.user_starred.l_name,
          'email': person.user_starred.email,
          'friendly': person.user_starred.friendly,
          'common_likes': len(
              set(json.loads(user_likes.likes)).intersection(set(json.loads(p_likes.likes))))
      })
    except:
      pass

  for person in favorited_you:
    if person.registration.conference.unique_name != conf:
      continue

    r = Registration.objects.get(user=person.user, conference=conference)
    p_likes = Likes.objects.get(registration=r)
    people_favorited_you.append({
        'id': person.user.id,
        'name': person.user.f_name + ' ' + person.user.l_name,
        'friendly': person.user.friendly,
        'email': person.user.email,
        'common_likes': len(
            set(json.loads(user_likes.likes)).intersection(set(json.loads(p_likes.likes))))

    })

  return {'people_favorited_you': people_favorited_you,
      'people_you_favorited': people_you_favorited}