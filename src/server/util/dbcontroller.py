from cassandra.cluster import Cluster
from load_dotenv import load_dotenv
import os

load_dotenv()

class DatabaseManager:
    def __init__(self, node: str, keyspace: str):
        self.cluster = Cluster([node])
        self.session = cluster.connect(keyspace)

    def fetchData(self, data_type: str)->tuple:
        lookup_stmt = self.session.prepare("SELECT * FROM ?")
        return self.session.execute(lookup_stmt, [data_type])
        
    def insertData(self, data_type: str, data: dict):
        insert_stmt = self.session.prepare("INSERT INTO ? (client_id, content) VALUES(?, ?)")
        try:
            self.session.execute(insert_stmt, [data_type, data.client_id, data.content])
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
