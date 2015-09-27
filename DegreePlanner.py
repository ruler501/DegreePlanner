import copy
import html
import json
import sys
import traceback
import urllib3
from bs4 import BeautifulSoup
from graphviz import Digraph

#cat-reqi Actual Course/Item
#cat-reqa Header/Area
#cat-reqg Sub-Heading/Group

COURSE_CLASS = "cat-reqi"
HOURS_PREFIX = '<span class="course_hours">('

http = urllib3.PoolManager()

itemTemplate = {
        "name": "",
        "code": "",
        "description": "Testing Description but don't actually care",
        "hours": 0,
        "completed": False,
        "prereqs": [],
        "coreqs": [],
        "alternatives": [],
        "equivalencies": []
    }

items = []

def doesExist(code):
    for item in items:
        if item["code"] == code:
            return True
    return False

def addItem(item):
    if doesExist(item["code"]):
        #TODO Merge with the previous definition
        return
    items.append(item)

def addDegree(url):
    data = http.request('GET', url).data

    doc = BeautifulSoup(data, 'lxml')

    for link in doc.find_all('p'):
        try:
            if link['class'][0][:len(COURSE_CLASS)] == COURSE_CLASS:
                try:
                    item = copy.deepcopy(itemTemplate)
                    item["name"] = link.text[len(link.a.text)+1:]
                    item["code"] = link.a.text
                    classStr = html.unescape(link.a['title'])
                    item["hours"] = int(classStr[classStr.index(HOURS_PREFIX)+len(HOURS_PREFIX)])
                    try:
                        tStr = classStr[classStr.index("Prerequisite"):]
                        left = tStr.index('>')+1
                        right = tStr[left:].index('<')
                        if right > 4:
                            item["prereqs"].append(dict(codes=[tStr[left:left + right],]))
                    except ValueError:
                        pass
                    try:
                        tStr = classStr[classStr.index("Corequisite"):]
                        left = tStr.index('>')+1
                        right = tStr[left:].index('<')
                        if right > 4:
                            item["coreqs"].append(dict(codes=[tStr[left:left + right],]))
                    except ValueError:
                        pass
                    #TODO Implement adding of description 
                    addItem(item)
                except Exception as e:
                    print(traceback.format_exc())
        except KeyError:
            continue

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

INCLUDE_DESC = False

def generateGraph(items):
    """
    Generates and renders a dependency graph for the class items being passed in
    TODO Handle equivalencies nicely, currently just ignoring
    """
    nodes = []
    edges = []
    dot = Digraph()
    for item in items:
        for prereqs in item["prereqs"]:
            for prereq in prereqs["codes"]:
                edges.append((prereq, item["code"]))
        for coreqs in item["coreqs"]:
            for coreq in coreqs["codes"]:
                edges.append(((coreq, item["code"]), {"style": "dashed", "constraint": "false"}))
        found = False
        for node in nodes:
            if node[0] == item["code"]:
                found = True
        if not found:
            if INCLUDE_DESC:
                if item["completed"]:
                    nodes.append((item["code"], {"label": item["code"] + ' ' + item["name"] + '\n' +  item["description"] 
                                                                   + ' ' + str(item["hours"]) + " semester hours.",
                                                 "fillcolor": "gray", "style": "filled"}))
                else:
                    nodes.append((item["code"], {"label": item["code"] + ' ' + item["name"] + '\n' +  item["description"] 
                                                                   + ' ' + str(item["hours"]) + " semester hours."}))
            else:
                if item["completed"]:
                    nodes.append((item["code"], {"label": item["code"] + ' ' + item["name"], "fillcolor": "gray", "style": "filled"}))
                else:
                    nodes.append((item["code"], {"label": item["code"] + ' ' + item["name"]}))
    dot = add_edges(add_nodes(dot, nodes), edges)
    with open("DegreePlan.dot", 'w') as dotOut:
        print(dot.source, file=dotOut)
    dot.render(view=True)

if len(sys.argv) > 1:
    for url in sys.argv[1:]:
        addDegree(url)
    with open("DegreePlan.json", 'w') as dbOut:
        print(json.dumps(items, sort_keys=True, indent=4, separators=(',', ': ')), file=dbOut)
else:
    with open("DegreePlan.json", 'r') as dbIn:
        items = json.loads(dbIn.read())
generateGraph(items)
