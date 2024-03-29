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
import os


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
        while True:
            try:
                req = s.get(firsturl, headers=get_header(), proxies=proxy)
                if(req.status_code == 200):
                    firstPage = req.text
                    break
                else:
                    print("Error statue_code: " + str(req.status_code))
                    time.sleep(2)
                    continue

            except Exception as e:
                print(e)
                print(datetime.datetime.now())
                print("Error")
                time.sleep(2)
                continue
    else:
        while True:
            try:
                req = s.get(firsturl, headers=get_header())
                if(req.status_code == 200):
                    firstPage = req.text
                    break
                else:
                    print("Error statue_code: " + str(req.status_code))
                    time.sleep(2)
                    continue
            except Exception as e:
                print(e)
                print(datetime.datetime.now())
                print("Error")
                time.sleep(2)
                continue
    if(firstPage != ""):
        soup = bas(firstPage, "html5lib")
        try:
            maxPageNum = soup.select_one("div.p-skip > em > b").get_text()
        except:
            maxPageNum = 1

        return maxPageNum
    else:
        print("Error: firstPage is null")


def get_bookmeta(listurl, homeurl, cid, pagenum, proxy=None):
    
    s = requests.session()
    s.mount('http://', HTTPAdapter(max_retries=20))
    s.mount('https://', HTTPAdapter(max_retries=20))

    r = redis.StrictRedis(host="127.0.0.1", port=6379, charset="utf-8", decode_responses=True)

    if(proxy):
        while True:
            try:
                req = s.get(listurl, headers=get_header(), proxies=proxy)
                if(req.status_code == 200):
                    listPage = req.text
                    break
                else:
                    print("Error statue_code: " + str(req.status_code))
                    time.sleep(2)
                    continue
            except Exception as e:
                print(e)
                print(datetime.datetime.now())
                print("Error")
                time.sleep(2)
                continue
    else:
        while True:
            try:
                req = s.get(listurl, headers=get_header())
                if(req.status_code == 200):
                    listPage = req.text
                    break
                else:
                    print("Error statue_code: " + str(req.status_code))
                    time.sleep(2)
                    continue
            except Exception as e:
                print(e)
                print(datetime.datetime.now())
                print("Error")
                time.sleep(2)
                continue
    
    print(cid + " Page: " + str(pagenum))

    soup = bas(listPage, "html5lib")

    tb = soup.select("div.bookTextCon > ul > li")
    for etb in tb:
        flag = True
        title = etb.select_one("div.name.fl > a").get_text().strip()
        author = etb.select_one("div.author.fl").get_text().strip()
        publish = etb.select_one("div.publish.fl").get_text().strip()
        price = float(etb.select_one("div.price.fl > span").get_text().replace("¥", "").  strip())
        salePrice = float(etb.select_one("div.salePrice.fl > span").get_text().replace("¥", "").strip())

        detailLink = etb.select_one("div.name.fl > a")["href"]

        if(flag):
            query = {"detailLink": homeurl + detailLink}
            book = collection.find_one(query)
            count = collection.count_documents(query)

            if(count == 0):

                if(proxy):
                    while True:
                        try:
                            req = s.get(homeurl + detailLink, headers=get_header(),  proxies=proxy)
                            if(req.status_code == 200):
                                detailPage = req.text
                                break
                            else:
                                print("Error statue_code: " + str(req.status_code))
                                time.sleep(2)
                                continue
                        except Exception as e:
                            print(e)
                            print(datetime.datetime.now())
                            print("Error")
                            time.sleep(2)
                            continue
                else:
                    while True:
                        try:
                            req = s.get(homeurl + detailLink, headers=get_header())
                            if(req.status_code == 200):
                                detailPage = req.text
                                break
                            else:
                                print("Error statue_code: " + str(req.status_code))
                                time.sleep(2)
                                continue
                        except Exception as e:
                            print(e)
                            print(datetime.datetime.now())
                            print("Error")
                            time.sleep(2)
                            continue

                xSoup = bas(detailPage, "html5lib")

                isbn = xSoup.select_one("div#copyrightInfor > ul > li").get_text().split("：")[1]

                sr = SearchBook(isbn, title)

                if(sr == 0 or sr == 1): # 查询已有书库

                    count = collection.count_documents({"isbn": isbn})
                    if(count == 0):


                        # 下载封面和采集简介信息
                        intro = xSoup.select("div#brief > p")
                        if(len(intro) > 0):
                            intro_text = intro[0].get_text()
                        else:
                            intro_text = ""
                        try:
                            imgDom = xSoup.select("div#popbigpic > a > img")[0]["src"]
                        except:
                            imgDom = ""
                        if(len(imgDom) > 0):
                            if("http" in imgDom):
                                imgUrl = imgDom
                            else:
                                temp = list(imgDom)
                                temp.insert(0, "http:")
                                imgUrl = "".join(temp)
                            imgName = isbn + ".jpg"
                            coverName = downloadCover(imgUrl, imgName, get_header(), None)
                        else:
                            coverName = "default.jpg"
                        
                        today = datetime.datetime.today().strftime("%Y-%m-%d")
                        dbRow = {
                            "title": title,
                            "author": author,
                            "publish": publish,
                            "category": cid.split("-")[0],
                            "price": price,
                            "salePrice": salePrice,
                            "detailLink": homeurl + detailLink,
                            "isbn": isbn,
                            "rating": "",
                            "doubanLink": "http://douban.com/isbn/"+isbn,
                            "addDate": today,
                            "updateDate": today,
                            "frequency": 1,
                            "cover_name": coverName,
                            "intro": intro_text,
                            "t_category": cid.split("-")[1]
                        }

                        if(sr == 0):
                            dbRow["inlib"] = 0
                            dbRow["suspected_title"] = 0
                            print(title, author, publish, price, salePrice, "")
                        if(sr == 1):
                            dbRow["inlib"] = 1
                            dbRow["suspected_title"] = 1
                            print("--*-- Suspected purchase " + title + " --*--")
                            print(title, author, publish, price, salePrice, "")

                        collection.insert_one(dbRow)
                        r.lpush("isbn", isbn)
                        time.sleep(random.randint(1,2))
                    else:
                        print("repeated isbn")

                else:
                    print("--*-- Purchased " + title + " skip --*--")
            else:

                finder = collection.find_one({"detailLink": homeurl + detailLink})

                today = datetime.datetime.today().strftime("%Y-%m-%d")

                id = {
                    "_id": finder["_id"]
                }
                frequency = finder["frequency"] + 1

                collection.update_one(
                    id, {"$set": {
                            "salePrice": salePrice,
                            "updateDate": today,
                            "frequency": frequency
                            }
                        }
                )
                print(book["isbn"] + " in base, update info")

