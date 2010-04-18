from urllib2 import urlopen
from string import maketrans

urls = ['http://www.cs.technion.ac.il/~erelsgl/bxi/hmntx/milon/lex0p.ma',
        'http://www.cs.technion.ac.il/~erelsgl/bxi/hmntx/milon/lex0e.ma']

categories = {'p': 'ProperName',
        't': 'Adverb',
        'E': 'Noun',
        'j': 'Interrogative',
        'T': 'Adjective',
        'x': 'Conjunction',
        'm': 'Particle',
        'P': 'Verb'}

def parse_hmntx(urls):
    hmntx = 'ABGDHWZX@IKKLMMNNS&PPCCQR$T'
    heb_unicode = map(unichr, range(0x05d0, 0x05d0 + len(hmntx)))
    trans_dict = dict((source, target) for source, target in \
            zip(hmntx, heb_unicode))
    sofiot = {u'\u05db': u'\u05da', u'\u05de': u'\u05dd',
            u'\u05e0': u'\u05df', u'\u05e4': u'\u05e3',
            u'\u05e6': u'\u05e5'}

    text = '\n'.join(urlopen(url).read() for url in urls)
    lines = text.split('\n')
    d = {}
    for line in lines: 
        if line == '' or line[0] in ('{', '}', '%'):
            continue
        lemma, kind = line.split()
        category = categories.get(kind[0], kind[0])
        if lemma[-1] == ':':
            lemma = lemma[:-1]    
        if category == 'Verb' and lemma[-1] == 'I':
            # replace root final yod with heh
            lemma = lemma[:-1] + 'H'
        t = ''.join(trans_dict.get(c, c) for c in lemma)
        t = t[:-1] + sofiot.get(t[-1], t[-1])
        d.setdefault(category, []).append(t)

    for category, words in d.items():
        codecs.open(category, 'w', 'utf8').write(u'\n'.join(words))
