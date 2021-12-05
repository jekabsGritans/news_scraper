from base.db import DataBase
from .target import Target
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from threading import Thread
from requests.exceptions import ProxyError
from .proxies import Proxy
from .headers import Headers
from .user import User
from .config import CONCURRENT_REQUESTS
from .datastore import DataStore


class DataConsumer(Thread):
    def __init__(self, data_store: DataStore, data_base: DataBase, db_table: str):
        Thread.__init__(self)
        self.data_store = data_store
        self.db = data_base
        self.db_table = db_table

    def run(self):
        while True:
            if not self.data_store.empty:
                items = self.data_store.get_all()
                self.db.insert(self.db_table, items)
            print("Batch uploaded to DB")
            sleep(3)


class Scraper:
    """Handles threading for web scraping"""
    def __init__(self, target: Target):
        self.target = target
        self.data_store = DataStore()
        self.data_consumer = DataConsumer(self.data_store, self.target.db, self.target.table)

    def start(self):
        args = ((url, User.from_randagent_proxyrotator(), self.data_store) for url in self.target._url_gen)
        self.data_consumer.start()
        ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS).map(lambda ar: self.target.scrape(*ar), args)         
                    