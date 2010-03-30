# -*- coding: utf-8 -*-

from filter import Filter

class PossessiveFilter(Filter):

    verbs_selecting_l = set([u'נתן',
            u'היה',
            u'הראה',
            u'נמאס',
            u'האמין',
            u'הודיע',
            u'הבטיח',
            u'הזכיר',
            u'נדמה'
            u'נראה',
            u'מסר',
            u'לקח',
            u'העניק',
            u'הסביר',
            u'גילה',
            u'קרה',
            u'בא',
            u'אמר',
            u'קנה',
            u'הרשה',
            u'העביר',
            u'סיפר',
            u'עזר',
            u'הגיד',
            u'החזיר'])

    debug = False

    clitic_prepositions = set([
        u'ל',
        u'ב',
        u'כ',
        u'מ'
    ])

