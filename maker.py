from db import collection
import redis

r = redis.StrictRedis(host="127.0.0.1", port=6379, charset="utf-8", decode_responses=True)


finder = collection.count_documents({"rating": ""})
print(finder)

finder = collection.find({"rating": ""})

for i in finder:
    r.lpush("isbn", i["isbn"])

