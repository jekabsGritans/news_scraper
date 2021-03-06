from collections import namedtuple
import lxml.html, re
from dateutil import parser as datetime_parser
from datetime import date, timedelta
from base.target import Target
from base.scraper import ThreadedScraper
from base.db import Table, default_db

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

#Scrape wsj archive for headlines

class WSJ(Target):
    Model = namedtuple("wsj_articles",["wsj_id", "newssection", "headline", "tstz"])
    
    def __init__(self, start_date, end_date):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date

    def urls(self):
        start_date = self.start_date
        end_date = self.end_date
        for day in daterange(start_date, end_date):
            url = day.strftime("https://www.wsj.com/news/archive/%Y/%m/%d")
            yield url
    
    
    def extract_items(self,response):
        parser = lxml.html.HTMLParser()
        doc = lxml.html.fromstring(response.content,parser=parser)
        num_pages = int(re.search("\d+", doc.xpath("//*[@id='main']/div[contains(@class,'secondary')]/div/div/div/span/text()")[0]).group())
        title = doc.xpath("/html/head/title/text()")[0]
        month, day, year = re.search("Archive for ([A-z]+) (\d+), (\d\d\d\d)", title).groups()
        articles = doc.xpath('//article')
        items=[]
        for article in articles:
            wsj_id = article.xpath("@data-id")[0]
            timestamp = article.xpath("descendant::div[contains(@class,'timestamp')]//div//p/text()")[0]
            section = article.xpath("descendant::div[contains(@class,'flashline')]//div//span/text()")[0]
            headline = article.xpath("descendant::span[contains(@class,'headline')]/text()")[0]
            dt = datetime_parser.parse(" ".join([year, month, day, timestamp]),ignoretz=True) + timedelta(hours=5)
            items.append(self.Model(wsj_id, section, headline, dt))
        if "?page=" not in response.request.url:
            to_scrape = [response.request.url+"?page=%d" % i for i in range(2,num_pages)]
        else: 
            to_scrape=[]
        return items, to_scrape


wsj = WSJ(date(2020,1,1),date(2020,12,31))
table = Table(default_db, wsj.Model)
scraper = ThreadedScraper(wsj, table)
scraper.start()
