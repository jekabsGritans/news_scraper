import psycopg2
from typing import NamedTuple, List
from .config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from datetime import datetime

def sqlise(val):
    """
    Convert values to be SQL query friendly
    """
    if isinstance(val,str):
        return f"""
        '{val.replace("'","''")}'
        """
    
    if isinstance(val,int):
        return str(val)

    if isinstance(val, datetime):
        return val.strftime("'%Y-%m-%d %H:%M:%S-00'")


class DataBase:
    """One instance handles communication with one database"""
    def __init__(self, host = DB_HOST, port = DB_PORT, name = DB_NAME, user = DB_USER, password = DB_PASSWORD):
        self._conn = psycopg2.connect(host=host, port=port, dbname=name, user=user, password=password)
        self.cursor = self._conn.cursor()
    
    def insert(self, table: str, rows: List[NamedTuple]):
        """Inserts NamedTuples into a table, where each field of the NamedTuple is a column"""
        sql_values = []
        for row in rows:
            field_string = "("+",".join(row._fields)+")"
            values_string_list = [sqlise(value) for value in row]
            values_string = "("+",".join(values_string_list)+")"
            sql_values.append(values_string)

        sql_values_string = ",".join(sql_values).rstrip()               

        self.cursor.execute(
            f"""INSERT INTO {table} {field_string} VALUES {sql_values_string}"""
        )
        self._conn.commit()

local_db = DataBase()#default params are params from config.py