from bs4 import BeautifulSoup
import urllib3

#cat-reqi Actual Course/Item
#cat-reqa Header/Area
#cat-reqg Sub-Heading/Group

COURSE_CLASS = "cat-reqi"

http = urllib3.PoolManager()
curURL = 'http://catalog.utdallas.edu/now/undergraduate/programs/jsom/business-administration'

data = http.request('GET', curURL).data

doc = BeautifulSoup(data, 'html5lib')

for link in doc.find_all('p'):
    try:
        if link['class'][0][:len(COURSE_CLASS)] == COURSE_CLASS:
            print(link)
    except KeyError:
        continue
