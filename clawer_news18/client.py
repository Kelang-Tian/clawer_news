from selenium import webdriver
#from selenium import exceptions
import pymongo
import socket
import time
import requests
from bs4 import BeautifulSoup
import traceback
import re



__HOST_ADDR__ = "127.0.0.1"
__HOST_PORT__ = 9992

__DB_ADDR__ = "127.0.0.1"
__DB_PORT__ = 27017

client_id = int(time.time())

mongo_client = pymongo.MongoClient("mongodb://{0}:{1}/".format(__DB_ADDR__, __DB_PORT__))
mongo_db = mongo_client["News"]
mongo_col = mongo_db["NewsWangyi"]

#driver = webdriver.Chrome()


def getinfo(newsURL, path1, path2, attr):
    html = gethtmltext(newsURL)
    try:
        soup = BeautifulSoup(html, 'html.parser')
        info = soup.find(path1, attrs={path2: attr})
        return info
    except:
        return ""


def gethtmltext(url, code="gbk"):
    try:
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = code
        return r.text
    except requests.exceptions.ConnectionError:
        return ""

while 1:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((__HOST_ADDR__, __HOST_PORT__))
        req = "get,{0}".format(client_id)
        sock.send(req.encode("gbk"))

        res = sock.recv(1024)
        sock.close()
        task_url = res.decode("gbk")

        #try:
        #    driver.get(task_url)
        #except:
        #    break
        #selector = etree.HTML(driver.page_source)


        print("---working with---：", task_url)
        text = {
            "title": getinfo(task_url, "div", "class", "post_content_main").string,
            "time": getinfo(task_url, "div", "class", "post_time_source").text.split()[0],
            "author": getinfo(task_url, "a", "id", "ne_article_source").string,
            "content": ""
        }
        text_content = getinfo(task_url, "div", "class", "post_text").get_text()
        for line in text_content:
            if line.isspace():
                continue
            text["content"] += (line.lstrip())

        #if mongo_col.find_one({"title": text["title"]}) is None:
        mongo_col.insert_one(text)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((__HOST_ADDR__, __HOST_PORT__))
        req = "done,{0},{1}".format(client_id, task_url)
        sock.send(req.encode("gbk"))

    except socket.error:
        print("Connection error")
        time.sleep(5)


