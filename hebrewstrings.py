import re

__all__ = ['heb', 'rheb']

class HebrewStrings(object):

    hebrew_letters = 'abgdhwzxTiKklMmNnsAPpCcqrSt'
    aleph_unicode = 0x05d0
    numbers_re = re.compile(r'[\d\.]+')
    sofiot_re = re.compile(r'[kmnpc]\b')

    def __init__(self):
        self.letter_to_code = dict((self.hebrew_letters[i], unichr(self.aleph_unicode + i)) \
                for i in range(len(self.hebrew_letters)))
        self.letter_to_code.update({'(': ')', ')': '('})

    def fix_sofiot(self, s):
        return self.sofiot_re.sub(lambda x: x.group(0).upper(), s)

    def convert_reversed(self, s):
        s = self.fix_sofiot(s)
        s = self.numbers_re.sub(lambda match: ''.join(reversed(match.group(0))), s)
        s = ''.join(reversed(s))
        s = '\n'.join(reversed(s.split('\n')))
        return self.transliterate(s)

    def convert(self, s):
        s = self.fix_sofiot(s)
        return self.transliterate(s)

    def transliterate(self, s):
        return u''.join(self.letter_to_code.get(char, char) for char in s)

hs = HebrewStrings()
heb = hs.convert
rheb = hs.convert_reversed
