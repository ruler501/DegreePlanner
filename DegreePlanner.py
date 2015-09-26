import urllib3
from bs4 import BeautifulSoup
from graphviz import Digraph

#cat-reqi Actual Course/Item
#cat-reqa Header/Area
#cat-reqg Sub-Heading/Group

COURSE_CLASS = "cat-reqi"

http = urllib3.PoolManager()
curURL = 'http://catalog.utdallas.edu/now/undergraduate/programs/jsom/business-administration'

data = ''#http.request('GET', curURL).data

doc = BeautifulSoup(data, 'html5lib')

for link in doc.find_all('p'):
    try:
        if link['class'][0][:len(COURSE_CLASS)] == COURSE_CLASS:
            print(link)
    except KeyError:
        continue

items = [{"name": "Testing", "code": "TEST 1010", "description": "We like testing new courses to BS freshman.", "hours": 0, 
          "prereqs": [{"name": "Freshman Seminar", "code": "UNIV 1010"}], 
          "coreqs": [{"name": "Discrete Math", "code": "CS 2305"}],
          "alternatives": [{"name": "Introduction to Business", "code": "BSN 1200"}],
          "equivalencies": [{"code": "ADV 1010"}]},]


def add_nodes(graph, nodes):
    for n in nodes:
        if isinstance(n, tuple):
            graph.node(n[0], **n[1])
        else:
            graph.node(n)
    return graph

def add_edges(graph, edges):
    for e in edges:
        if isinstance(e[0], tuple):
            graph.edge(*e[0], **e[1])
        else:
            graph.edge(*e)
    return graph

def generateGraph(items):
    nodes = []
    edges = []
    dot = Digraph(format='svg')
    for item in items:
        schools = []
        for equiv in item["equivalencies"]:
            schools.append(equiv["code"].split()[0])
        school, num = item["code"].split()
        schools.append(school)
        schools.sort()
        item["code"] = '/'.join(schools) + ' ' + num
        for prereq in item["prereqs"]:
            edges.append((prereq["code"], item["code"]))
        for coreq in item["coreqs"]:
            edges.append(((coreq["code"], item["code"]), {"style": "dashed"}))
        found = False
        for node in nodes:
            if node[0] == item["code"]:
                found = True
        if not found:
            nodes.append((item["code"], {"label": item["code"] + ' ' + item["name"] + '\n' +  item["description"] 
                                                               + ' ' + str(item["hours"]) + " semester hours."}))
    dot = add_edges(add_nodes(dot, nodes), edges)
    dot.render(view=True)

generateGraph(items)
