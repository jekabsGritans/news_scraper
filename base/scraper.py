from .db import Table
from .target import Target
from .user import UserMaster
from .config import CONCURRENT_REQUESTS
from .datastore import DataStore
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
import requests
from requests.exceptions import ProxyError


class DataConsumer(Thread):
    def __init__(self, data_store: DataStore, db_table: Table):
        Thread.__init__(self)
        self.data_store = data_store
        self.db_table = db_table

    def run(self):
        while True:
            if not self.data_store.empty:
                items = self.data_store.get_all()
                self.db_table.insert_many(items)
                print("Batch inserted")
            sleep(2)


def getx(g,n):
    out=[]
    for _ in range(n):
        try:
            out.append(next(g))
        except:
            break
    return out

class Scraper:
    """Handles threading for web scraping"""
    def __init__(self, target: Target, table: Table, user_master: UserMaster = UserMaster()):
        self.target = target
        self.user_master = user_master
        self.data_store = DataStore()
        self.data_consumer = DataConsumer(self.data_store, table)
        self.url_queue = DataStore()
    
    def populate_queue(self):
        """Populates URLs to scrape from the target URL generator"""
        #urls = islice(self.target._url_gen, CONCURRENT_REQUESTS*3)
        urls = getx(self.target._url_gen, 6)
        self.url_queue.add_many(urls)
        return bool(urls)

    def scrape_target(self, url):
        """Scrape a single url"""
        print("scraping: ", url)
        user = self.user_master.designee()
        try:
            r = user.get(url)
        except requests.exceptions.ProxyError:
            self.url_queue.add(url)
            
        if r.status_code == 200: # OK response
            print("Successful response")
            items, urls_to_scrape = self.target.extract_items(r)
            self.data_store.add_many(items)
            self.url_queue.add_many(urls_to_scrape)

        elif r.status_code == 429: # Bad repsonse, usually proxy detected - myb pause scraping?
            sys.exit(1)
        else:#TODO: if non-fatal status_code, add url back to queue
            print("statuscode: ",r.status_code)

    def start(self):
        self.data_consumer.start()
        pool = ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS)
        while True:
            if not self.populate_queue():
                break
            pool.map(self.scrape_target, self.url_queue.get_all())
        print("Finished")
