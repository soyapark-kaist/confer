import sys, json, csv, re, time
from collections import OrderedDict

def prepare_papers(data_file):
  papers_dict = dict()
  f = open(data_file, 'rU')
  reader = csv.reader(f)  
  reader.next()

  for row in reader:
    paper_id = unicode(row[0], "ISO-8859-1")
    if u'SIGMOD' in paper_id.strip():
      paper_title = unicode(row[2], "ISO-8859-1").strip()
      paper_authors = unicode(row[3], "ISO-8859-1")   
    else:
      paper_title = unicode(row[3], "ISO-8859-1").strip()
      paper_authors = unicode(row[2], "ISO-8859-1")   
    #paper_type = unicode(row[2], "ISO-8859-1").split(' ', 1)[0].strip()
    paper_type = 'paper'
    abstract = unicode(row[4], "ISO-8859-1")    

    # prepare papers data
    papers_dict[paper_id] = {
        'id': paper_id,
        'title': paper_title,
        'subtype': paper_type,
        'type': paper_type,
        'abstract': abstract,
        'authors': [{'name': author.strip()} for author in re.split(r',|\sand\s', paper_authors)]
    }

  return papers_dict


def main():
  conf = sys.argv[2]
  data_file = sys.argv[1]
  papers_dict = prepare_papers(data_file)

  # write files
  papers_dict = OrderedDict(sorted(papers_dict.items(), key=lambda k: k[1]['title']))
  p = open('data/' + conf + '/papers.json','w')
  p.write(json.dumps(papers_dict, indent=2))
  p = open('server/static/conf/' + conf + '/data/papers.json','w')
  p.write('entities='+json.dumps(papers_dict, indent=2))
  #p = open('server/static/conf/' + conf + '/data/sessions.json','w')
  #p.write('sessions='+json.dumps(sessions, indent=2, sort_keys=True))
  #p = open('server/static/conf/' + conf +'/data/schedule.json','w')
  #p.write('schedule='+json.dumps(schedule, indent=2, sort_keys=True))
  

if __name__ == "__main__":
  main()
