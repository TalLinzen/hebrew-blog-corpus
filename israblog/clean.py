import re, os
from .db import WebPage, User
from HTMLParser import HTMLParser, HTMLParseError

class ExtractText(HTMLParser):

    def __init__(self, index, suppress):
        HTMLParser.__init__(self)
        self.index = index
        self.suppress = suppress
        self.in_postedit = False
        self.in_p = False
        self.text = ''
        self.span_stack = []

    def handle_starttag(self, tag, attrib):
        attrib = dict(attrib)
        if tag == 'span':
            self.span_stack.append(attrib.get('class'))
            if attrib.get('class') == 'postedit':
                self.in_postedit = True
        elif tag == 'p':
            self.in_p = True

    def handle_endtag(self, tag):
        if tag == 'span':
            try:
                popped = self.span_stack.pop()
            except IndexError:
                print '%d: unbalanced span' % self.index
                return
            if popped == 'postedit':
                self.in_postedit = False
        elif tag == 'p':
            self.in_p = False

    def check_for_whole_start_tag(self, *args):
        try:
            return HTMLParser.check_for_whole_start_tag(self, *args)
        except HTMLParseError, exc:
            if self.suppress:
                print '%d: check_for_whole_start_tag exc suppressed: %s' % (self.index, exc)
            else:
                raise

    def parse_endtag(self, *args):
        try:
            return HTMLParser.parse_endtag(self, *args)
        except HTMLParseError, exc:
            if self.suppress:
                print '%d: parse_endtag exc suppressed: %s' % (self.index, exc)
            else:
                raise

    def handle_data(self, data):
        if self.in_postedit or self.in_p:
            self.text += data


class IsrablogCleaner(object):

    suppress = True

    def __init__(self):
        object.__init__(self)
        self.weird_comment = re.compile(r'<![^>]*?>')
        self.high_ascii_in_tags = re.compile(r'<[^>]*?[\x80-\xff]+[^>]*?>')
        self.href = re.compile('href=[^>]+(?=>)')
        self.empty_attr = re.compile(r'(<[^>]+ )\w+= ')
        self.empty_end_tag = re.compile('</>')
        self.high_ascii = re.compile(r'[\x80-\xff]')
        self.unended_tag = re.compile('(<[^>]*?)<')

        self.age_regexp = re.compile(r'<b>(\xe1[\xef\xfa]):</b>\xa0(\d+)')   # b[nt] (ben/bat)
        self.sex_regexp = re.compile(r'<b>\xee\xe9\xef:</b>\xa0(.*?)<br>')   # min
        self.url_user_regexp = re.compile(r'blog=(\d+)')

    def clean(self, object):
        s = object.raw
        s = self.unended_tag.sub(lambda x: '%s><' % x.group(1), s)
        s = self.href.sub('', s)
        s = self.empty_end_tag.sub('', s)
        s = self.high_ascii_in_tags.sub(lambda x: self.high_ascii.sub('', x.group(0)), s)
        s = self.empty_attr.sub(lambda x: x.group(1), s)
        s = self.weird_comment.sub('', s)
        extract_text = ExtractText(object.id, self.suppress)
        extract_text.feed(s)
        object.clean_text = extract_text.text

    def fill_age_and_sex(object):
        # http://www.ascii.ca/cp1255.htm
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

    def fill_user(object):
        match = self.url_user_regexp.search(object.url)
        object.user = match.group(1)

    def run_on_many(self, functions, start=0, end=155000):
        if not isinstance(functions, list):
            functions = [functions]
        for i in range(start, end, 1000):
            print i
            objects = WebPage.select("id >= %d and id < %d" % (i, i + 1000))
            for object in objects:
                for function in functions:
                    function(object)

    def fill_user_table(self, out_dir):
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
            open(os.join.path(out_dir, user), 'w').write(posts)
            User(number=user, age=age, sex=sex)
            

