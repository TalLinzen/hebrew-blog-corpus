# -*- coding: utf-8 -*-
import codecs
import os

from hbc.conf import data_dir

def csv_read(filename):
    # Very simple CSV! Don't put commas in fields
    handle = codecs.open(os.path.join(data_dir, filename), encoding='utf8')
    lines = []
    for line in handle.readlines():
        words = []
        for word in line.strip().split(','):
            if word[0] == '"':
                word = word[1:]
            if word[-1] == '"':
                word = word[:-1]
            words.append(word)
        lines.append(tuple(words))
    return lines

def csv_read_list(filename):
    return [x[0] for x in csv_read(filename)]

def csv_read_set(filename):
    return set(csv_read_list(filename))

def csv_read_dict(filename):
    return dict(csv_read(filename))

body_parts = csv_read_set('body_parts.csv')

subcat_candidates = [
    u'אהב',
    u'אחז',
    u'החליט',
    u'הכחיש',
    u'הכריז',
    u'הצהיר',
    u'הצטער',
    u'השתוקק',
    u'התבשר',
    u'התגעגע',
    u'התחרט',
    u'התלהב'
    u'התנגד',
    u'התנדב',
    u'התעסק',
    u'התעקש',
    u'התפתה',
    u'התקרב',
    u'התרגל',
    u'התריע',
    u'וידא',
    u'זכר',
    u'חייג',
    u'חפץ',
    u'חקר',
    u'טעם',
    u'כרסם',
    u'מיעט',
    u'נזכר',
    u'נטה',
    u'ניחש',
    u'ניסה',
    u'נקט',
    u'סיים',
    u'סירב',
    u'סרב',
    u'פגש',
    u'ציין',
    u'קיווה',
    u'שנא',
    u'תכנן',
]

possession_black_list = set([
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
    u'תרם'])

governed_preps = {
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
    u'השתלט': u'על',
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
    u'שיחק': u'ב',
    u'תלש': u'את',
    u'תקע': u'את',
    u'שיחק': u'ב',
    u'תלש': u'את'
}

# All dative with only pronouns, ages 23 to 40, which had at least
# 5 occurences for a specific frame (preposition after dative)
pd_verbs = csv_read_dict('possessive_dative_verbs.csv')

def tuplify_values(d):
    for key in d.keys():
        if isinstance(d[key], basestring):
            d[key] = (d[key],)

tuplify_values(pd_verbs)

subcat_cond1 = [
    u'התגעגע',
    u'ניסה',
    u'פגש',
    u'וידא',
    u'התלהב',
    u'חקר',
    u'קיווה',
    u'סירב',
]

subcat_cond2 = [
    u'נקט',
    u'זכר',
    u'התעקש',
    u'החליט',
    u'הצטער',
    u'תכנן',
    u'השתוקק',
    u'הכריז'
]

subcat_control = [
    u'נתקל',
    u'ניגש',
    u'הצחיק',
    u'שבר',
    u'חיבק',
    u'הזיק',
    u'בהה',
    u'שיפר'
]

einat_previous_experiment = [
    u'השלים',
    u'דרך',
    u'טעם',
    u'בנה',
    u'פרץ',
    u'זלל',
    u'לגם',
    u'שקל',
    u'הכחיש',
    u'סיים',
    u'התחרט',
    u'נחלץ',
    u'הספיק',
    u'הפסיק',
    u'קיווה',
    u'ניסה',
    u'התעקש',
    u'התרגל',
    u'שנא',
    u'הקפיד'
]
