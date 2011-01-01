#!/usr/bin/python

'''
Usage: main2.py marks-file.csv [sort]

Format of marks file:
ROLL,NAME,English:FA1:MARKS,English:FA1:MAX MARKS,English:FA2:MARKS,English:FA2:MAX MARKS,English:SA1:MARKS,English:SA1:MAX MARKS,Mathematics:FA1:MARKS,Mathematics:FA1:MAX MARKS,Mathematics:FA2:MARKS,Mathematics:FA2:MAX MARKS,Mathematics:SA1:MARKS,Mathematics:SA1:MAX MARKS,Social Science:FA1:MARKS,Social Science:FA1:MAX MARKS,Social Science:FA2:MARKS,Social Science:FA2:MAX MARKS,Social Science:SA1:MARKS,Social Science:SA1:MAX MARKS,Science:FA1:MARKS,Science:FA1:MAX MARKS,Science:FA2:MARKS,Science:FA2:MAX MARKS,Science:SA1:MARKS,Science:SA1:MAX MARKS,TAMIL:FA1:MARKS,TAMIL:FA1:MAX MARKS,TAMIL:FA2:MARKS,TAMIL:FA2:MAX MARKS,TAMIL:SA1:MARKS,TAMIL:SA1:MAX MARKS,FRENCH:FA1:MARKS,FRENCH:FA1:MAX MARKS,FRENCH:FA2:MARKS,FRENCH:FA2:MAX MARKS,FRENCH:SA1:MARKS,FRENCH:SA1:MAX MARKS,HINDI:FA1:MARKS,HINDI:FA1:MAX MARKS,HINDI:FA2:MARKS,HINDI:FA2:MAX MARKS,HINDI:SA1:MARKS,HINDI:SA1:MAX MARKS,SANSKRIT:FA1:MARKS,SANSKRIT:FA1:MAX MARKS,SANSKRIT:FA2:MARKS,SANSKRIT:FA2:MAX MARKS,SANSKRIT:SA1:MARKS,SANSKRIT:SA1:MAX MARKS,IT:FA1:MARKS,IT:FA1:MAX MARKS,IT:FA2:MARKS,IT:FA2:MAX MARKS,IT:SA1:MARKS,IT:SA1:MAX MARKS,Comp.Science:FA1:MARKS,Comp.Science:FA1:MAX MARKS,Comp.Science:FA2:MARKS,Comp.Science:FA2:MAX MARKS,Comp.Science:SA1:MARKS,Comp.Science:SA1:MAX MARKS
A-1,AAKASH DILIP KUMAR MEHTA,37,50,27,50,46,80,30,50,32,50,16,80,44,50,40,50,53,80,21,50,29,50,42,80,,,,,,,,,,,,,36,50,38,50,53,80,,,,,,,,,,,,,,,,,43,50
'''

import sys, csv, os.path, re, operator
from tornado import template

if len(sys.argv) < 2:
    print __doc__
    sys.exit(0)

# Load the data
infile = open(sys.argv[1])
title  = os.path.splitext(os.path.basename(sys.argv[1]))[0].replace('-', ' ')
exit
reader = csv.DictReader(infile)
students = list(reader)
fieldlist = reader.fieldnames[2:] # Ignore the first two. These should be "Name" and "Roll"
subjectlist = []
subjects = {}
tests = {}

grades=zip('A1 A2 B1 B2 C1 C2 D E1 E2'.split(), [90,80,70,60,50,40,32,20,-1])
def grade(item):
    if item['MAX MARKS'] > 0:
        mark = item['MARKS'] * 100.0 / item['MAX MARKS']
        for grade, floor in grades:
            if mark > floor: return grade
    else: return ''


# Compute student[] parameters
for student in students:
    percent_total = 0.0
    for item in fieldlist:
        subject, test, type = item.split(':')
        val = student[item] and float(student[item]) or 0.0

        if subject not in subjectlist: subjectlist.append(subject)

        sub = subjects.setdefault(subject, {})
        sub[test][type] = sub.setdefault(test, {}).get(type, 0) + val
        sub[type] = sub.setdefault(type, 0) + val

        studentsub = student.setdefault(subject, {})
        studentsub.setdefault(test, {})[type] = val
        studentsub[type] = val + studentsub.get(type, 0)

        testsub = tests.setdefault(subject, {})
        testsub[test] = 1

        del student[item]

# Post-computation
for subject in subjects:
    count = 0
    for student in students:
        if student[subject]['MAX MARKS'] > 0:
            g = grade(student[subject])
            subjects[subject][g] = subjects[subject].get(g, 0) + 1
            student[subject]['GRADE'] = g
            count += 1

            for test in tests[subject]:
                g = grade(student[subject][test])
                student[subject][test]['GRADE'] = g

    subjects[subject]['COUNT'] = count

loader = template.Loader(os.path.dirname(__file__))
outfile = re.sub(r'\W+', r'-', title).lower() + '.xhtml'
open(outfile, 'w').write(loader.load("dashboard2.html").generate(**globals()))
