from pymongo import MongoClient

DB_HOSTS = "192.168.50.50"
DB_PORT = 27017
DB_USERNAME = "librarian"
DB_PWD = "123456"

client = MongoClient(host=DB_HOSTS, port=DB_PORT, username=DB_USERNAME, password=DB_PWD, authSource="Library")
db = client.get_database("Library")
collection = db.books


def SearchBook(isbn, bookname):
    if(" " in bookname):
        title = bookname.split(" ")[0]
    elif(":" in bookname):
        title = bookname.split(":")[0]
    elif("：" in bookname):
        title = bookname.split("：")[0]
    elif("，" in bookname):
        title = bookname.split("，")[0]
    else:
        title = bookname


    count = collection.count_documents({"ISBN": isbn})

    if(count == 0):
        r = collection.count_documents({
            "Title" : {"$regex": title}
        })

    if(count == 0 and r == 0):
        return True
    else:
        return False
