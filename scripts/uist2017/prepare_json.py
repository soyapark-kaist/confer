import sys, json, csv, re, time

papers = {}
sessions = {}
schedule = []

dt_format='%m/%d'

def construct_id(s):
  return re.sub(r'\W+', '_', s)

def get_start_time(s_time):
  date = time.strptime(s_time, '%I:%M:%S %p')
  s = time.strftime("%H", date)
  t = time.strftime("%M", date)
  val = float(s + '.' + t)
  return val

def get_date_time(s_date, dt_format='%m/%d'):
  s_date = s_date + '/2017'
  return time.strptime(s_date, '%m/%d/%Y')

def get_day(time_struct):
  return time.strftime("%A", time_struct)

def get_date(time_struct):
  return time.strftime("%m/%d", time_struct)

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
    s_date = unicode(row[1], "ISO-8859-1")
    s_time = unicode(row[4], "ISO-8859-1")

    session = unicode(row[3], "ISO-8859-1")
    #session_chair = unicode(row[7], "ISO-8859-1")
    
    if not s_time:
        continue
    
    paper_abstract = unicode(row[269], "ISO-8859-1")
    paper_abstract = re.sub('\\\\', '', paper_abstract)
    
    paper_authors = ''
    for i in range(29,269,15):
        if row[i]:
            first_name = row[i+1].title()
            middle = row[i+2].title()
            last = row[i+3].title()
            aff = row[i+6]
            if aff.lower() == "graduate school" or aff == "University" or aff == "4-21-1,Nakano,":
                aff = row[i+5]
            if aff == "Massachusetts Institute of Technology":
                aff = "MIT"
            if aff == "University of California, San Diego":
                aff = "UC San Diego"
            if aff == "KYUNG HEE UNIVERSITY":
                aff = "Kyung Hee University"
            if aff == "Palo Alto":
                aff = "Stanford University"
            if aff == "Boston":
                aff = "Wentworth Institute of Technology"
            if aff == "Montreal":
                aff = "McGill University"
            if aff == "Computer Scienve and Technology":
                aff = "Zhejiang University"
            if aff == "West Lafayette":
                aff = "Purdue University"
            if aff == "Daejeon":
                aff = "KAIST"
            if 'Telecom ParisTech' in aff:
                aff = "Telecom ParisTech"
            if aff == "CSAIL":
                aff = "MIT"
            if aff == "Stanford":
                aff = "Stanford University"
            if aff == "Los Angeles":
                aff = "I.AM+"
            if "Adobe" in aff:
                aff = "Adobe Research"
            if "TSUKUBA" in aff:
                aff = "University of Tsukuba"
            if aff == "KAIST (Korea Advanced Institute of Science and Technology)":
                aff = 'KAIST'
            
            
            if aff:
                paper_authors += first_name + ' ' + middle + ' ' + last + ', ' + aff + '\t'
            else:
                paper_authors += first_name + ' ' + middle + ' ' + last + '\t'
        else:
            break
    

    type = "paper"
    
    award_s = unicode(row[14], "ISO-8859-1")
    award = False
    hm = False
    
    if award_s.lower() == "honorable mention":
        hm = True

    if award_s.lower() == "best paper":
        award = True 
 
    paper_title = unicode(row[18], "ISO-8859-1")

    if paper_title:
        # prepare papers data
        papers[paper_id] = {
            'title': paper_title,
            'subtype':type,
            'type': type,
            'award': award,
            'hm': hm}
        
        papers[paper_id]['abstract'] = paper_abstract
        papers[paper_id]['authors'] = [{'name': name.strip()} for name in paper_authors.split('\t') if name.strip() != '']
        print papers[paper_id]['authors']
    
    # prepare sessions data
    s_id = row[2]
    if not s_id:
        s_id = row[0]
        #s_id = construct_id(session)
        if(s_id not in sessions):
          sessions[s_id] = {
              'submissions': [], 's_title': session, 'time': s_time, 'date': s_date}
        
    else:
        if(s_id in sessions):
          sessions[s_id]['submissions'].append(paper_id)
        else:
          sessions[s_id] = {
              'submissions': [paper_id], 's_title': session, 'time': s_time, 'date': s_date}

    p_id += 1

  # prepare schedule data
  for session in sessions:
    s_info = sessions[session]
    s_date = s_info['date']
    s_time = s_info['time']
    s_data = {'session': session}
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
