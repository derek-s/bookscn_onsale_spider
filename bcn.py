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


from bs4 import BeautifulSoup as bas

from ua import UAMaker
#from engine import dban
from db import collection


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

    maxPageNum = soup.select_one("div.p-skip > em > b").get_text()

    return maxPageNum


def get_bookmeta(listurl, homeurl, cid, pagenum, proxy=None):

    s = requests.session()
    s.mount('http://', HTTPAdapter(max_retries=20))
    s.mount('https://', HTTPAdapter(max_retries=20))

    if(proxy):
        listPage = s.get(listurl, headers=get_header(), proxies=proxy).text
    else:
        listPage = s.get(listurl, headers=get_header()).text
    
    print(cid + " Page: " + str(pagenum))

    soup = bas(listPage, "html5lib")

    tb = soup.select("div.bookTextCon > ul > li")
    for etb in tb:
        title = etb.select_one("div.name.fl > a").get_text().strip()
        anthor = etb.select_one("div.author.fl").get_text().strip()
        publish = etb.select_one("div.publish.fl").get_text().strip()
        price = etb.select_one("div.price.fl > span").get_text().replace("¥", "").strip()
        salePrice = etb.select_one("div.salePrice.fl > span").get_text().replace("¥", "").strip()

        detailLink = etb.select_one("div.name.fl > a")["href"]

        count = collection.count_documents({"detailLink": homeurl + detailLink})
        
        if(count == 0):
            
            if(proxy):
                detailPage = s.get(homeurl + detailLink, headers=get_header(), proxies=proxy).text
            else:
                detailPage = s.get(homeurl + detailLink, headers=get_header()).text

            xSoup = bas(detailPage, "html5lib")

            isbn = xSoup.select_one("div#copyrightInfor > ul > li").get_text().split("：")[1]

            count = collection.count_documents({"detailLink": homeurl + detailLink})

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
                    "doubanLink": ""+isbn,
                    "addDate": today,
                    "updateDate": today
                }

                collection.insert_one(dbRow)
                print(title, anthor, publish, price, salePrice, "")

                time.sleep(random.randint(2,5))
        else:
            
            finder = collection.find_one({"detailLink": homeurl + detailLink})
            
            today = datetime.datetime.today().strftime("%Y-%m-%d")

            id = {
                "_id": finder["_id"]
            }
            collection.update_one(
                id, {"$set": {"updateDate": today}}
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
    #     "64000000": "自然科学",
    #     "0": "未分类"
    # }

    cid = {
        "62000000": "政治/军事",
        "48000000": "社会科学",
        "52000000": "文化",
        "57000000": "艺术",
        "34000000": "经济",
        "64000000": "自然科学"
    }

    for c in cid:

        firsturl = urlFirst + c + urlEnd +"1"
        maxpage = get_maxpagenum(firsturl)
        print(maxpage)
        if(c == "62000000"):
            f = 7
        else:
            f = 1
        for p in range(f, int(maxpage) + 1):
            
            urlListPage = urlFirst + c + urlEnd + str(p)
            
            get_bookmeta(urlListPage, urlHomePage, cid[c], p)
        
