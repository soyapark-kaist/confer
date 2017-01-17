import sys, json, csv, re, time

papers = {}
sessions = {}
schedule = []

dt_format='%m-%d-%y'

def construct_id(s):
  return re.sub(r'\W+', '_', s)

def get_start_time(s_time):
  s = s_time.strip()[0:5]
  return int(re.match(r'\d+', s).group())

def get_date_time(s_date, dt_format='%m-%d-%y'):
  return time.strptime(s_date, dt_format)  
  #time_struct = time.strptime(s_date, dt_format)
  #return time_struct

def get_day(time_struct):
  return time.strftime("%A", time_struct)

def get_date(time_struct):
  return time.strftime("%m-%d-%y", time_struct)

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
  t[0] = t[0].strip()[0:5]
  t[1] = t[1].strip()[0:5]
  return t[0] + ' - ' + t[1]


def prepare_data(data_file1):
  f1 = open(data_file1, 'rU')
  reader1 = csv.reader(f1)
  
  p_id = 1
  
  reader1.next()
  
  t_schedule = {}
  for i, row in enumerate(reader1):
      
    type = unicode(row[1].decode("utf-8"))
      
    paper_id = i
    paper_title = unicode(row[2].decode("utf-8")).strip()
    new_title = unicode(row[16].decode("utf-8")).strip()
    if new_title:
        paper_title = new_title
    
    paper_authors = unicode(row[3].decode("utf-8")).strip()
    new_authors = unicode(row[14].decode("utf-8")).strip()
    if new_authors:
        paper_authors = new_authors
    
    chair = unicode(row[5].decode("utf-8"))
    
    if chair:
        session = unicode(row[4].decode("utf-8")) + ' - Chair: ' + chair
    else:
        session = unicode(row[4].decode("utf-8"))
    
    s_date = unicode(row[7].decode("utf-8"))
    
    s_time = unicode(row[8].decode("utf-8")) + '-' + unicode(row[9].decode("utf-8"))
    
    s_time = get_times(s_time)
    
    room = unicode(row[6].decode("utf-8"))
    
    paper_abstract = unicode(row[12].decode("utf-8"))
    
    keywords = unicode(row[10].decode("utf-8"))
    
    award_s = unicode(row[11].decode("utf-8"))
    hm = False
    
    if award_s.lower() == "hm":
        hm = True


    # prepare papers data
    papers[paper_id] = {
        'title': paper_title,
        'type': type,
        'hm': hm,
    }
    
    papers[paper_id]['abstract'] = paper_abstract
    papers[paper_id]['authors'] = [{'name': name.strip()} for name in paper_authors.split(',') if name.strip() != '']

    papers[paper_id]['keywords'] = [word for word in keywords.split(',') if word.strip() != '']
    
    # prepare sessions data
    s_id = construct_id(session)
    if(s_id in sessions):
      sessions[s_id]['submissions'].append(str(paper_id))
    else:
      sessions[s_id] = {
          'submissions': [str(paper_id)], 's_title': session, 'room': room, 'time': s_time, 'date': s_date}

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
