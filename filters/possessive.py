# -*- coding: utf-8 -*-

from filter import Filter

class PossessiveFilter(Filter):

    white_list = set([
        u'שבר',
        u'הרס',
        u'מילא',
        u'שינה',
        u'שטף',
        u'רחץ',
        u'ניקה',
    ])

    black_list = set([
        u'אמר',
        u'אפשר',
        u'בא',
        u'גילה',
        u'האמין',
        u'הבטיח',
        u'הביא',
        u'הגיד',
        u'הגיש',
        u'הודיע',
        u'הוכיח',
        u'הזכיר',
        u'החזיר'
        u'היה',
        u'הכין',
        u'הסביר',
        u'העביר',
        u'העניק',
        u'הציע',
        u'הראה',
        u'הרשה',
        u'השאיל',
        u'השאיר',
        u'השיב',
        u'לקח',
        u'מכר',
        u'מסר',
        u'נדמה'
        u'נמאס',
        u'נראה',
        u'נתן',
        u'סיפר',
        u'עזר',
        u'עשה',
        u'קנה',
        u'קרה',
        u'שילם',
        u'שלח',
        u'שם',
        u'תרם',
    ])
    debug = False

    clitic_prepositions = set([
        u'ל',
        u'ב',
        u'כ',
        u'מ'
    ])

    def __init__(self, only_at_is_preposition=False, use_white_list=False):
        Filter.__init__(self)
        self.only_at_is_preposition = only_at_is_preposition
        self.use_white_list = use_white_list

    def is_relevant_verb(self, word):
        if self.use_white_list:
            return word.pos == 'verb' and \
                    word.lemma in self.white_list
        else:
            return word.pos == 'verb' and \
                    word.lemma in self.black_list

    def is_preposition(self, word):
        if self.only_at_is_preposition:
            return word.pos == 'at-preposition'
        else:
            return word.pos == 'at-preposition' \
                    or word.pos == 'preposition' \
                    or word.prefix in self.clitic_prepositions
