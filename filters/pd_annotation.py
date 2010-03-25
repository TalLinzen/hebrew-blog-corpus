import os
from pyExcelerator import Workbook
from annotation import Annotation

class PDAnnotation(Annotation):

    def create(self, pd_filter, dirname=''):

        dir = self.safe_mkdir(dirname)

        by_user = {}
        for sentence in pd_filter.sentences:
            l = by_user.setdefault(sentence.metadata.get('user', 'NoUser'), [])
            l.append(sentence)

        for user, user_sentences in by_user.items():

            print 'Creating annotation spreadsheet for user %s' % user
            workbook = Workbook()
            sheet = workbook.add_sheet(str(user))
            sheet.col(1).width = 0x3000
            sheet.col(3).width = 0x3000
            for index, sentence in enumerate(user_sentences):
                m = min(sentence.lamed_indices)[0]
                self.write_splitted(sentence, (m, m), sheet, index)
            outfile = os.path.join(dir, '%s.xls' % user)
            workbook.save(outfile)
