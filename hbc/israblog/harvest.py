import logging
import re
from datetime import datetime

from hbc.tools.httptools import FirefoxRequest
from hbc.db import WebPage

logger = logging.getLogger(__name__)

class IsrablogHarvester(object):

    blog_id_re = re.compile(r'blog=(\d+)')
    periods_re = re.compile(r'<select name="PeriodsForUser".*?</select>')
    period_value_re = re.compile(r'(?<=option value=")[^"]*')
    navigate_count_re = re.compile(r'var *navigateCount *= *(\d+)')
    
    def extract_period_urls(self, req):
        period_select = self.periods_re.findall(req.html)
        assert len(period_select) == 1
        periods = self.period_value_re.findall(period_select[0])
        urls = []
        for period in periods:
            month, year = period.split('/')
            urls.append('%s&year=%s&month=%s' % (req.url, year, month))
        return urls

    def extract_sub_pages(self, period_req):
        match = self.navigate_count_re.search(period_req.html)
        urls = []
        if match is not None:
            navigate_count = int(match.group(1))
            for i in range(1, navigate_count + 1):
                urls.append('%s&pagenum=%d' % (period_req.url, i))
        else:
            urls = [period_req.url]
        return urls

    def rip_random_blog(self):
        req = FirefoxRequest('http://israblog.nana10.co.il/random.asp')
        req.read()
        blog_id = self.blog_id_re.search(req.url).group(1)
        period_urls = self.extract_period_urls(req)
        all_sub_urls = []
        for period in period_urls:
            period_req = FirefoxRequest(period)
            period_req.read()
            all_sub_urls.extend(self.extract_sub_pages(period_req))
        for url in all_sub_urls:
            if len(list(WebPage.select(WebPage.q.url == url))) > 0:
                logger.info('%s already ripped' % url)
            else:
                req = FirefoxRequest(url)
                req.read()
                WebPage(site='israblog', clean_text='', url=url,
                        accessed=datetime.now(), raw=req.html,
                        age=None, user=None, sex=None)

    def rip_many(self, how_many):
        for i in range(how_many):
            print '>> %d <<' % i
            self.rip_random_blog()
