
from engine import dban
from db import collection

import redis
import time


r = redis.StrictRedis(host="127.0.0.1", port=6379,charset="utf-8", decode_responses=True)

while True:
    task = r.rpop("isbn")
    if not task:
        print("task list Emtpy")
        time.sleep(2)
        continue

    print(task)
    finder = collection.find_one({
        "isbn": task
    })

    if(finder["rating"] == ""):
        rating = dban(task)
        b = collection.find_one({"isbn": task})
        id = {"_id": b["_id"]}
        collection.update_one(id, {"$set": {"rating":  rating}})
    else:
        print("repeated task")
