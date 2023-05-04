from pymongo import MongoClient

DB_HOSTS = ""
DB_PORT = 
DB_USERNAME = ""
DB_PWD = ""

client = MongoClient(host=DB_HOSTS, port=DB_PORT, username=DB_USERNAME, password=DB_PWD, authSource="")
db = client.get_database("")
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
