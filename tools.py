def group_by(func, l):
    d = {}
    for x in l:
        d.setdefault(func(x), []).append(x)
    return d

def dicmif(d):
    return dict((x, len(y)) for x, y in d.items())
