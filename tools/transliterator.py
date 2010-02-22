from string import maketrans
import os

class Transliterator(object):
    
    aleph_ascii_code = 0xe0
    aleph_unicode_code = 0x90
    # letters with final forms appear twice
    hebrew_letters = 'abgdhwzxTikklmmnnsAppccqrSt'

    def __init__(self):
        heb_ascii_codes = range(self.aleph_ascii_code, self.aleph_ascii_code + len(self.hebrew_letters))
        heb_unicode = range(self.aleph_unicode_code, self.aleph_unicode_code + len(self.hebrew_letters))
        source_sequence = ''.join(map(chr, heb_ascii_codes)) 
        unicode_source_seq = ''.join(map(chr, heb_unicode))
        self.trans_dict = maketrans(source_sequence, self.hebrew_letters)
        self.reverse_trans_dict = maketrans(self.hebrew_letters, source_sequence)
        self.unicode_dict = maketrans(unicode_source_seq, self.hebrew_letters)
        self.rev_unicode_dict = maketrans(self.hebrew_letters, unicode_source_seq)

    def translate(self, s, clean_high_ascii=False):
        translated = s.translate(self.trans_dict)
        if clean_high_ascii:
            translated = translated.translate(self.high_ascii_remove)
        return translated

    def taatik_to_unicode(self, s):
        return s.translate(self.rev_unicode_dict)

    def reverse_translate(self, s):
        return s.translate(self.reverse_trans_dict)
