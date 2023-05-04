#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# AUTHOR: Derek Song
# FILE: bcn.py
# DATE: 2022/11/17
# TIME: 21:28:45

# DESCRIPTION:

import random
import requests
from requests.adapters import HTTPAdapter
import time
import datetime
from search import SearchBook


from bs4 import BeautifulSoup as bas

from ua import UAMaker
#from engine import dban
from db import collection
import redis

def get_header():
    
    UAStr = UAMaker().random_PC()

    headers = {
        "user-agent": UAStr,
        "Accept-Encoding": "gzip"
    }

    return headers


def get_maxpagenum(firsturl, proxy=None):

    s = requests.session()
    s.mount('http://', HTTPAdapter(max_retries=20))
    s.mount('https://', HTTPAdapter(max_retries=20))
    
    if(proxy):
        firstPage = s.get(firsturl, headers=get_header(), proxies=proxy).text
    else:
        firstPage = s.get(firsturl, headers=get_header()).text

    soup = bas(firstPage, "html5lib")
    try:
        maxPageNum = soup.select_one("div.p-skip > em > b").get_text()
    except:
        maxPageNum = 1

    return maxPageNum


def get_bookmeta(listurl, homeurl, cid, pagenum, proxy=None):

    s = requests.session()
    s.mount('http://', HTTPAdapter(max_retries=20))
    s.mount('https://', HTTPAdapter(max_retries=20))

    r = redis.StrictRedis(host="", port=6379, charset="utf-8", decode_responses=True)

    if(proxy):
        listPage = s.get(listurl, headers=get_header(), proxies=proxy).text
    else:
        listPage = s.get(listurl, headers=get_header()).text
    
    print(cid + " Page: " + str(pagenum))

    soup = bas(listPage, "html5lib")

    tb = soup.select("div.bookTextCon > ul > li")
    for etb in tb:
        flag = True
        title = etb.select_one("div.name.fl > a").get_text().strip()
        anthor = etb.select_one("div.author.fl").get_text().strip()
        publish = etb.select_one("div.publish.fl").get_text().strip()
        price = etb.select_one("div.price.fl > span").get_text().replace("¥", "").  strip()
        salePrice = etb.select_one("div.salePrice.fl > span").get_text().replace("  ¥", "").strip()

        detailLink = etb.select_one("div.name.fl > a")["href"]

        # for bx in blackListTitle:
        #     if(bx in title):
        #         print("black list")
        #         flag = False
        #         break
    
        if(flag):
            count = collection.count_documents({"detailLink": homeurl + detailLink})

            if(count == 0):

                if(proxy):
                    detailPage = s.get(homeurl + detailLink, headers=get_header(),  proxies=proxy).text
                else:
                    detailPage = s.get(homeurl + detailLink, headers=get_header()).text

                xSoup = bas(detailPage, "html5lib")

                isbn = xSoup.select_one("div#copyrightInfor > ul > li").get_text().split("：")[1]

                if(SearchBook(isbn, title)): # 查询已有书库

                    count = collection.count_documents({"isbn": isbn})
                    if(count == 0):
                        today = datetime.datetime.today().strftime("%Y-%m-%d")

                        dbRow = {
                            "title": title,
                            "anthor": anthor,
                            "publish": publish,
                            "category": cid,
                            "price": price,
                            "salePrice": salePrice,
                            "detailLink": homeurl + detailLink,
                            "isbn": isbn,
                            "rating": "",
                            "doubanLink": isbn,
                            "addDate": today,
                            "updateDate": today,
                            "frequency": 1
                        }

                        collection.insert_one(dbRow)
                        print(title, anthor, publish, price, salePrice, "")
                        r.lpush("isbn", isbn)
                        time.sleep(random.randint(1,3))
                    else:
                        print("repeated isbn")
                else:
                    print("--*-- Purchased " + title + " --*--")
            else:

                finder = collection.find_one({"detailLink": homeurl + detailLink})

                today = datetime.datetime.today().strftime("%Y-%m-%d")

                id = {
                    "_id": finder["_id"]
                }
                frequency = finder["frequency"] + 1

                collection.update_one(
                    id, {"$set": {
                            "updateDate": today,
                            "frequency": frequency
                            }
                        }
                )

                print("in base, update info")


if __name__ == "__main__":
    
    tunnel = ""

    username = ""
    password = ""

    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
    }

    urlHomePage = ""
    urlFirst = ""
    urlEnd = ""

    # cid = {
    #     "54000000": "小说",
    #     "53000000": "文学",
    #     "37000000": "历史",
    #     "61000000": "哲学/宗教",
    #     "62000000": "政治/军事",
    #     "48000000": "社会科学",
    #     "52000000": "文化",
    #     "57000000": "艺术",
    #     "34000000": "经济",
    #     "64000000": "自然科学"
    # }


    cid = {
        "54000000": "小说",
        "53000000": "文学",
        "37000000": "历史",
        "61111600": "哲学/宗教-哲学理论",
        "61111800": "哲学/宗教-中国古代哲学",
        "61111700": "哲学/宗教-哲学知识读物",
        "61111300": "哲学/宗教-马哲",
        "61111000": "哲学/宗教-哲学",
        "61111500": "哲学/宗教-世界哲学",
        "61111900": "哲学/宗教-中国近当代哲学",
        "61111400": "哲学/宗教-美学",
        "61111100": "哲学/宗教-伦理学",
        "61111200": "哲学/宗教-逻辑学",
        "62122000": "政治/军事-政治理论",
        "62121700": "政治/军事-中国政治",
        "62111300": "政治/军事-军事理论",
        "62121800": "政治/军事-世界政治",
        "62120000": "政治/军事-政治",
        "62111700": "政治/军事-中外战争纪实",
        "62111400": "政治/军事-军事史",
        "62110000": "政治/军事-军事",
        "48190000": "社会科学-心理学",
        "48140000": "社会科学-社会科学总论",
        "48131200": "社会科学-社会学",
        "48131500": "社会科学-信息学",
        "48200000": "社会科学-新闻传媒出版",
        "48180000": "社会科学-文化人类学",
        "48131300": "社会科学-心理学",
        "48150000": "社会科学-社会学",
        "48150000": "社会科学-社会学理论",
        "57110000": "艺术-艺术理论",
        "57191600": "艺术-设计理论",
        "57211400": "艺术-理论/欣赏",
        "57201300": "艺术-摄影理论",
        "57201600": "艺术-作品集/作品赏析",
        "57201100": "艺术-摄影后期处理",
        "57200000": "艺术-摄影",
        "57201500": "艺术-数码摄影",
        "57201400": "艺术-摄影器材",
        "34180000": "经济-经济理论",
        "34211200": "经济-其他经济学理论",
        "34280000": "经济-经济通俗读物",
        "34270000": "经济-国际经济",
        "34190000": "经济-经济史",
        "34211400": "经济-政治经济学",
        "34210000": "经济-经济学理论"
    }


    f = 1

    for c in cid:

        # if(c == "57000000"):
        #     f = 42
        # else:
        #     f = 1

        firsturl = urlFirst + c + urlEnd +"1"
        maxpage = get_maxpagenum(firsturl)
        print(maxpage)
        
        for p in range(f, int(maxpage) + 1):
            
            urlListPage = urlFirst + c + urlEnd + str(p)
            
            get_bookmeta(urlListPage, urlHomePage, cid[c], p)
        
