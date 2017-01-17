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
  if s_date == "Monday":
      return time.strptime('04/11/2016', dt_format)
  if s_date == "Tuesday":
      return time.strptime('04/12/2016', dt_format)
  if s_date == "Wednesday":
      return time.strptime('04/13/2016', dt_format)
  if s_date == 'Thursday':
      return time.strptime('04/14/2016', dt_format)
  if s_date == 'Friday':
      return time.strptime('04/15/2016', dt_format)     


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

def prepare_data(data_file1):
  f1 = open(data_file1, 'rU')
  reader1 = csv.reader(f1)
  
  p_id = 1
  
  reader1.next()
  
  t_schedule = {}
  
  curr_s_time = ''
  
  for row in reader1:
    paper_id = unicode(row[1], "ISO-8859-1")
    s_date = unicode(row[4], "ISO-8859-1")
    s_time = unicode(row[6], "ISO-8859-1")

    session = unicode(row[7], "ISO-8859-1")
    
    if row[5].strip() != '':
        curr_s_time = unicode(row[5], "ISO-8859-1")
    
    paper_authors = unicode(row[3], "ISO-8859-1")
    paper_title = unicode(row[2], "ISO-8859-1")
    
    room = unicode(row[9], "ISO-8859-1")
    print room
    abstract = unicode(row[11], "ISO-8859-1")
    
    type = unicode(row[0], "ISO-8859-1")
    if type == 'R':
        type = 'paper'
    elif type == 'W':
        type = 'workshop'
    elif type == 'T':
        type = 'tutorial'
    elif type == 'I':
        type = 'Industry Session'
    elif type == 'P':
        type = "PhD Symposium"

    # prepare papers data
    papers[paper_id] = {
        'title': paper_title,
        'subtype':type,
        'type': type,
        'abstract': abstract}


    papers[paper_id]['authors'] = []
    
    for name in paper_authors.strip('"').split(','):
        if name.strip() != '':
            
            if 'and' in name or 'And' in name:
                if ' and' in name:
                    names = name.strip().split(' and ')
                    for n in names:
                        n = re.sub('\.','', n)
                        papers[paper_id]['authors'].append({'name': n.strip()})
                elif ' And' in name:
                    names = name.strip().split(' And ')
                    for n in names:
                        n = re.sub('\.','', n)
                        papers[paper_id]['authors'].append({'name': n.strip()})
            else:
                papers[paper_id]['authors'].append({'name': name.strip()})
    
     


    
    # prepare sessions data
    s_id = construct_id(session)
    if(s_id in sessions):
      sessions[s_id]['submissions'].append(paper_id)
    else:
      sessions[s_id] = {
          'submissions': [paper_id], 's_title': session, 'room': room, 'time': curr_s_time, 'date': s_date}

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
