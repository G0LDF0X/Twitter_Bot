#!/usr/bin/env python
# coding: utf-8

import sys
import json
import hashlib
import subprocess
import datetime
from time import time
from xml.etree import ElementTree
import bs4
import requests
import time
import tweepy
from tendo import singleton

me = singleton.SingleInstance()

# 현재 개인적으로 받아둔 Twitter 개발자 계정 API를 사용하고 있기 때문에 하단의 정보들은 가려둔다.
consumer_key = "트위터 개발자 API consumer_key"
consumer_secret = "트위터 개발자 API consumer_secret" 
access_token = "접근하려는 계정의 access_token"
access_token_secret = "접근하려는 계정의 access_token_secret"

auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


dryRun = False

while True:
    # time.sleep(600)
    with open("memory.json",encoding="utf8") as fp:
        data = json.load(fp)

    try:
        rawRSS = requests.get("https://trpgnet.work/rss").content.decode("utf8")
        root = ElementTree.fromstring(rawRSS)
    except: continue
    
    for item in root.findall("channel/item"):
        link = item.find("link").text
        title = item.find("title").text

        # 시나리오가 계속 숫자로 나온다는 전제 하에
        # shop_view = 그 외
        # 37 = 공지
        # 62 = 이용 가이드
        if link.find("https://trpgnet.work/shop_view/")!=-1 or link.find("https://rpg-net.work/INFO/")!=-1 or link.find("https://trpgnet.work/62/")!=-1:
            continue
            
        if link in data:
            continue

        print("detect new: %s" % (title))

        data[link] = True
        
        try:
            item_link = bs4.BeautifulSoup(requests.get(link).text)
        except : continue
    
        try:
            category = None
            if item_link.find("span",{"class": "category"})!=None:
                category = item_link.find("span",{"class": "category"}).get_text().strip()[1:-1]
                if(category == "자작 룰" or category == "번역 룰"):
                    tweet = "?? 새로운 룰이 투고되었습니다. \n" + link
                else:
                    if(category != "카테고리 없음"):
                        tweet = "?? 새로운 " + category + " 시나리오가 투고되었습니다. \n" + link
            elif item_link.find("ul",{"class": "sub_depth"})!=None:    
                # category = item_link.find("ul",{"class": "sub_depth"}).find("a",{"class": "active"}).get_text().strip()
                category = "상품"
                tweet = "새로운 " + category + "이 입고되었습니다. \n" + link
            else : continue
        except: continue

        if dryRun == True:
            print(tweet)
        else:
            api.update_status(tweet)

        with open("memory.json","w",encoding="utf8") as fp:
            fp.write(json.dumps(data,ensure_ascii=False,indent=4))
    time.sleep(600)



# In[ ]:




