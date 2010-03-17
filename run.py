from pdb import pm
import codecs

from db import setup_connection, WebPage, User
from israblog.clean import IsrablogCleaner, run_morph_analyzer
from israblog.harvest import IsrablogHarvester
from filters.pd import PossessiveDative
from filters.subcat import SubcategorizationFrames
from bgutag import BGUFile, BGUDir, BGUQuery

cleaner = IsrablogCleaner()
harvester = IsrablogHarvester()

def pheb(s):
    h = s.decode('cp1255')
    p = []
    for line in h.split('\n'):
        p.append(''.join(reversed(line)))
    print '\n'.join(p)

def dump(s):
    codecs.open('/tmp/t.html', 'w', 'utf16').write(s.clean_text.decode('utf8').replace('\n', '<br>'))
    codecs.open('/tmp/r.html', 'w', 'utf16').write(s.raw.decode('cp1255'))

def pheb2(s):
    print deu(s.decode('utf-8')).decode('cp1255')

def age_histogram():
    return WebPage._connection.queryAll('select age, count(*) from user group by age')
