import scrapy
from scrapy import Request
from scrapy import Selector
import logging
import requests
import json
import numpy as np

def entryUrls():
    PERCENTILE_UPPER_RATE = 98
    PERCENTILE_LOWER_RATE = 95

    with open("./out.json","r") as f:
        infos = json.load(f)        
    base = 'https://www.prestomusic.com'
    q = '?award_winner=true&size=10&view=large&sort=relevance'
    list_of_urls = []
    counts = list(map(lambda entity: int(entity['count']), infos))
    t1 = np.percentile(counts, PERCENTILE_UPPER_RATE)
    t2 = np.percentile(counts, PERCENTILE_LOWER_RATE)
    for work in infos:
        if int(work['count'])<t1 and int(work['count'])>=t2:
            url = work['url']
            list_of_urls.append(base + url + q)
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

        yield request


    def process_item(self, item, composer, work, recommended):
        
        title_elem = item.css('.c-product-block__title')

        title = title_elem.css('a::text').get().replace('\n                                    ','')
        if title == '':
            title = title_elem.css('a')[0].css('::text')[-1].get()
        url = title_elem.css('a').attrib['href']
        img = item.css('.o-image > img').attrib['src']
        label = ''
        release_year = ''
        release_date = ''
        no = ''
        metadict = {}
        awards = []
        for meta in item.css('.c-product-block__metadata > ul > li'):
            caption = meta.css('strong::text').get()
            if 'Release Date:' in caption:
                [nul, dd, mm, yy] = meta.css('::text')[1].get().split(' ')
                m = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'].index(mm.lower()) + 1
                release_date = str(m) + '/'+dd[:-2]
                release_year = yy
            elif 'Label:' in caption:
                label = meta.css('::text')[1].get()
            elif 'Catalogue No:' in caption:
                no = meta.css('::text')[1].get()
            else:
                metatxt = meta.css('::text')[1].get().replace(caption,'')
                if metatxt != '':
                    metadict[caption.replace(':','')]=metatxt
                else:
                    try:
                        metatxt = meta.css('::text')[2].get().replace(caption,'')
                        if metatxt != '':
                            metadict[caption.replace(':','')]=metatxt
                    except:
                        print(meta)


        for award in item.css('.c-product-awards__list > li > div'):
            awards.append(award.attrib['aria-label'])

        return {'composer':composer,'title':title,'work':work,'url':url, 'cover':img, 'label':label, 'year':release_year, 'date':release_date, 'no':no, 'meta':metadict, 'awards':awards, 'recommended':recommended}


    def parse(self, response):
        MAX_ALBUM_PER_WORK=3

        logging.info("SCRAPING '%s'" % response.url)

        items = response.css('.c-browse__result')
        work = response.css('.c-h1--browse::text')[1].get().split(' - ')[1].replace(', Award Winners','')
        composer = response.css('.c-browse__header-info > p > a::text').get()
        recommended_exists = len(response.css('.c-product__recommendation')) > 0
        if recommended_exists:
            c = 0
            for item in items:
                recommended = len(item.css('.c-product__recommendation')) > 0
                if recommended and c <= MAX_ALBUM_PER_WORK: 
                    c+=1
                    yield self.process_item(item, composer, work, True)
        elif len(items)>0:
                yield self.process_item(items[0], composer, work, False)
        else:
            yield None
        next_url = self.url.__next__()
        yield Request(next_url)

