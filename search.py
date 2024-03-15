from pymongo import MongoClient

DB_HOSTS = ""
DB_PORT = 0
DB_USERNAME = ""
DB_PWD = ""

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
    elif("(" in bookname):
        title = bookname.replace("(", "")
        title = title.replace(")", "")
    elif(")" in bookname):
        title = bookname.replace("(", "")
        title = title.replace(")", "")
    else:
        title = bookname


    ir = collection.count_documents({"ISBN": isbn})

    if(ir == 0):
        tr = collection.count_documents({
            "Title" : {"$regex": r"(?i)title"}
        })

    if(ir == 0 and tr == 0):
        return 0 # 返回0表示库内没有
    elif(ir == 0 and tr != 0):
        return 1 # 返回1表示疑似库内有，标题可能匹配
    else:
        return -1 # isbn匹配的情况不管标题如何都认为存在
    

