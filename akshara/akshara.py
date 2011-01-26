#!/usr/bin/python

'''
Usage: akshara.py reading-results.txt

Format of the reading results file:
DISTRICT|BLOCK|CLUSTER|SCODE|SNAME|MOI|SID|GENDER|LANGUAGE|CLASS|CURRNAME|ENAME|SUBJECT|GRADE
RAMNAGARA|MAGADI|MOTAGANAHALLI|34451|G LPS MUMMENAHALLI||1420426|Girl|KANNADA|4NoSection|Akshara Reading Program|Pre Test|Reading|O
RAMNAGARA|MAGADI|MOTAGANAHALLI|34451|G LPS MUMMENAHALLI||1420426|Girl|KANNADA|4NoSection|Akshara Reading Program|Post Test|Reading|S
'''

import sys, csv, os.path, re, collections, locale
from tornado import template

locale.setlocale(locale.LC_ALL, "")
filename = sys.argv[1]
title = os.path.splitext(filename)[0].lower()
fields = 'SUBJECT GENDER CLASS LANGUAGE DISTRICT BLOCK CLUSTER'.split(' ')
lookup = { 'O': 0, 'L': 1, 'W': 2, 'S': 3, 'P': 4 }
levels = dict(((v,k) for k,v in lookup.iteritems()))

# Store grades
student = {}
for row in csv.DictReader(open(filename), delimiter='|'):
    if row['ENAME'] not in ('Pre Test', 'Post Test'): continue
    sid = student.setdefault(row['SID'], {})
    sid[row['ENAME']] = row['GRADE']
    for field in fields:
        sid[field] = row[field]

# Compute summaries by field
summary = dict((field, {}) for field in fields)
pre     = dict((field, {}) for field in fields)
post    = dict((field, {}) for field in fields)
for row in student.values():
    if not (row.get('Pre Test', '') and row.get('Post Test', '')): continue
    for field in fields:
        key = lookup[row['Pre Test']], lookup[row['Post Test']]
        summary[field].setdefault(row[field], collections.defaultdict(int))[key] += 1
        pre [field].setdefault(row[field], collections.defaultdict(int))[key[0]] += 1
        post[field].setdefault(row[field], collections.defaultdict(int))[key[1]] += 1

improvement = dict((field, {}) for field in fields)
for field in fields:
    for value in pre[field].keys():
        pre_ave  = float(sum(k*v for k,v in pre [field][value].iteritems())) / sum(pre [field][value].values())
        post_ave = float(sum(k*v for k,v in post[field][value].iteritems())) / sum(post[field][value].values())
        improvement[field][value] = post_ave - pre_ave

school_pre, school_post = {}, {}
for row in student.values():
    if not (row.get('Pre Test', '') and row.get('Post Test', '')): continue
    school_pre.setdefault(row['CLASS'], collections.defaultdict(int))[row['Pre Test']] += 1
    school_post.setdefault(row['CLASS'], collections.defaultdict(int))[row['Post Test']] += 1

loader = template.Loader(os.path.dirname(__file__))
outfile = re.sub(r'\W+', r'-', title).lower() + '.xhtml'
open(outfile, 'w').write(loader.load('akshara.html').generate(**globals()))
