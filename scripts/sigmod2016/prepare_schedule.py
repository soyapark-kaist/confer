import sys, json, csv, re, time
from collections import OrderedDict

sessions_dict = [
  {"Scalable Analytics &amp; Machine Learning":{"papers":["402","420","916","421","919","369","937"], 'day': 'Tuesday', 'time': '10:30-12:15', 'Room': 'Grand Ballroom B'
}},
  {"Privacy &amp; Security":{"papers":["935","983","392","388","393","367","424"], 'day': 'Tuesday', 'time': '10:30-12:15', 'Room': 'Grand Ballroom C'}},
  {"Logical and Physical Database Design":{"papers":["900","874","Ind_103","892","971","426","383"], 'day': 'Tuesday', 'time': '10:30-12:15', 'Room': 'Seacliffs'}},
  {"New Storage and Network Architectures":{"papers":["384","943","365","416","990","375"], 'day': 'Tuesday', 'time': '13:30-15:00', 'Room': 'Grand Ballroom B'}},
  {"Graphs 1: Infrastructure and Processing on Modern Hardware":{"papers":["429","418","933","924","970","401"], 'day': 'Tuesday', 'time': '13:30-15:00', 'Room': 'Grand Ballroom C'}},
  {"Streaming 1: Systems and Outlier Detection":{"papers":["413","984","379","408","195","692"], 'day': 'Tuesday', 'time': '13:30-15:00', 'Room': 'Seacliffs'}},
  {"Approximate Query Processing":{"papers":["407","965","404","363","959","988"], 'day': 'Wednesday', 'time': '8:30-10:00', 'Room': 'Grand Ballroom B'}},
  {"Networks and the Web":{"papers":["927","989","432","390","889","934"], 'day': 'Wednesday', 'time': '8:30-10:00', 'Room': 'Grand Ballroom C'}},
  {"Data Discovery and Extraction":{"papers":["873","890","922","422","Ind_102","364"], 'day': 'Wednesday', 'time': '8:30-10:00', 'Room': 'Seacliffs'}},
  {"Data Integration / Cleaning":{"papers":["423","975","963","309","987","926","991"], 'day': 'Wednesday', 'time': '10:30-12:15', 'Room': 'Grand Ballroom B'}},
  {"Spatio / Temporal Databases":{"papers":["380","882","982","368","434","430","968"], 'day': 'Wednesday', 'time': '10:30-12:15', 'Room': 'Grand Ballroom C'}},
  {"Careers in Industry Panel":{'day': 'Wednesday', 'time': '10:30-12:15', 'Room': 'Seacliffs'}},
  {"Distributed Data Processing":{"papers":["Ind_101","899","901","928","958","381"], 'day': 'Wednesday', 'time': '13:30-15:00', 'Room': 'Grand Ballroom B'}},
  {"Graphs 2: Subgraph-based Optimization Techniques":{"papers":["936","394","967","400","929","954"], 'day': 'Wednesday', 'time': '13:30-15:00', 'Room': 'Grand Ballroom C'}},
  {"Main Memory Analytics":{"papers":["925","102","872","885","961","504"], 'day': 'Wednesday', 'time': '13:30-15:00', 'Room': 'Seacliffs'}},
  {"Interactive Analytics":{"papers":["411","972","378","930","Ind_104","898"], 'day': 'Thursday', 'time': '10:30-12:00', 'Room': 'Grand Ballroom B'}},
  {"Streaming 2: Sketches":{"papers":["412","373","414","956","949","951"], 'day':'Thursday', 'time': '10:30-12:00', 'Room': 'Grand Ballroom C'}},
  {"Transaction Processing":{"papers":["377","839","955","947","428","940"], 'day':'Thursday', 'time': '10:30-12:00', 'Room': 'Seacliffs'}},
  {"Transactions and Consistency":{"papers":["419","397","395","382","173","921"], 'day':'Thursday', 'time': '13:30-15:00', 'Room': 'Grand Ballroom B'}},
  {"Query Optimization":{"papers":["932","370","387","870","974","386"], 'day':'Thursday', 'time': '13:30-15:00', 'Room': 'Grand Ballroom C'}},
  {"Graphs 3: Potpourri &nbsp;":{"papers":["946","945","436","962","976","410"], 'day':'Thursday', 'time': '13:30-15:00', 'Room': 'Seacliffs'}},
  {"Hardware Acceleration &amp; Query Compilation":{"papers":["399","977","883","950","887","376"], 'day':'Thursday', 'time': '15:00-17:00', 'Room': 'Grand Ballroom B'}},
  {"Nearest Neighbors and Similarity Search":{"papers":["406","931","985","391","435","964"], 'day':'Thursday', 'time': '15:00-17:00', 'Room': 'Grand Ballroom C'}}
]

