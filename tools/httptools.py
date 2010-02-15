from HTMLParser import HTMLParser, HTMLParseError
from urllib2 import Request, urlopen
import logging
from gzip import GzipFile
from cStringIO import StringIO

LOGGER = logging.getLogger("Corpus builder")


class FirefoxRequest(Request):

    def __init__(self, *args, **kwargs):
        Request.__init__(self, *args, **kwargs)

        print "HTTP request: %s" % args[0]
        self.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.1) Gecko/2008070206 Firefox/3.0.1')
        self.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        self.add_header('Accept-Language', 'en-us,en;q=0.5')
        self.add_header('Accept-Encoding', 'gzip,deflate')
        self.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7')

    def read(self):

        self.response = urlopen(self)
        self.html = self.response.read()
        self.url = self.response.geturl()
        if self.response.info().get('Content-Encoding', '').upper() == 'GZIP':
            self.html = GzipFile(fileobj=StringIO(self.html)).read()


class HTML2Text(HTMLParser):

    tags_to_ignore = ['script']

    def __init__(self):
        HTMLParser.__init__(self)
        self.discarded_tags = []
        self.data = ''

    def handle_starttag(self, tag, attrs):
        if tag in self.tags_to_ignore:
            self.discard_data = True
        elif tag in ('br', 'p'):
            self.data += '\n'

    def handle_data(self, data):
        if len(self.discarded_tags) == 0:
            self.data += data

    def handle_endttag(self, tag):
        self.discarded_tags.remove(tag)

    def feed_ignore_errors(self, data):
        for d in data:
            try:
                self.feed(d)
            except HTMLParseError, exc:
                pass
