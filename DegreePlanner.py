import collections
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
                        tStr = tStr[:tStr.index('.')]
                        curList = []
                        while True:
                            left = 0
                            right = 0
                            try:
                                left = tStr.index('>')+1
                                print(tStr,'\n',tStr[left:]+'\n')
                                right = tStr[left:].index('<')
                            except ValueError:
                                print(curList,'\n\n')
                                item["prereqs"].append(dict(codes=curList))
                                break
                            if tStr[:left].find(')') is not -1:
                                print(curList,'\n\n')
                                item["prereqs"].append(dict(codes=curList))
                                curList = []
                            if tStr[:left].find('(') is not -1:
                                print(curList,'\n\n')
                                item["prereqs"].append(dict(codes=curList))
                                curList = []
                            elif tStr[:left].find('and') is not -1:
                                print(curList,'\n\n')
                                item["prereqs"].append(dict(codes=curList))
                                curList = []
                            if right > 4:
                                curList.append(tStr[left:left + right])
                            tStr = tStr[left+right+4:]
                    except ValueError:
                        print(traceback.format_exc())
                    try:
                        tStr = classStr[classStr.index("Corequisite"):]
                        tStr = tStr[:tStr.index('.')]
                        curList = []
                        while True:
                            left = 0
                            right = 0
                            try:
                                left = tStr.index('>')+1
                                print(tStr,'\n',tStr[left:]+'\n')
                                right = tStr[left:].index('<')
                            except ValueError:
                                print(curList,'\n\n')
                                item["coreqs"].append(dict(codes=curList))
                                break
                            if tStr[:left].find(')') is not -1:
                                print(curList,'\n\n')
                                item["coreqs"].append(dict(codes=curList))
                                curList = []
                            if tStr[:left].find('(') is not -1:
                                print(curList,'\n\n')
                                item["coreqs"].append(dict(codes=curList))
                                curList = []
                            elif tStr[:left].find('and') is not -1:
                                print(curList,'\n\n')
                                item["coreqs"].append(dict(codes=curList))
                                curList = []
                            if right > 4:
                                curList.append(tStr[left:left + right])
                            tStr = tStr[left+right+4:]
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

def findHours(code):
    for item in items:
        if item["code"] == code:
            return item["hours"]
    return int(code.split()[1][1])

def isCompleted(code):
    for item in items:
        if item["code"] == code:
            return item["completed"]
    return False

courseWeights = collections.defaultdict(int)
courseIDeps = collections.defaultdict(list)
courseDeps = collections.defaultdict(list)

def calculateWeight(code, deps):
    if isCompleted(code):
        #Hacky way to make them come first
        courseWeights[code]=1000
    deps.append(code)
    if courseWeights[code] > 0:
        return
    courseWeights[code] = findHours(code)
    for idep in courseIDeps[code]:
        if idep in deps:
            continue
        calculateWeight(idep, deps)
        courseWeights[code] += courseWeights[idep]

def sortGraph(items, edges):
    for item in items:
        courseIDeps[item["code"]] = []
        courseDeps[item["code"]] = []
        for edge in edges: 
            source = target = None
            if isinstance(edge[0], tuple):
                target = edge[0][1]
                source = edge[0][0]
            else:
                target = edge[1]
                source = edge[0]
                if target == item["code"] and source not in courseDeps[item["code"]]:
                    courseDeps[item["code"]].append(source)
            if source == item["code"] and target not in courseIDeps[item["code"]]:
                courseIDeps[item["code"]].append(target)
            if source not in courseDeps.keys():
                courseDeps[source] = []
            if target not in courseDeps.keys():
                courseDeps[target] = []
    for item in items:
        calculateWeight(item["code"], [])
        if item["completed"]:
            courseDeps[item["code"]] = []
    courseList = []
    while not (len(courseDeps.keys()) == 0):
        tList = []
        for code, deps in courseDeps.items():
            if deps == None:
                continue
            if len(deps) == 0 and (code not in courseList):
                tList.append(code)
        if len(tList) == 0:
            raise Exception("Infinite loop reached")
        tList.sort(key=(lambda x: courseWeights[x]), reverse=True)
        total = 0
        index = 0
        for code in tList:
            total += findHours(code)
            if total > 18:
                #print(total, ' ', code, ' ', tList[:index])
                break
            index += 1
            for key in courseDeps.keys():
                try:
                    courseDeps[key].remove(code)
                except:
                    continue
            courseDeps.pop(code)
        courseList.append(tList[:index])
    return courseList

START_SEMESTER = -1

def generateGraph(items):
    """
    Generates and renders a dependency graph for the class items being passed in
    TODO Handle equivalencies nicely, currently just ignoring
    TODO Generate subgraphs with same rank for semesters and have an invisible edge between them
         to force vertical alignment
    """
    nodes = []
    edges = []
    dot = Digraph(format="pdf",graph_attr = {"splines": "ortho", "autosize": "false", "size": "8.5,11", 
                                             "landscape": "true", "ratio": "compress", "fontsize": "32",
                                             "page": "8.5,11", "ranksep": "1.5 equally"})
    for item in items:
        if not item["completed"]:
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
                                                 "fillcolor": "gray", "style": "filled", "fontsize": "24", "height": "1.5",
                                                 "width": "8.5", "fixedsize": "shape"}))
                else:
                    nodes.append((item["code"], {"label": item["code"] + ' ' + item["name"] + '\n' +  item["description"] 
                                                                   + ' ' + str(item["hours"]) + " semester hours.",
                                                 "fontsize": "24", "height": "1.5", "width": "8.5", "fixedsize": "shape"}))
            else:
                if item["completed"]:
                    nodes.append((item["code"], {"label": item["code"] + ' ' + item["name"], "fillcolor": "gray",
                                                 "style": "filled", "fontsize": "24", "height": "1.5",
                                                 "width": "8.5", "fixedsize": "shape"}))
                else:
                    nodes.append((item["code"], {"label": item["code"] + ' ' + item["name"], "fontsize": "24", "height": "1.5",
                                                 "width": "8.5", "fixedsize": "shape"}))
    courseList = sortGraph(items, edges)
    for i,courses in enumerate(courseList):
        tNodes = []
        tDot = Digraph("cluster_"+str(i), graph_attr={"rank": "same", "label": "Semester "+str(i+START_SEMESTER), "style": "rounded", "penwidth": "3"})
        #tDot = Digraph(graph_attr={"rank": "same", "label": "Semester "+str(i+START_SEMESTER), "style": "rounded", "penwidth": "3"})
        for node in nodes:
            for course in courses:
                if course == node[0]:
                    tNodes.append(node)
        tDot = add_nodes(tDot, tNodes)
        dot.subgraph(tDot)
        print(i)
        if i > 0:
            edges.append(((courseList[i-1][0], courseList[i][0]), {"style": "invis", "weight": "100"}))
    dot = add_edges(dot, edges)
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
