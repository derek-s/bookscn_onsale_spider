#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# AUTHOR: Derek Song
# FILE: engine.py
# DATE: 2022/11/17
# TIME: 22:19:28

# DESCRIPTION:

import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests_toolbelt import SSLAdapter

from bs4 import BeautifulSoup as bas
from ua import UAMaker


import random
import time

def dban(isbn):

    # 隧道域名:端口号
    tunnel = ""

    # 用户名密码方式

    s = requests.Session()
    retries = Retry(total=10,backoff_factor=1,status_forcelist=[500,502,503,504])

    s.mount("http://", HTTPAdapter(max_retries=retries))
    s.mount("https://", HTTPAdapter(max_retries=retries))
    # s.mount("https://", SSLAdapter("TLSv1"))

    username = ""
    password = ""
    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" %  {"user": username, "pwd": password, "proxy": tunnel},
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" %     {"user": username, "pwd": password, "proxy": tunnel}
    }

    url = "" + isbn

    uaString = UAMaker().random_PC()

    headers = {
        "user-agent": uaString,
        'Accept-Encoding': 'gzip',
        "referer": url
    }
    try:
        detailPage = s.get(url, headers=headers, allow_redirects=True)
    except requests.exceptions.SSLError as e:
        print(e)
        time.sleep(2)
        rating = dban(isbn)
        s.close()

    except requests.exceptions.ProxyError as e:
        print(e)
        time.sleep(2)
        rating = dban(isbn)
        s.close()

    soup = bas(detailPage.text, "html5lib")
    #print(detailPage.text)
    try:
        rating = soup.select_one("div#interest_sectl > div > div.rating_self.clearfix > strong").get_text().replace(" ", "")
        print(rating)
        if(rating == ""):
            rating = "0.0"
        print("DRating: " + str(rating))
        s.close()
        
    except Exception as e:
        print("Error")
        try:
            error = soup.select_one("div#exception > ul > li").get_text()
            print(error)
            rating = "0.0"

        except:
            try:
                error = soup.select_one("h1").get_text()
                print(error)
                if(error == "登录跳转"):
                    time.sleep(3)
                    s.close()
                    rating = dban(isbn)
                    
                else:
                    print(error.strip())
                    rating = "0.0"
                    
            except:
                print("重试")
                time.sleep(1)
                s.close()
                rating = dban(isbn)
    time.sleep(random.randint(2,3))
    return rating
