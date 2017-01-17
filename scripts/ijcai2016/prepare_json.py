import sys, json, csv, re, time

papers = {}
sessions = {}
schedule = []

dt_format='%m/%d/%Y'

def construct_id(s):
  return re.sub(r'\W+', '_', s)

def get_start_time(s_time):
  s = s_time.split('-')[0].strip()
  return int(re.match(r'\d+', s).group())
  return s

def get_date_time(s_date, dt_format='%m/%d/%Y'):
  if s_date == "7/12/2016":
      return time.strptime('07/12/2016', dt_format)
  if s_date == '7/13/2016':
      return time.strptime('07/13/2016', dt_format)
  if s_date == '7/14/2016':
      return time.strptime('07/14/2016', dt_format) 
  if s_date == "7/15/2016":
      return time.strptime('07/15/2016', dt_format)    
  #time_struct = time.strptime(s_date, dt_format)
  #return time_struct

def get_day(time_struct):
  return time.strftime("%A", time_struct)

def get_date(time_struct):
  return time.strftime("%m/%d/%Y", time_struct)

def get_class(s_time):
  v =  get_start_time(s_time)
  if(v < 10 and v >= 7):
    return 'morning1'
  elif(v >= 8 and v < 12):
    return 'morning2'
  elif(v >= 12 and v < 15):
    return 'afternoon1'
  elif(v >= 15 and v < 18):
    return 'afternoon2'
  else:
    return 'evening'

def prepare_schedule(t_schedule):
  # sort schedule data
  for s_date in t_schedule:    
    t_schedule[s_date] = sorted(
      t_schedule[s_date].items(), key = lambda x: get_start_time(x[0]))

  t_schedule = sorted(t_schedule.items(), key=lambda x: time.mktime(get_date_time(x[0], dt_format=dt_format)))
  for day_schedule in t_schedule:
    slots = []
    s_date = day_schedule[0]
    all_slots = day_schedule[1]
    for slot_info in all_slots:
      slot_time = slot_info[0]
      slot_sessions = slot_info[1]['sessions']
      slots.append({
        'time': slot_time,
        'sessions': slot_sessions,
        'slot_class': get_class(slot_time),
        'slot_id': construct_id(s_date + slot_time)
      })
    schedule.append({'date': get_date(get_date_time(s_date, dt_format=dt_format)), 'slots': slots, 'day': get_day(get_date_time(s_date, dt_format=dt_format))})

def prepare_data(data_file1):
  f1 = open(data_file1, 'rU')
  reader1 = csv.reader(f1)
  
  p_id = 1
  
  reader1.next()
  
  t_schedule = {}
  for row in reader1:
    paper_id = unicode(row[0], "ISO-8859-1")
    paper_title = unicode(row[2].decode('utf-8'))
    paper_authors = unicode(row[3].decode('utf-8'))
    keywords = unicode(row[4].decode('utf-8')).strip('"')
    session = unicode(row[5].decode('utf-8'))
    session_chair = unicode(row[6].decode('utf-8'))
    s_date = unicode(row[7], "ISO-8859-1")
    s_time = unicode(row[8], "ISO-8859-1")
    room = unicode(row[9], "ISO-8859-1")
    paper_abstract = unicode(row[10], "ISO-8859-1")
    
    if paper_abstract.strip() == '-':
        paper_abstract = ''
        
    if paper_title.strip() == '-' or paper_title.strip() == '':
        paper_title = session
    
    if session_chair.strip() != '-' and session_chair.strip() != '':
        session = session + ' - Chair: ' + session_chair
        
    type = unicode(row[1], "ISO-8859-1")
    if type == "Main Track" or type == "AI&Web Track":
        type = 'paper'
    elif 'posters' in session.lower():
        type = 'poster'
    elif 'demos' in session.lower():
        type = 'demo'
    else:
        type = 'talk'

    # prepare papers data
    papers[paper_id] = {
        'title': paper_title,
        'type': type,
    }
    
    if keywords.strip() != '-' and keywords.strip() != '':
        papers[paper_id]['keywords'] = keywords
    
    papers[paper_id]['abstract'] = paper_abstract
    
    
    
    paper_authors = re.sub(' and ', ', ', paper_authors)
    
    
    if paper_authors.strip() != '-' and paper_authors.strip() != '':
        papers[paper_id]['authors'] = [{'name': name.strip()} for name in paper_authors.split(',') if name.strip() != '']
    else:
        if session_chair != '-':
            papers[paper_id]['authors'] = [session_chair]
        papers[paper_id]['authors'] = []
    
    
    # prepare sessions data
    s_id = construct_id(session)
    if(s_id in sessions):
      sessions[s_id]['submissions'].append(paper_id)
    else:
      sessions[s_id] = {
          'submissions': [paper_id], 's_title': session, 'room': room, 'time': s_time, 'date': s_date}

    p_id += 1

  # prepare schedule data
  for session in sessions:
    s_info = sessions[session]
    s_date = s_info['date']
    s_time = s_info['time']
    s_data = {'session': session, 'room': s_info['room']}
    if s_date in t_schedule:
      if s_time in t_schedule[s_date]:
        t_schedule[s_date][s_time]['sessions'].append(s_data)
      else:
        t_schedule[s_date][s_time] = {'time': s_time, 'sessions':[s_data] }
    else:
      t_schedule[s_date] =  {s_time: {'time': s_time, 'sessions':[s_data]}}

  prepare_schedule(t_schedule)


def main():
  conf = sys.argv[2]
  data_file1 = sys.argv[1]
  prepare_data(data_file1)
  # write files
  p = open('data/' + conf + '/papers.json','w')
  p.write(json.dumps(papers, indent=2, sort_keys=True))
  p = open('server/static/conf/' + conf + '/data/papers.json','w')
  p.write('entities='+json.dumps(papers, indent=2, sort_keys=True))
  p = open('server/static/conf/' + conf + '/data/sessions.json','w')
  p.write('sessions='+json.dumps(sessions, indent=2, sort_keys=True))
  p = open('server/static/conf/' + conf +'/data/schedule.json','w')
  p.write('schedule='+json.dumps(schedule, indent=2, sort_keys=True))
  

if __name__ == "__main__":
  main()
