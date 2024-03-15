from pymongo import MongoClient

DB_HOSTS = ""
DB_PORT = 0
DB_USERNAME = ""
DB_PWD = ""

client = MongoClient(host=DB_HOSTS, port=DB_PORT, username=DB_USERNAME, password=DB_PWD, authSource="booksChina")
db = client.get_database("booksChina")
collection = db.books
