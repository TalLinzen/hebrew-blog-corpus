from db import setup_connection, WebPage, User
from israblog.clean import IsrablogCleaner, ExtractText
from israblog.harvest import IsrablogHarvester
from pdb import pm
import codecs
cleaner = IsrablogCleaner()
harvester = IsrablogHarvester()

def pheb(s):
    h = s.decode('cp1255')
    p = []
    for line in h.split('\n'):
        p.append(''.join(reversed(line)))
    print '\n'.join(p)

def dump(s):
    codecs.open('/tmp/t.html', 'w', 'utf16').write(s.clean_text.decode('utf8').replace('\n\n', '<br>'))
    codecs.open('/tmp/r.html', 'w', 'utf16').write(s.raw.decode('cp1255'))

def pheb2(s):
    print deu(s.decode('utf-8')).decode('cp1255')

def deu(s):
    return ''.join(chr(ord(x)) for x in s)

def u(s):
    return ''.join(unichr(ord(x)) for x in s)