sessions = {}
schedule = []


def construct_id(s):
  return re.sub(r'\W+', '_', s)

def get_start_time(s_time):
  s = s_time.split('-')[0].strip()
  return int(re.match(r'\d+', s).group())
  return s

def get_date_time(s_date, dt_format='%m/%d/%Y'):
  if s_date == "Monday":
    return time.strptime('06/27/2016', dt_format)
  if s_date == "Tuesday":
    return time.strptime('06/28/2016', dt_format)
  if s_date == "Wednesday":
    return time.strptime('06/29/2016', dt_format)
  if s_date == 'Thursday':
    return time.strptime('06/30/2016', dt_format)
  if s_date == 'Friday':
    return time.strptime('07/01/2016', dt_format)     


def get_day(time_struct):
  return time.strftime("%A", time_struct)

def get_date(time_struct):
  return time.strftime("%m/%d/%Y", time_struct)

def get_time(time_struct):
  return time.strftime("%H:%M", time_struct)

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

def prepare_sessions():
  t_schedule = {}
  for s in sessions_dict:
    for k, v in s.iteritems():
      print k, v
      s_id = construct_id(k)
      sessions[s_id] = {
        's_title': k,
        'submissions': v['papers'] if 'papers' in v else [],
        'day': v['day']
      }
      s_data = {'session': s_id, 'room': v['Room']}
      s_date = get_date_time(v['day'])
      s_time = v['time']

      if s_date in t_schedule:
        if s_time in t_schedule[s_date]:
          t_schedule[s_date][s_time]['sessions'].append(s_data)
        else:
          t_schedule[s_date][s_time] = {'time': s_time, 'sessions':[s_data] }
      else:
        t_schedule[s_date] =  {s_time: {'time': s_time, 'sessions':[s_data]}}

  for s_date in t_schedule:
    t_schedule[s_date] = sorted(
      t_schedule[s_date].items(), key = lambda x: get_start_time(x[0]))
  
  t_schedule = sorted(t_schedule.items(), key=lambda x: x[0])
  for day_schedule in t_schedule:
    slots = []
    s_date = get_date(day_schedule[0])
    s_day = get_day(day_schedule[0])
    all_slots = day_schedule[1]
    for slot_info in all_slots:
      slot_time = slot_info[0]
      slot_sessions = slot_info[1]['sessions']
      slots.append({
        'time': slot_time,
        'sessions': slot_sessions,
        'slot_class': get_class(slot_time),
        'slot_id': construct_id(s_date + '_' + slot_time)
      })
      print(slots)
    schedule.append({'date': s_date, 'slots': slots, 'day': s_day})


def main():
  conf = sys.argv[1]
  prepare_sessions()
  
  # write files
  p = open('server/static/conf/' + conf + '/data/sessions.json','w')
  p.write('sessions='+json.dumps(sessions, indent=2, sort_keys=True))
  p = open('server/static/conf/' + conf +'/data/schedule.json','w')
  p.write('schedule='+json.dumps(schedule, indent=2, sort_keys=True))
  

if __name__ == "__main__":
  main()
