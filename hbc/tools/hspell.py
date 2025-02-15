# -*- coding: utf-8 -*-
import os, codecs
from hbc.conf import hspell_dir

lamed = u'ל'

def get_infinitives():
    verbs = codecs.open(os.path.join(hspell_dir, 'verbs'), encoding='utf8')
    infinitives = set() 
    for line in verbs.readlines():
        if line[0] == 'L':
            infinitives.add(lamed + line.split()[0][1:])
    return infinitives

infinitives = get_infinitives()
