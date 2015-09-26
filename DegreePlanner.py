from bs4 import BeautifulSoup
import urllib

#cat-reqi Actual Course/Item
#cat-reqa Header/Area
#cat-reqg Sub-Heading/Group

COURSE_CLASS = "cat-reqi"

doc = BeautifulSoup(urllib.request.urlopen('http://catalog.utdallas.edu/now/undergraduate/programs/jsom/business-administration').read(), 'html5lib')
for link in doc.find_all('p'):
    if link['class'][0][:len(COURSE_CLASS)] == COURSE_CLASS:
        print(link)

