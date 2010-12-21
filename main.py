#!/usr/bin/python

'''
Usage: main.py marks-file.csv [sort]

Format of marks file:
Roll,Name,English,Mathematics,Social Science,Science,Tamil,French,Hindi,Sanskrit,IT,CompScience
A-1,ABHIJIT P,120/200,106/180,123/200,139/200,0/0,0/0,149/200,0/0,0/0,35/50
'''

import sys, csv, os.path, re, operator
from tornado import template

if len(sys.argv) < 2:
    print __doc__
    sys.exit(0)

# Load the data
infile = open(sys.argv[1])
title  = infile.readline().replace(',', '').strip()
reader = csv.DictReader(infile)
students = list(reader)
subjects = {}
subjectlist = reader.fieldnames[2:] # Ignore the first two. These should be "Name" and "Roll"


# Compute student[] parameters
for row in students:
    percent_total = 0.0
    for subject, value in row.iteritems():
        if value.find('/') > 0:
            marks, total = (float(x) for x in value.split('/'))
            row[subject] = {'marks': marks, 'total': total, 'percent': marks/total if total > 0 else 0 }
            percent_total += marks/total if total > 0 else 0
            subjects.setdefault(subject, {})
            if subjects[subject].setdefault('total', 0) < total:
                subjects[subject]['total'] = total
    row.setdefault('percentile', {})
    row.setdefault('percent', percent_total)

if len(sys.argv) > 2:
    if sys.argv[2] == 'sort':
        students = sorted(students, key=operator.itemgetter('percent'), reverse=True)

# Compute subject[] parameters
for subject in subjects:
    sorted_data = [row for row in sorted(students, key=lambda x: x[subject]['percent']) if row[subject]['total'] > 0]
    sorted_marks = [row[subject]['percent'] for row in sorted_data]
    subjects[subject].update({
        'min'   : min(sorted_marks)                     if sorted_marks else 0,
        'q1'    : sorted_marks[1*len(sorted_marks)/4]   if sorted_marks else 0,
        'q2'    : sorted_marks[2*len(sorted_marks)/4]   if sorted_marks else 0,
        'q3'    : sorted_marks[3*len(sorted_marks)/4]   if sorted_marks else 0,
        'mean'  : sum(sorted_marks)/len(sorted_marks)   if sorted_marks else 0,
        'max'   : max(sorted_marks)                     if sorted_marks else 0,
        'hist'  : [0]*20
    })
    for percent in sorted_marks:
        subjects[subject]['hist'][int(percent*20-0.5)] += 1

    l = len(sorted_data)
    for i, row in enumerate(sorted_data):
        row['percentile'][subject] = float(i)/(l-1) if row[subject]['total'] and (l > 1) else -1

    max_hist = max(subjects[subject]['hist'])
    subjects[subject]['hist'] = [float(x)/max_hist if max_hist > 0 else 0 for x in subjects[subject]['hist']]

# Compute correlations
# TODO: Change this to spearman r instead of pearson r
def correlation(vx, vy):
    n = len(vx)
    xy, xx, yy, x, y = 0, 0, 0, 0, 0
    for i in xrange(0,n):
        x += vx[i]
        y += vy[i]
        xy += vx[i] * vy[i]
        xx += vx[i] * vx[i]
        yy += vy[i] * vy[i]
    d = (n*xx - x*x)*(n*yy - y*y)
    return (n*xy - x*y)/d**0.5 if d > 0 else 1.0

cor = {}
for subject1 in subjectlist:
    cor[subject1] = {}
    for subject2 in subjectlist:
        if subject1 != subject2:
            # TODO: Change this to use percentrank instead
            vx = [row[subject1]['percent'] for row in students if row[subject1]['total'] > 0 and row[subject2]['total'] > 0]
            vy = [row[subject2]['percent'] for row in students if row[subject1]['total'] > 0 and row[subject2]['total'] > 0]
            c = cor[subject1][subject2] = correlation(vx, vy)

loader = template.Loader(os.path.dirname(__file__))
outfile = re.sub(r'\W+', r'-', title).lower() + '.xhtml'
open(outfile, 'w').write(loader.load("dashboard.html").generate(**globals()))
