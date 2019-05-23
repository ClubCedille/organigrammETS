import os
import sys
import re
import PyPDF2
from graphviz import Digraph

BACHELORS = {
    '7622': 'Baccalauréat en génie de la construction',
    '7694': 'Baccalauréat en génie électrique',
    '7483': 'Baccalauréat en génie électrique',
    '7365': 'Baccalauréat en génie logiciel',
    '7684': 'Baccalauréat en génie mécanique',
    '7495': 'Baccalauréat en génie des opérations et de la logistique',
    '7610': 'Baccalauréat en génie des technologies de l\'information',
    '7485': 'Baccalauréat en génie de la production automatisée'
}


def parseCourses(index: int, pdf ):
    pattern = re.compile("\\s*(\\w{3}\\d{3})\\s*")
    lines = pdf.getPage(index).extractText().split("\n") 
    courses = {}
    for i, line in enumerate(lines):
        if pattern.match(line):
            courseName = pattern.findall(line)[0]
            depedencies = lines[i+3]

            if courseName:
                if pattern.match(depedencies):
                    courses[courseName] = courses.get(courseName, []) + pattern.findall(depedencies)
    return courses

def mergeCourses(courses1: dict, courses2: dict):
    courses = courses1.copy()

    for courseName, dependencies in courses2.items():
        courses[courseName] = list(set(dependencies + courses.get(courseName, [])))

    return courses

def getDotFile(courses):
    dotFile = Digraph(node_attr={'shape': 'rectangle', 'fillcolor':'#f8f8f8', 'style':'filled'}, edge_attr={'arrowhead':'vee'})
    for courseName, dependencies in courses.items():
        for dependency in dependencies:
            dotFile.edge(dependency, courseName)
    
    return dotFile

def run():
    argsLen = len(sys.argv)
    if argsLen  > 1:
        for fileIndex in range(1, argsLen):
            filePath = sys.argv[fileIndex]
            if os.path.isfile(filePath): 
                file = open(filePath, 'rb')
                pdf = PyPDF2.PdfFileReader(file)
                bachelorCode = file.name[-8:-4] # Find the four digit int the PDF name
                
                courses = {}
                
                for pageIndex in range(0, pdf.getNumPages()):
                    courses = mergeCourses(courses, parseCourses(pageIndex, pdf))

                dot = getDotFile(courses)
                dot.graph_attr = {'label':BACHELORS[bachelorCode]}
                #Generate the dot file then the SVG
                dot.render('graph/'+bachelorCode, view=False, cleanup=True, format='svg')
            else:
                print('File: {} is not found'.format(filePath))

    else:
        print('Usage: python organigrammETS.py [file1] [file2] [file3] ...')

run()