import sys, json, csv, re, time
from collections import OrderedDict

papers_static = [{
    'id': 'Ind_101',
    'title': 'Data Processing at Facebook',
    'subtype': 'Industrial',
    'type': 'Industrial',
    'abstract': '',
    'authors': 'Guoqiang Jerry Chen (Facebook, Inc.); Janet L. Wiener (Facebook, Inc.); Shridhar Iyer (Facebook, Inc.); Anshul Jaiswal (Facebook, Inc.); Ran Lei Nikhil Simha (Facebook, Inc.); Wei Wang (Facebook, Inc.); Kevin Wilfong (Facebook, Inc.); Tim Williamson (Facebook, Inc.); Serhat Yilmaz (Facebook, Inc.)'
    },
    {
    'id': 'Ind_102',
    'title': 'Extracting Databases from Dark Data with DeepDive',
    'abstract': '',
    'subtype': 'Industrial',
    'type': 'Industrial',
    'authors': 'Ce Zhang (Stanford University); Jaeho Shin (Stanford University); Christopher Re (Stanford University); Michael Cafarella (University of Michigan Ann Arbor); Feng Niu (Lattice Data, Inc.)'
    },

    {
    'id': 'Ind_103',
    'title': 'Have Your Data and Query It Too: From Key-Value Caching to Big Data Management',
    'abstract': '',
    'subtype': 'Industrial',
    'type': 'Industrial',
    'authors': 'Dipti Borkar (Couchbase Inc.); Ravi Mayurum (Couchbase Inc.); Gerald Sangudi (Couchbase Inc.); Michael Carey (UCI/Couchbase Inc.)'
    },


    {
    'id': 'Ind_104',
    'title': 'Shasta: Interactive Reporting At Scale',
    'subtype': 'Industrial',
    'type': 'Industrial',
    'abstract': '',
    'authors': 'Gokul Nath Babu Manoharan (Google); Stephan Ellner (Google); Karl Schnaitter (Google); Sridatta Chegu (Google); Alejandro Estrella Balderrama (Google); Stephan Gudmundson (Google); Apurv Gupta (Google); Ben Handy (Google); Bart Samwel (Google); Chad Whipkey (Google); Larysa Aharkava (Google); Himani Apte (Google); Nitin Gangahar (Google); Jun Xu (Google); Shivakumar Venkataraman (Google); Divyakant Agrawal (Google/UCSB); Jeffrey D. Ullman (Stanford University)'
    },
  ]


def prepare_papers(data_file):
  papers_dict = dict()
  f = open(data_file, 'rU')
  reader = csv.reader(f)  
  reader.next()

  for row in reader:
    paper_id = unicode(row[0], "ISO-8859-1")
    paper_title = unicode(row[1], "ISO-8859-1").strip()
    paper_type = unicode(row[2], "ISO-8859-1").split(' ', 1)[0].strip()
    abstract = unicode(row[3], "ISO-8859-1")
    paper_authors = unicode(row[4], "ISO-8859-1")   
    

    # prepare papers data
    papers_dict[paper_id] = {
        'id': paper_id,
        'title': paper_title,
        'subtype': paper_type,
        'type': paper_type,
        'abstract': abstract,
        'authors': [{'name': authors.split(',', 1)[0].strip()} for authors in paper_authors.split(';')]
    }

  return papers_dict


def main():
  conf = sys.argv[2]
  data_file = sys.argv[1]
  papers_dict = prepare_papers(data_file)
  for paper in papers_static:
    papers_dict[paper['id']] = {
        'id': paper['id'],
        'title': paper['title'],
        'subtype': paper['subtype'],
        'type': paper['type'],
        'abstract': paper['abstract'],
        'authors': [{'name': authors.split('(', 1)[0].strip()} for authors in paper['authors'].split(';')]
    }
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
