#!/usr/bin/python

# This is used to generate student report visualisations shown at the
# [Reportbee blog](http://blog.reportbee.com/visualising-student-performance-2)
#
# The data must be in the format shown here:

'''
Usage: main2.py marks-file.csv [sort]

Format of marks file:
ROLL,NAME,English:FA1:MARKS,English:FA1:MAX MARKS,English:FA2:MARKS,English:FA2:MAX MARKS,English:SA1:MARKS,English:SA1:MAX MARKS,Mathematics:FA1:MARKS,Mathematics:FA1:MAX MARKS,Mathematics:FA2:MARKS,Mathematics:FA2:MAX MARKS,Mathematics:SA1:MARKS,Mathematics:SA1:MAX MARKS,Social Science:FA1:MARKS,Social Science:FA1:MAX MARKS,Social Science:FA2:MARKS,Social Science:FA2:MAX MARKS,Social Science:SA1:MARKS,Social Science:SA1:MAX MARKS,Science:FA1:MARKS,Science:FA1:MAX MARKS,Science:FA2:MARKS,Science:FA2:MAX MARKS,Science:SA1:MARKS,Science:SA1:MAX MARKS,TAMIL:FA1:MARKS,TAMIL:FA1:MAX MARKS,TAMIL:FA2:MARKS,TAMIL:FA2:MAX MARKS,TAMIL:SA1:MARKS,TAMIL:SA1:MAX MARKS,FRENCH:FA1:MARKS,FRENCH:FA1:MAX MARKS,FRENCH:FA2:MARKS,FRENCH:FA2:MAX MARKS,FRENCH:SA1:MARKS,FRENCH:SA1:MAX MARKS,HINDI:FA1:MARKS,HINDI:FA1:MAX MARKS,HINDI:FA2:MARKS,HINDI:FA2:MAX MARKS,HINDI:SA1:MARKS,HINDI:SA1:MAX MARKS,SANSKRIT:FA1:MARKS,SANSKRIT:FA1:MAX MARKS,SANSKRIT:FA2:MARKS,SANSKRIT:FA2:MAX MARKS,SANSKRIT:SA1:MARKS,SANSKRIT:SA1:MAX MARKS,IT:FA1:MARKS,IT:FA1:MAX MARKS,IT:FA2:MARKS,IT:FA2:MAX MARKS,IT:SA1:MARKS,IT:SA1:MAX MARKS,Comp.Science:FA1:MARKS,Comp.Science:FA1:MAX MARKS,Comp.Science:FA2:MARKS,Comp.Science:FA2:MAX MARKS,Comp.Science:SA1:MARKS,Comp.Science:SA1:MAX MARKS
A-1,AAKASH DILIP KUMAR MEHTA,37,50,27,50,46,80,30,50,32,50,16,80,44,50,40,50,53,80,21,50,29,50,42,80,,,,,,,,,,,,,36,50,38,50,53,80,,,,,,,,,,,,,,,,,43,50
'''

import sys, csv, os.path, re, operator, random

# Tornado templates are used to generate the output
from tornado import template

# If no command line arguments are given, print the docstring as help
if len(sys.argv) < 2:
    print __doc__
    sys.exit(0)

# Load the data
# -------------

# Load the data from the first command line argument
infile = open(sys.argv[1])

# The title is the filename, with spaces replaced by hyphens
title  = os.path.splitext(os.path.basename(sys.argv[1]))[0].replace('-', ' ')

# Read the file as a CSV file, with the first column as headers
reader = csv.DictReader(infile)
students = list(reader)

# Get the fieldnames, ignoring the first two ("Roll" and "Name")
fieldlist = reader.fieldnames[2:]

subjectlist = []
subjects = {}
sections = {}
tests = {}

# Define useful functions
# -----------------------

# The `grade()` function returns the grade given a percentage
# See the last page of [CBSE's Certificate](http://www.cbse.nic.in/cce/CCE%20Certificate-2009-11-A3%20size%20(Coloured)-13-10-2010.pdf) (PDF)
gradelist =             'A1 A2 B1 B2 C1 C2 D  E1 E2'.split()
grades = zip(gradelist, [90,80,70,60,50,40,32,20,-0.0001])
def grade(item):
    if item['MAX MARKS'] > 0:
        mark = item['MARKS'] * 100.0 / item['MAX MARKS']
        for grade, floor in grades:
            if mark > floor: return grade
    else: return ''

# `slugify` is a utility used by the template to convert subject names
# to HTML-safe class names
def slugify(s): return re.sub(r'[^A-Za-z0-9_]+', '-', s)

# We plot student's as circles along a horizontal line.
# Sometimes, these circles overlap if the marks are close enough.
# We can overcome this by moving them a bit, vertically.
# `jitter` returns a number indicating how much to move vertically
def jitter(student, subject):
    # Get the percentage
    pc = student[subject]['PERCENTILE']

    # Collect all subjects with a difference of within 5% from the subject
    mindiffs = [subject]
    for sub in subjectlist:
        if sub != subject and student[sub]['MAX MARKS'] > 0:
            if abs(student[sub]['PERCENTILE'] - pc) < 0.05:
                mindiffs.append(sub)

    # Sort the subjects alphabetically (to get a stable order).
    # Just use the subject's position in the list as the jitter factor.
    # This isn't the best jitter possible. Ideally, closer items would get
    # a bigger jitter, but getting a stable algorithm (i.e. one that returns
    # the same result for a subject irrespective of neighbours) need thought.
    mindiffs.sort()
    j = 0.5
    if len(mindiffs) > 1:
        j = float(mindiffs.index(subject)) / (len(mindiffs)-1)
    return (j-0.5)

# `percentile` takes an array of scores and returns the percentiles of each.
# We use [percentile](http://en.wikipedia.org/wiki/Percentile#Nearest_rank) =
# [Fractional rank](http://en.wikipedia.org/wiki/Ranking#Fractional_ranking_.28.221_2.5_2.5_4.22_ranking.29)
# divided by number of students.
def percentile(scores):
    total = {}  # sum of ranks of all students with a given score
    count = {}  # number of students with a given score
    for i, score in enumerate(sorted(scores)):
        total[score] = total.get(score, 0) + i
        count[score] = count.get(score, 0) + 1

    fractional_ranks = [float(total[score]) / count[score] for score in scores]

    # We make one modification to this, however.
    # We scale it so that the lowest score always gets 0, and highest gets 1
    min_rank = min(fractional_ranks)
    range_rank = max(fractional_ranks) - min_rank
    return [(x - min_rank) / range_rank for x in fractional_ranks]

# Calculate statistics
# --------------------

# Compute student properties. TODO: documentation
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

# Post-computation. TODO: documentation
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

            section = student['ROLL'][0]
            sections.setdefault(section, {}).setdefault(subject, {})
            sections[section][subject][g] = sections[section][subject].get(g, 0) + 1
            sections[section][subject]['MARKS'] = sections[section][subject].get('MARKS', 0) + student[subject]['MARKS']
            sections[section][subject]['MAX MARKS'] = sections[section][subject].get('MAX MARKS', 0) + student[subject]['MAX MARKS']

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

# Generate the template
# ---------------------

loader = template.Loader(os.path.dirname(__file__))
outfile = re.sub(r'\W+', r'-', title).lower() + '.xhtml'

# If we have multiple sections, generate using a multi-section template.
# Otherwise, just use the regular single-section template
tmpl = len(sections) > 1 and 'multisection.html' or 'dashboard2.html'
open(outfile, 'w').write(loader.load(tmpl).generate(**globals()))
