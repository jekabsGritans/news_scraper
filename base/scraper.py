from base.db import DataBase
from .target import Target
from concurrent.futures import ThreadPoolExecutor
from time import sleep, time
from threading import Thread
from itertools import islice
from requests.exceptions import ProxyError
from .proxies import Proxy
from .headers import Headers
from .user import User
from .config import CONCURRENT_REQUESTS
from .datastore import DataStore

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
            sleep(3)


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
        urls = islice(self.target._url_gen, 100)#TODO: make N configurable
        self.url_queue.add_many(urls)
        return bool(urls)

    def scrape_target(self, url)
     """Scrape a single url"""
        user = self.user_master.designee()
        try:
            r = requests.get(url, proxies=user.proxy.dict(), headers=user.headers.dict())
        except requests.exceptions.ProxyError:
            self.url_queue.add(url)

        if r.status_code == 200: # OK response
            items, urls_to_scrape = self.target.extract_items(r)
            self.data_store.add_many(items)
            self.url_queue.add_many(urls_to_scrape)

        elif r.status_code == 429: # Bad repsonse, usually proxy detected - myb pause scraping?
            ...
        else:#TODO: if non-fatal status_code, add url back to queue
            ...

    def start(self):
        self.data_consumer.start()
        while True:
            if not self.populate_queue():
                break
            ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS).map(self.scrape_target, self.url_queue.get_all())
        print("Finished")
