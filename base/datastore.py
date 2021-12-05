from threading import Lock
from typing import List

class DataStore:
    def __init__(self):
        self.lock = Lock()
        self.items = []
        self.empty = True
    
    def add_many(self, items):
        with self.lock:
            self.items.extend(items)
            self.empty = False
    
    def get_all(self) -> List[object]:
        with self.lock:
            items, self.items = self.items, []
            self.empty = True
        return items