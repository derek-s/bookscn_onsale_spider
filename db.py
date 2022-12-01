from pymongo import MongoClient

DB_HOSTS = ""
DB_PORT = 27017
DB_USERNAME = ""
DB_PWD = ""

client = MongoClient(host=DB_HOSTS, port=DB_PORT, username=DB_USERNAME, password=DB_PWD, authSource="")
db = client.get_database("")
collection = db.books
