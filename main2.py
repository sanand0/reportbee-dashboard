#!/usr/bin/python

'''
Usage: main2.py marks-file.csv [sort]

Format of marks file:
ROLL,NAME,English:FA1:MARKS,English:FA1:MAX MARKS,English:FA2:MARKS,English:FA2:MAX MARKS,English:SA1:MARKS,English:SA1:MAX MARKS,Mathematics:FA1:MARKS,Mathematics:FA1:MAX MARKS,Mathematics:FA2:MARKS,Mathematics:FA2:MAX MARKS,Mathematics:SA1:MARKS,Mathematics:SA1:MAX MARKS,Social Science:FA1:MARKS,Social Science:FA1:MAX MARKS,Social Science:FA2:MARKS,Social Science:FA2:MAX MARKS,Social Science:SA1:MARKS,Social Science:SA1:MAX MARKS,Science:FA1:MARKS,Science:FA1:MAX MARKS,Science:FA2:MARKS,Science:FA2:MAX MARKS,Science:SA1:MARKS,Science:SA1:MAX MARKS,TAMIL:FA1:MARKS,TAMIL:FA1:MAX MARKS,TAMIL:FA2:MARKS,TAMIL:FA2:MAX MARKS,TAMIL:SA1:MARKS,TAMIL:SA1:MAX MARKS,FRENCH:FA1:MARKS,FRENCH:FA1:MAX MARKS,FRENCH:FA2:MARKS,FRENCH:FA2:MAX MARKS,FRENCH:SA1:MARKS,FRENCH:SA1:MAX MARKS,HINDI:FA1:MARKS,HINDI:FA1:MAX MARKS,HINDI:FA2:MARKS,HINDI:FA2:MAX MARKS,HINDI:SA1:MARKS,HINDI:SA1:MAX MARKS,SANSKRIT:FA1:MARKS,SANSKRIT:FA1:MAX MARKS,SANSKRIT:FA2:MARKS,SANSKRIT:FA2:MAX MARKS,SANSKRIT:SA1:MARKS,SANSKRIT:SA1:MAX MARKS,IT:FA1:MARKS,IT:FA1:MAX MARKS,IT:FA2:MARKS,IT:FA2:MAX MARKS,IT:SA1:MARKS,IT:SA1:MAX MARKS,Comp.Science:FA1:MARKS,Comp.Science:FA1:MAX MARKS,Comp.Science:FA2:MARKS,Comp.Science:FA2:MAX MARKS,Comp.Science:SA1:MARKS,Comp.Science:SA1:MAX MARKS
A-1,AAKASH DILIP KUMAR MEHTA,37,50,27,50,46,80,30,50,32,50,16,80,44,50,40,50,53,80,21,50,29,50,42,80,,,,,,,,,,,,,36,50,38,50,53,80,,,,,,,,,,,,,,,,,43,50
'''

import sys, csv, os.path, re, operator, random
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

gradelist =             'A1 A2 B1 B2 C1 C2 D  E1 E2'.split()
grades = zip(gradelist, [90,80,70,60,50,40,32,20,-0.0001])
def grade(item):
    if item['MAX MARKS'] > 0:
        mark = item['MARKS'] * 100.0 / item['MAX MARKS']
        for grade, floor in grades:
            if mark > floor: return grade
    else: return ''

def slugify(s): return re.sub(r'[^A-Za-z0-9_]+', '-', s)

def jitter(student, subject):
    pc = student[subject]['PERCENTILE']
    mindiffs = [subject]
    for sub in subjectlist:
        if sub != subject and student[sub]['MAX MARKS'] > 0:
            if abs(student[sub]['PERCENTILE'] - pc) < 0.05:
                mindiffs.append(sub)
    mindiffs.sort()
    j = 0.5
    if len(mindiffs) > 1:
        j = float(mindiffs.index(subject)) / (len(mindiffs)-1)
    return (j-0.5)*8


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

        testsub = tests.setdefault(subject, [])
        if test not in testsub: testsub.append(test)

        del student[item]

# Post-computation
for subject in subjects:
    count = 0
    max_marks = max(x[subject]['MARKS'] for x in students)
    min_marks = min(x[subject]['MARKS'] for x in students)
    range_marks = max_marks - min_marks
    for student in students:
        if student[subject]['MAX MARKS'] > 0:
            g = grade(student[subject])
            subjects[subject][g] = subjects[subject].get(g, 0) + 1
            student[subject]['GRADE'] = g
            count += 1

            pc = dict([(test, student[subject][test]['MARKS'] / student[subject][test]['MAX MARKS']) for test in tests[subject] if student[subject][test]['MAX MARKS'] > 0])
            pcmin = min(pc.values()) - 0.05
            pcrange = max(pc.values()) - pcmin + 0.01
            for test in tests[subject]:
                g = grade(student[subject][test])
                student[subject][test]['GRADE'] = g
                if student[subject][test]['MAX MARKS'] > 0:
                    student[subject][test]['BARHEIGHT'] = (pc[test] - pcmin) / pcrange

        student[subject]['PERCENTILE'] = (student[subject]['MARKS'] - min_marks) / range_marks if range_marks > 0 else 0.5

    subjects[subject]['COUNT'] = count

subjectlist = [x for x in subjectlist if subjects[x]['MAX MARKS'] > 0]

loader = template.Loader(os.path.dirname(__file__))
outfile = re.sub(r'\W+', r'-', title).lower() + '.xhtml'
open(outfile, 'w').write(loader.load("dashboard2.html").generate(**globals()))
