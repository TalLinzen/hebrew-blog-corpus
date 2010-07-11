# -*- coding: utf-8 -*-
import re, os, types, sys
import lxml.html, lxml.etree
from .db import WebPage, User
from HTMLParser import HTMLParser, HTMLParseError
from subprocess import Popen, PIPE

class HTMLToText(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.text = ''

    def handle_starttag(self, tag, attrib):
        self.text += ' '
        if tag == 'br':
            self.text += '\n'
        elif tag == 'p':
            self.text += '\n'

    def handle_data(self, data):
        self.text += data


class IsrablogCleaner(object):
    '''
    Example:
    cleaner = IsrablogCleaner()
    cleaner.run_many(cleaner.clean, cleaner.fill_user)
    '''

    suppress = True

    def __init__(self):
        object.__init__(self)
        self.age_regexp = re.compile(r'<b>(\xe1[\xef\xfa]):</b>\xa0(\d+)') # b[nt] (ben/bat)
        self.sex_regexp = re.compile(r'<b>\xee\xe9\xef:</b>\xa0(.*?)<br>') # min
        self.url_user_regexp = re.compile(r'blog=(\d+)')
        self.url_year_regexp = re.compile(r'year=(\d+)')

    def clean(self, object):
        s = lxml.html.fromstring(object.raw.decode('cp1255', 'ignore'))
        postedits = s.xpath('//span[@class="postedit"]')
        text = []
        for postedit in postedits:
            for element in postedit.iter():
                if isinstance(element, lxml.html.HtmlElement):
                    if not element.tag.isalpha():
                        element.tag = 'tag'
                else:
                    element.text = ''  # For processing instructions
                for key in element.attrib:
                    element.attrib.pop(key)
            as_string = lxml.html.tostring(postedit, encoding='cp1255')
            s = HTMLToText()
            s.feed(as_string)
            normalized = s.text.replace('\xa0', ' ')
            normalized = re.sub('[\r\n][\r\n ]+', '\n', normalized)
            text.append(normalized)
        object.clean_text = '\n---------\n'.join(text).decode('cp1255').\
                encode('utf8')

    def fill_age_and_sex(self, object):
        year_match = self.url_year_regexp.search(object.url)
        age_match = self.age_regexp.search(object.raw)
        if age_match:
            object.age = int(age_match.group(2))
            if year_match:
                object.birthyear = int(year_match.group(1)) - object.age
            object.sex = 'male' if age_match.group(1) == '\xe1\xef' else \
                    'female'
        else:
            sex_match = self.sex_regexp.search(object.raw)
            if sex_match:
                if sex_match.group(1) == '\xf0\xf7\xe1\xe4':
                    object.sex = 'female'
                elif sex_match.group(1) == '\xe6\xeb\xf8':
                    object.sex = 'male'
                else:
                    print 'Weird sex:', sex_match.group(1)

    def fill_user(self, object):
        match = self.url_user_regexp.search(object.url)
        object.user = match.group(1)

    def find_duplicates(self, object):
        # Shouldn't happen -- probably old bugs that have been since corrected
        same_url = WebPage.select(WebPage.q.url == object.url)
        deleted = open('/home/tal/corpus/deleted', 'a')
        for duplicate in list(same_url)[1:]:
            print 'Deleting %d' % duplicate.id
            deleted.write('%d\n' % duplicate.id)
            subdir = str(duplicate.id // 1000)
            os.unlink('/home/tal/corpus/clean_text/%s/%d' % \
                    (subdir, duplicate.id))
            os.unlink('/home/tal/corpus/analyzed/%s/%d' % \
                    (subdir, duplicate.id))
            duplicate.destroySelf()
        deleted.close()

    def run_on_many(self, functions, start=0, end=None):
        if end is None:
            end = WebPage._connection.\
                    queryAll('select max(id) from web_page')[0][0]
            print 'total:', end
        if not isinstance(functions, list):
            functions = [functions]
        for i in range(start, end, 1000):
            print i
            objects = WebPage.select("id >= %d and id < %d" % \
                    (i, min(end, i + 1000)))
            for object in objects:
                for function in functions:
                    if type(function) == tuple:
                        function, args = function
                    else:
                        args = ()
                    try:
                        function(object, *args)
                    except Exception, exc:
                        print '%d: major exc, giving up: %s' % \
                                (object.id, str(exc)[:200])

    def fill_user_table(self):
        User.dropTable()
        User.createTable()
        users = User._connection.queryAll('select distinct user from web_page')
        users = [x[0] for x in users]
        for i, user in enumerate(users):
            print i, user
            ages = User._connection.queryAll(
                    "select distinct age from web_page where user='%s'" % user)
            potential_age = [y[0] for y in ages if y[0] != None]
            age = potential_age[0] if len(potential_age) != 0 else None
            sexes = User._connection.queryAll(
                    "select distinct sex from web_page where user='%s'" % user)
            potential_sex = [y[0] for y in sexes if y[0] != None]
            sex = potential_sex[0] if len(potential_sex) != 0 else None
            chars = User._connection.queryAll(
                    "select sum(length(clean_text)) from web_page where user='%s'" % user)
            chars = int(chars[0][0])
            User(number=user, age=age, sex=sex, chars=chars)

    def count_tokens(self, object):
        if not hasattr(self, 'tokens'):
            self.tokens = 0

        for char in object.clean_text:
            if char == ' ' or char == '\n':
                self.tokens += 1

    word_in_english = re.compile(r'([A-Za-z]+)')
    character = re.compile(r'([\)\("-])')
    dots = re.compile(r'(\.\.+)')
    def prepare_for_tokenizer(self, string):
        '''
        Surround every word in Latin script with spaces, workaround for
        tokenizer bug
        '''
        string = self.word_in_english.sub(r' \1 ', string)
        string = self.character.sub(r' \1 ', string)
        string = self.dots.sub(r' \1 ', string)
        return string
    
    def dump_to_files(self, object, dir='/home/tal/corpus/clean_text',
            prepare_for_tokenizer=True):
        thousand_dir = os.path.join(dir, str(object.id // 1000))
        if not os.path.isdir(thousand_dir):
            os.mkdir(thousand_dir)
        filename = os.path.join(thousand_dir, str(object.id))
        text = self.prepare_for_tokenizer(object.clean_text) if \
                prepare_for_tokenizer else object.clean_text
        open(filename, 'w').write(text)
    
    def load_back_from_files(self, object):
        thousand_dir = object.id // 1000
        f = '/home/tal/corpus/analyzed/%d/%d' % (thousand_dir, object.id)
        if os.path.exists(f):
            object.analyzed = open(f).read()

def run_morph_analyzer(start, end):
    '''
    start and end are in a scale of thousands: 4 means 4000-4999
    '''
    previous_dir = os.getcwd()
    os.chdir('/home/tal/tagger')
    for i in range(start, end):
        os.system('rm -rf /home/tal/corpus/analyzed/%d' % i)
        os.mkdir(os.path.join('/home/tal/corpus/analyzed', str(i)))
        command = 'java -Xmx1200m -XX:MaxPermSize=256m -cp trove-2.0.2.jar:morphAnalyzer.jar:opennlp.jar:gnu.jar:chunker.jar:splitsvm.jar:duck1.jar:tagger.jar vohmm.application.BasicTagger /home/tal/tagger/ /home/tal/corpus/clean_text/%d/ /home/tal/corpus/analyzed/%d/ -lemma -tokenfeat -chunk' % (i, i)
        print command
        p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, close_fds=True)
        print 'STDOUT:', p.stdout.read()
        print 'STDERR:', p.stderr.read()
    os.chdir(previous_dir)
