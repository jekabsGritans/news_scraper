from abc import ABC, abstractmethod, abstractstaticmethod
from time import sleep
from typing import Generator, NamedTuple, List, Tuple
from requests import Response
from .db import DataBase, local_db
from .user import User
from .datastore import DataStore
import requests

class TryAgain(Exception):
    """Raised when non-fatal error occurs during scraping --> try again"""

class Target(ABC):#TODO: Consider separating html scraping and insertion in the db. Myb separate processes or move all to async
    """Baseclass - Handle job generation of a single site, where a job is a function to be executed that scrapes one url"""
    table: str
    db: DataBase = local_db
    item: NamedTuple

    def __init__(self):
        self._url_gen = self.urls()
    
    @abstractmethod
    def urls(self) -> Generator:
        """Defines Generator that yields urls to scrape"""
    
    @abstractstaticmethod
    def extract_items(response: Response) -> Tuple[List[NamedTuple],List[str]]:
        """Parses HTTP response's HTML and returns a list of NamedTuple-s (specifically - self.item-s) that represent the objects' properties = table columns and other extracted urls that need to be scraped"""

    def scrape(self, url: str, user: User, data_store: DataStore) -> None:
        """Scrape a single url"""     
        try:
            r = requests.get(url, proxies=user.proxy.dict(), headers=user.headers.dict())
        except requests.exceptions.ProxyError:
            raise TryAgain
        if r.status_code == 200: # OK response
            items, urls_to_scrape = self.extract_items(r)
            data_store.add_many(items)
            for url in urls_to_scrape:
                self.scrape(url, user=user, data_store=data_store)
        elif r.statuc_code == 429: # Bad repsonse, usually proxy detected
            ...
        else:
            ...