def downloadCover(imgUrl, imgName, headers, proxy):

    s = requests.session()

    if(not os.path.isfile("Cover/"+imgName)):
        while True:
            try:
                if(proxy):
                    img = s.get(imgUrl, headers=headers, proxies=proxy, timeout=3)
                else:
                    img = s.get(imgUrl, headers=headers, timeout=3)
                if(len(img.content) > 2000):
                    open("cover/"+imgName, "wb").write(img.content)
                else:
                    print("Cover broke")
                    imgName = "default.jpg"
                break
            except Exception as e:
                print(e)
                print(datetime.datetime.now())
                print("Error")
                time.sleep(2)
                continue
    else:
        print(imgName + " is exits")
    
    return imgName

if __name__ == "__main__":
    

    avid = 0

    tunnel = ""


    username = ""
    password = ""

    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
    }

    urlHomePage = ""
    urlFirst = "" + str(avid) + ""
    urlEnd = ""

    cid = {
        "54000000": "小说-小说",
        "53000000": "文学-文学",
        "37000000": "历史-历史",
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
        "48151400": "社会科学-社会学理论",
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
        "34210000": "经济-经济学理论",
        "52000000": "文化-文化"
    }


    f = 1

    for c in cid:

        firsturl = urlFirst + c + urlEnd + "1"
        maxpage = get_maxpagenum(firsturl)
        print(maxpage)
        
        for p in range(f, int(maxpage) + 1):
            
            urlListPage = urlFirst + c + urlEnd + str(p)
            
            get_bookmeta(urlListPage, urlHomePage, cid[c], p)
        
