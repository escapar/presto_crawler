import scrapy
from scrapy import Request
import logging
import requests
from scrapy import Selector

def entryUrls():
    base = 'https://prestomusic.com'
    res = requests.get("https://www.prestomusic.com/classical/composers")
    sel = Selector(res)
    list_of_urls = []
    for element in sel.css('.o-list--text'):
        for a in element.css('a'):
            list_of_urls.append(base + a.attrib['href'])
    for next_url in list_of_urls:
        yield next_url

class PrestoSpider(scrapy.Spider):
    name = 'prestospider'
    url = entryUrls()

    start_urls = []

    def start_requests(self):
        start_url = self.url.__next__()

        logging.info('START_REQUESTS : start_url = %s' % start_url)

        request = Request(start_url, dont_filter=True)

        ### important to yield, not return (not sure why return doesn't work here)
        yield request


    def parse(self, response):

        logging.info("SCRAPING '%s'" % response.url)
        col = response.css('.o-columns--1-2')[1]
        profile_block = response.css('.c-profile-block__title::text')
        composer = profile_block[0].get()
        for entity in col.css('a'):
            txts = entity.css('::text')
            title = ''
            count = ''
            if len(txts)>0:
                title = txts[0].get()
            if len(txts) > 1:
                count = txts[1].get().replace('(','').replace(')','')
            yield {'composer':composer,'title':title,'count':count,'url':entity.attrib['href']}

        next_url = self.url.__next__()
        yield Request(next_url)
