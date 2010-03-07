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

    suppress = True

    def __init__(self):
        object.__init__(self)
        self.age_regexp = re.compile(r'<b>(\xe1[\xef\xfa]):</b>\xa0(\d+)')   # b[nt] (ben/bat)
        self.sex_regexp = re.compile(r'<b>\xee\xe9\xef:</b>\xa0(.*?)<br>')   # min
        self.url_user_regexp = re.compile(r'blog=(\d+)')

    def new_clean(self, object):
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
            normalized = re.sub('[\r\n\xa0][\r\n\xa0 ]+', '\n', s.text)
            text.append(normalized)
        object.clean_text = '\n---------\n'.join(text).decode('cp1255').encode('utf8')

    def fill_age_and_sex(self, object):
        age_match = self.age_regexp.search(object.raw)
        if age_match:
            object.age = int(age_match.group(2))
            object.sex = 'male' if age_match.group(1) == '\xe1\xef' else 'female'
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

    def run_on_many(self, functions, start=0, end=None):
        if end is None:
            end = WebPage._connection.queryAll('select max(id) from web_page')[0][0]
            print 'total:', end
        if not isinstance(functions, list):
            functions = [functions]
        for i in range(start, end, 1000):
            print i
            objects = WebPage.select("id >= %d and id < %d" % (i, i + 1000))
            for object in objects:
                for function in functions:
                    if type(function) == tuple:
                        function, args = function
                    else:
                        args = ()
                    try:
                        function(object, *args)
                    except Exception, exc:
                        print '%d: major exc, giving up: %s' % (object.id, str(exc)[:200])

    def fill_user_table(self):
        User.dropTable()
        User.createTable()
        users = User._connection.queryAll('select distinct user from web_page')
        users = [x[0] for x in users]
        for i, user in enumerate(users):
            print i, user
            ages = User._connection.queryAll(
                    "select distinct age from web_page where user = '%s'" % user)
            potential_age = [y[0] for y in ages if y[0] != None]
            age = potential_age[0] if len(potential_age) != 0 else None
            sexes = User._connection.queryAll(
                    "select distinct sex from web_page where user = '%s'" % user)
            potential_sex = [y[0] for y in sexes if y[0] != None]
            sex = potential_sex[0] if len(potential_sex) != 0 else None
            posts = User._connection.queryAll(
                    "select clean_text from web_page where user = '%s'" % user)
            posts = '\n'.join(x[0] for x in posts)
            User(number=user, age=age, sex=sex)

    def count_tokens(self, object):
        if not hasattr(self, 'tokens'):
            self.tokens = 0

        for char in object.clean_text:
            if char == ' ' or char == '\n':
                self.tokens += 1

    word_in_english = re.compile(r'([A-Za-z]+)')
    character = re.compile(r'([\)\("-])')
    def prepare_for_tokenizer(self, string):
        '''
        Surround every word in Latin script with spaces, workaround for
        tokenizer bug
        '''
        string = self.word_in_english.sub(r' \1 ', string)
        string = self.character.sub(r' \1 ', string)
        return string
    
    def dump_to_files(self, object, dir='/home/tal/corpus_dumps'):
        thousand_dir = os.path.join(dir, str(object.id // 1000))
        if not os.path.isdir(thousand_dir):
            os.mkdir(thousand_dir)
        filename = os.path.join(thousand_dir, str(object.id))
        open(filename, 'w').write(self.prepare_for_tokenizer(object.clean_text))
    
    def load_back_from_files(self, object):
        thousand_dir = os.path.join(dir, str(object.id // 1000))
        f = '/home/tal/analyzed_corpus/%d/%d' % (thousand_dir, object.id)
        if os.path.exists(f):
            object.analyzed = open(f).read()

def run_morph_analyzer(start, end):
    '''
    start and end are in a scale of thousands: 4 means 4000-4999
    '''
    previous_dir = os.getcwd()
    os.chdir('/home/tal/tagger')
    for i in range(start, end):
        os.system('rm -rf /home/tal/analyzed_corpus/%d' % i)
        os.mkdir(os.path.join('/home/tal/analyzed_corpus', str(i)))
        command = 'java -Xmx1200m -XX:MaxPermSize=256m -cp trove-2.0.2.jar:morphAnalyzer.jar:opennlp.jar:gnu.jar:chunker.jar:splitsvm.jar:duck1.jar:tagger.jar vohmm.application.BasicTagger /home/tal/tagger/ /home/tal/corpus_dumps/%d/ /home/tal/analyzed_corpus/%d/ -lemma -tokenfeat -chunk' % (i, i)
        print command
        p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, close_fds=True)
        print 'STDOUT:', p.stdout.read()
        print 'STDERR:', p.stderr.read()
    os.chdir(previous_dir)
