# -*- coding: utf-8 -*-

from filter import Filter

class PossessiveFilter(Filter):

    white_list = {
        u'אכל': u'את',
        u'בדק': u'את',
        u'בהה': u'ב',
        u'בעט': u'ב',
        u'דחף': u'את',
        u'דרך': u'על',
        u'הזיז': u'את',
        u'החזיק': u'ב',
        u'הסתכל': u'על',
        u'הציף': u'את',
        u'הרים': u'את',
        u'הרס': u'את',
        u'זז': u'על',
        u'חימם': u'את',
        u'חסם': u'את',
        u'חתך': u'את',
        u'חתם': u'על',
        u'טייל': u'על',
        u'יצא': u'מ',
        u'ירד': u'מ',
        u'ישב': u'על',
        u'כיסה': u'את',
        u'מילא': u'את',
        u'משך': u'את',
        u'משך': u'ב',
        u'נגע': u'ב',
        u'נדבק': (u'ל', u'אל'),
        u'ניגב': u'את',
        u'ניפח': u'את',
        u'ניקה': u'את',
        u'נכנס': (u'ל', u'אל'),
        u'נפל': u'על',
        u'סובב': u'את',
        u'עזב': u'את',
        u'עלה': (u'ל', u'אל'),
        u'פגע': u'ב',
        u'פתח': u'את',
        u'צבע': u'את',
        u'צחק': u'על',
        u'צילם': u'את',
        u'קרע': u'את',
        u'קשר': u'את',
        u'ראה': u'את',
        u'שבר': u'את',
        u'שטף': u'את',
        u'שיבש': u'את',
        u'תלש': u'את',
        u'תקע': u'את',
        u'שיחק': u'ב',
        u'תלש': u'את'
    }

    black_list = set([
        u'אמר',
        u'אפשר',
        u'בא',
        u'בישר',
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
        u'ענה',
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

    def __init__(self, only_at_is_preposition=False, use_white_list=False,
            per_verb_limit=10000):
        Filter.__init__(self)
        self.only_at_is_preposition = only_at_is_preposition
        self.use_white_list = use_white_list
        self.per_verb_limit = per_verb_limit
        self.expected_prepositions = set()
        self.verb_counts = {}

    def is_relevant_verb(self, word):
        if self.use_white_list:
            if word.pos == 'verb' and word.lemma in self.white_list:
                prepositions = self.white_list[word.lemma]
                if isinstance(prepositions, basestring):
                    prepositions = (prepositions,)
                self.expected_prepositions = set(prepositions)
                return True
            else:
                return False
        else:
            return word.pos == 'verb' and \
                    word.lemma not in self.black_list

    def is_preposition(self, word):
        if word.prefix == u'ש':
            return False

        if self.use_white_list:
            return len(set((word.lemma, word.prefix)) & \
                    self.expected_prepositions) > 0

        if self.only_at_is_preposition:
            return word.pos == 'at-preposition'
        else:
            return word.pos == 'at-preposition' \
                    or word.pos == 'preposition' \
                    or word.prefix in self.clitic_prepositions

    def is_obstructor(self, word):
        return word.pos == 'punctuation' or word.prefix in (u'ש', u'ו', u'וש')

    def verb_count_still_low(self, verb):
        self.verb_counts[verb] = self.verb_counts.get(verb, 0) + 1
        return self.verb_counts[verb] <= self.per_verb_limit
        
