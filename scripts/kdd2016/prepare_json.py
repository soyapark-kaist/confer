import sys, json, csv, re, time

papers = {}
sessions = {}
schedule = []

dt_format='%m/%d/%Y'

def construct_id(s):
  return re.sub(r'\W+', '_', s)

def get_start_time(s_time):
  s = s_time.split('-')[0].strip()
  if 'am' in s:
      s = s[:-2]
  if s == "1:00pm":
      s = "13:00"
  if s == "4:15pm":
      s = "16:15"
  if s == "1:45pm":
      s = "13:45"
  if s == "7:00pm":
      s = "19:00"
  if s == "12:15pm":
      s = "12:15"
  return int(re.match(r'\d+', s).group())
  return s

def get_date_time(s_date, dt_format='%m/%d/%Y'):
  if s_date == "Saturday":
      return time.strptime('08/13/2016', dt_format)
  if s_date == 'Sunday':
      return time.strptime('08/14/2016', dt_format)
  if s_date == 'Monday':
      return time.strptime('08/15/2016', dt_format) 
  if s_date == "Tuesday":
      return time.strptime('08/16/2016', dt_format) 
  if s_date == "Wednesday":
      return time.strptime('08/17/2016', dt_format)    
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
    
  print t_schedule

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

def get_times(stime):
  t = stime.split('-')
  t[0] = t[0].strip()
  t[1] = t[1].strip()

  if 'am' in t[0]:
      tt = t[0][:-2]
  if t[0] == "1:00pm":
      tt = "13:00"
  if t[0] == "4:15pm":
      tt = "16:15"
  if t[0] == "1:45pm":
      tt = "13:45"
  if t[0] == "7:00pm":
      tt = "19:00"
  if t[0] == "7:00pm":
      tt = "19:00"
  if t[0] == "12:15pm":
      tt = "12:15"

  if 'am' in t[1]:
      ts = t[1][:-2]
  if t[1] == "12:00pm":
      ts = "12:00"
  if t[1] == "12:30pm":
      ts = "12:30"
  if t[1] == "1:30pm":
      ts = "13:30"
  if t[1] == "3:45pm":
      ts = "15:45"
  if t[1] == "6:15pm":
      ts = "18:15"
  if t[1] == "3:00pm":
      ts = "15:00"
  if t[1] == "12:00am":
      ts = "0:00"
  if t[1] == "5:00pm":
      ts = "17:00"
  if t[1] == "12:15pm":
      ts = "12:15"
  if t[1] == "4:15pm":
      ts = "16:15"
      

  return tt + ' - ' + ts


def prepare_data(data_file1):
  f1 = open(data_file1, 'rU')
  reader1 = csv.reader(f1)
  
  p_id = 1
  
  reader1.next()
  
  t_schedule = {}
  for i, row in enumerate(reader1):
      
    type = unicode(row[1], "ISO-8859-1")
      
    paper_id = i
    paper_title = unicode(row[5], "ISO-8859-1")
    paper_authors = unicode(row[6], "ISO-8859-1")
    
    session = unicode(row[3], "ISO-8859-1")
    
    s_date = unicode(row[8], "ISO-8859-1")
    
    s_time = unicode(row[9], "ISO-8859-1")
    if s_time.strip() == '':
        continue
    
    print s_time
    s_time = get_times(s_time)
    
    room = unicode(row[10], "ISO-8859-1")
    
    website = unicode(row[11], "ISO-8859-1")
    
    paper_abstract = unicode(row[7], "ISO-8859-1")
        
    type = unicode(row[1], "ISO-8859-1").lower()
    if 'talk' in type:
        if "Applied Data" in type:
            session = "Applied Data Science Track: " + session
        if "Research" in type:
            session = "Research Track: " + session
        type = 'paper'
        
    if website:
        paper_abstract = '<a href="' + website + '">' + website + '</a><BR>' + paper_abstract
        
    if 'keynote' in type:
        type = 'talk'
        session = 'Keynote: ' + paper_title
        
    if 'panel' in type:
        type = 'panel'
        session = 'Panel: ' + paper_title
        
    if 'poster' in type:

        if "Applied Data" in type:
            session = "Applied Data Science Track Posters"
        if "Research" in type:
            session = "Research Track Posters"
        
        type = 'poster'
        
    if 'tutorial' in type:
        type = "tutorial"
        session = 'Tutorial: ' + paper_title

    if 'workshop' in type:
        type = "workshop"
        session = 'Workshop: ' + paper_title

    if session == "Applied Data Science Invited Talks":
        type = "talk"

    # prepare papers data
    papers[paper_id] = {
        'title': paper_title,
        'type': type,
    }
    
    papers[paper_id]['abstract'] = paper_abstract
    
    papers[paper_id]['authors'] = [{'name': name.strip()} for name in paper_authors.split(',') if name.strip() != '']

    
    
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
