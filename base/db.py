
class DataBase:
    """Abstracts a database instance"""
    
    def connect(self):
        """Establishes a connection with the database"""


class Table:
    """Abstracts a table within a database instance"""
    db: DataBase
    
    def insert(self, item):
        """Inserts a single item in the database table"""

    def insert_many(self, items):
        """Inserts multiple items in the database table"""
