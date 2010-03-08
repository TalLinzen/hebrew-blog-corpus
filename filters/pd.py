# -*- coding: utf-8 -*-

from filter import Filter

class PossessiveDative(Filter):

    verbs_selecting_l = [u'נתן',
            u'היה',
            u'הראה',
            u'בישר',
            u'חסר',
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
            u'תרם',
            u'הציע',
            u'נענה',
            u'התרגל',
            u'חיכה',
            u'קנה',
            u'הרשה',
            u'העביר',
            u'סיפר',
            u'עזר',
            u'הגיד',
            u'החזיר']
    
    lamed = u'ל'
    vav_lamed = u'ול'
    max_distance = 3      # Between a verb and its associated lamed phrase

    def process(self, sentence):
        verb_neighborhoods = set()
        lamed_indices = set()

        for index, word in enumerate(sentence.words):
            if word.pos == 'verb' and word.lemma not in self.verbs_selecting_l:
                verb_neighborhoods.update(range(index - self.max_distance,
                    index + self.max_distance + 1))
            elif word.pos == 'noun' and \
                    word.prefix in (self.lamed, self.vav_lamed):
                lamed_indices.add(index)

        sentence.lamed_indices = set(index for index in lamed_indices \
                if index in verb_neighborhoods)
        return len(sentence.lamed_indices) > 0
