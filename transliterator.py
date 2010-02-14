from string import maketrans
import os

class Transliterator(object):
    
    aleph_ascii_code = 0xe0
    aleph_unicode_code = 0x90
    # letters with final forms appear twice
    hebrew_letters = 'abgdhwzxTikklmmnnsAppccqrSt'
    hmntx =          'ABGDHWZX@IKKLMMNNS&PPCCQR$T'
    morphtagger =    'ABGDHWZXJIKKLMMNNSEPPCCQRFT'

    def __init__(self):
        heb_ascii_codes = range(self.aleph_ascii_code, self.aleph_ascii_code + len(self.hebrew_letters))
        heb_unicode = range(self.aleph_unicode_code, self.aleph_unicode_code + len(self.hebrew_letters))
        source_sequence = ''.join(map(chr, heb_ascii_codes)) 
        unicode_source_seq = ''.join(map(chr, heb_unicode))
        self.trans_dict = maketrans(source_sequence, self.hebrew_letters)
        self.reverse_trans_dict = maketrans(self.hebrew_letters, source_sequence)
        self.high_ascii_remove = maketrans(''.join(map(chr, range(128, 256))), ' ' * 128)
        self.mine2hmntx_dict = maketrans(self.hebrew_letters, self.hmntx)
        self.mine2morphtagger_dict = maketrans(self.hebrew_letters, self.morphtagger)
        self.morphtagger2hebrew_dict = maketrans(self.morphtagger, source_sequence)
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

    def morphtagger2hebrew(self, s):
        return s.translate(self.morphtagger2hebrew_dict)
    
    def mine2hmntx(self, s, aggressive=False):
        if aggressive:
            return s.translate
        return s.translate(self.mine2hmntx_dict)

    def mine2morphtagger(self, s):
        return s.translate(self.mine2morphtagger_dict)

    def translate_file(self, filename):
        infile = open(filename)
        outfile = open(filename + '_trans', 'w')
        outfile.write(self.translate(infile.read()))
