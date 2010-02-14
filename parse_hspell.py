from transliterator import Transliterator

def parse_hspell(f='/Users/tal/University/PD/external_programs/hspell-1.0/dout.verbs'):

    infinitives = []
    t = Transliterator()    
    d = dict()
    verbs = open(f).read().lower().split('-----\n')
    for verb in verbs:
        forms = []
        for l in verb.split('\n'):
            if l and l[0] == 'l':
                infinitives.append(t.translate(l).split()[0])
            l = t.translate(l)
            sp = l.split()
            if len(sp) < 2:
                continue
            forms.append(sp[0])
        if len(forms) == 0:
            continue
        d[forms[0]] = forms
    return set(infinitives), d
    
