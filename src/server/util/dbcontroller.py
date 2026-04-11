from cassandra.cluster import Cluster
from dotenv import load_dotenv
import os

load_dotenv()

class DatabaseManager:
    def __init__(self, node: str, keyspace: str):
        self.cluster = Cluster([node])
        self.session = self.cluster.connect(keyspace)

    def fetchData(self, table: str, query: list)->tuple:
        lookup_stmt = self.session.prepare(f"SELECT * FROM {table}")
        return self.session.execute(lookup_stmt)
        
    def insertData(self, data_type: str, data: dict, client_id: str):
        insert_stmt = self.session.prepare(f"INSERT INTO {data_type} (client_id, content) VALUES(?, ?)")
        try:
            self.session.execute(insert_stmt, [data.client_id, data.content])
        except Exception as e:
            print(f"Exception thrown while trying to insert data into database: {str(e)}")


NODE = os.getenv("NODE_IP")
KEYSPACE = os.getenv("KEYSPACE")

database_manager = None

try:
    database_manager = DatabaseManager(NODE, KEYSPACE)
except ValueError:
    print("[ERR] Missing NODE_IP or KEYSPACE environment variables")
    exit()
