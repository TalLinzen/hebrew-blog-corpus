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

    def write_splitted(self, sentence, split_index, sheet, row):
        words = [w.word if w.word else '' for w in sentence.words]
        # None words - where do they come from?

        after = ' '.join(words[:split_index])[-45:]
        verb = words[split_index]
        before = ' '.join(words[split_index+1:])[:45]
        all = ' '.join(words)
        
        sheet.write(row, 1, after, self.right)
        sheet.write(row, 2, verb, self.center)
        sheet.write(row, 3, before, self.left)
        sheet.write(row, 4, all, self.left)
        sheet.write(row, 5, str(sentence.metadata), self.left)
