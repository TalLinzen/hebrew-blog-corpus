# Yahoo app ID:
# QwIN.i7V34GQeABgHohnvJCL_5QP6Vnv1FsLPJypqgH3HthF0wgtCHRH2khDXhsh

# create database corpus;
# use corpus;
# create table pages (url varchar(300), access date, data mediumtext);

from gzip import GzipFile
from cStringIO import StringIO
import re, time, sys, urllib, urllib2

from transliterator import Transliterator
from httptools import FirefoxRequest


class GoogleParser(object):

    results_per_page = 10
    max_results = 999

    def __init__(self):

        self.links_re = re.compile(r'(?<=<a href=")[^>]*?(?=" class=l)')
        self.exact_n_results_re = re.compile(r'<b>\d+</b> - <b>\d+</b>.*?<b>(\d+)</b>')
        
    def run(self, query, just_count=True):

        page_number = self.max_results / self.results_per_page
        links = []
        self.exact_n_results_known = False

        while page_number >= 0:
            response = self.send_request(query, page_number)
            data = self.unzip(response.read())

            if self.exact_n_results_known is False:
                match = self.exact_n_results_re.search(data)

                if match is not None:
                    self.n = int(match.group(1))
                    page_number = self.n / 100 - 1
                elif 'did not match any documents' in data and \
                        'Make sure all words are spelled correctly' in data:
                    self.n = 0
                else:
                    self.n = 1000

                self.exact_n_results_known = True

                if just_count:
                    return self.n
            else:
                time.sleep(1)
                page_number -= 1
            
            new_links = self.extract_links(data)
            links.extend(new_links)

        return links


    def send_request(self, query, page_number):

        d = {
                'hl': 'EN',
                'ie': 'utf-8',
                'oe': 'utf-8',
                'client': 'firefox-a',
                'rls': 'rg.mozilla:en-US:official',
                'q': query,
                'start': page_number * self.results_per_page,
                'sa': 'N',
                'filter': 0
            }

        req_str = 'http://www.google.co.il/search?' + urllib.urlencode(d)
        req = FirefoxRequest(req_str)
        return urllib2.urlopen(req)


    def unzip(self, s):

        return GzipFile(fileobj=StringIO(s)).read()


    def extract_links(self, data):

        return self.links_re.findall(data)
        

gp = GoogleParser()
