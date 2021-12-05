from collections import namedtuple
import lxml.html, re
from dateutil import parser as datetime_parser
from datetime import date, timedelta
from base.target import Target
from base.scraper import Scraper

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

#Scrape wsj archive for headlines

class WSJ(Target):
    item = namedtuple("wsj_articles",["wsj_id", "newssection", "headline", "tstz"])
    table = "wsj_headlines"

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
    
    
    @staticmethod
    def extract_items(response):
        parser = lxml.html.HTMLParser()
        doc = lxml.html.fromstring(response.content,parser=parser)
        num_pages = int(re.search("\d+", doc.xpath("//*[@id='main']/div[contains(@class,'secondary')]/div/div/div/span/text()")[0]).group())
        title = doc.xpath("/html/head/title/text()")[0]
        month, day, year = re.search("Archive for ([A-z]+) (\d+), (\d\d\d\d)", title).groups()
        print(f'scraping {month} {day} {year}')
        articles = doc.xpath('//article')
        items=[]
        for article in articles:
            wsj_id = article.xpath("@data-id")[0]
            timestamp = article.xpath("div[contains(@class,'timestamp')]//div//p/text()")[0]
            section = article.xpath("div[contains(@class,'flashline')]//div//span/text()")[0]
            headline = article.xpath("div[contains(@class,'headline')]//div//*//*//span/text()")[0]
            dt = datetime_parser.parse(" ".join([year, month, day, timestamp])) + timedelta(hours=5)
            items.append(WSJ.item(wsj_id, section, headline, dt))
        if "?page=" not in response.request.url:
            to_scrape = [response.request.url+"?page=%d" % i for i in range(2,num_pages)]
        else: 
            to_scrape=[]
        return items, to_scrape



wsj = WSJ(date(2011,1,1), date(2012,1,30))
Scraper(wsj).start()