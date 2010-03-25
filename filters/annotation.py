import os
from pyExcelerator import XFStyle, Alignment, UnicodeUtils

UnicodeUtils.DEFAULT_ENCODING = 'utf8'

class Annotation(object):

    left = XFStyle()
    left_alignment = Alignment()
    left_alignment.horz = Alignment.HORZ_LEFT
    left_alignment.dire = Alignment.DIRECTION_RL
    left.alignment = left_alignment

    right = XFStyle()
    right_alignment = Alignment()
    right_alignment.horz = Alignment.HORZ_RIGHT
    right_alignment.dire = Alignment.DIRECTION_RL
    right.alignment = right_alignment

    center = XFStyle()
    center_alignment = Alignment()
    center_alignment.horz = Alignment.HORZ_CENTER
    center_alignment.direction = Alignment.DIRECTION_RL
    center.alignment = center_alignment

    def safe_mkdir(self, dirname):
        dir = os.path.join(os.path.expanduser('~/corpus/annotations'), dirname)
        try:
            os.mkdir(dir)
        except OSError:
            pass
        return dir

    def write_splitted(self, sentence, emph_place, sheet, row):
        words = [w.word if w.word else '' for w in sentence.words]
        # None words - where do they come from?

        before = ' '.join(words[:emph_place[0]])[-45:]
        verb = ' '.join(words[emph_place[0]:emph_place[1]+1])
        after = ' '.join(words[emph_place[1]+1:])[:45]
        all = ' '.join(words)
        
        sheet.write(row, 1, after, self.right)
        sheet.write(row, 2, verb, self.center)
        sheet.write(row, 3, before, self.left)
        sheet.write(row, 4, all, self.left)
        sheet.write(row, 5, str(sentence.metadata), self.left)
