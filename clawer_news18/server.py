from selenium import webdriver
from tasklist import TaskList
import time
import socket
import requests
from bs4 import BeautifulSoup
import traceback
import re


def main():
    addr = "0.0.0.0"
    port = 9992

    main_url = "http://money.163.com/special/00252C1E/gjcj.html"

    task_list = TaskList(timeout=30)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((addr, port))
    sock.listen(50)

    #driver = webdriver.Chrome()
    #driver.get(main_url)

    print("正在从网页中解析URL链接...")

    def gethtmltext(url, code="gbk"):
        try:
            r = requests.get(url)
            r.raise_for_status()
            r.encoding = code
            return r.text
        except requests.exceptions.ConnectionError:
            return ""
    html = gethtmltext(main_url)
    try:
        if html == "":
            print("---html error1!---")
        soup = BeautifulSoup(html, 'html.parser')
        url_info = soup.find_all('div', attrs={'class': 'list_item clearfix'})
        news_url = list()
        for i in url_info:
            # noinspection PyBroadException
            try:
                a = i.find(name='h2')
                url = a.find(name='a').attrs['href']
                news_url.append(url)
                print(url)
            except:
                continue
        task_list.put_tasks(news_url)
    except:
        print("---url error2!---")
        # driver.close()

    print("等待client中.......")
    while 1:
        if task_list.is_empty():
            print("====任务完成====")
            sock.close()
            break

        conn, addr = sock.accept()  # 接受TCP连接，并返回新的套接字与IP地址
        print('Connected by\n', addr, conn)  # 输出客户端的IP地址
        try:
            data = conn.recv(1024).decode("gbk")
            if data.split(',')[0] == "get":
                client_id = data.split(',')[1]
                task_url = task_list.get_task()


                print("向client {0} 分配 {1}".format(client_id, task_url))
                conn.send(task_url.encode("gbk"))
            elif data.split(',')[0] == "done":
                client_id = data.split(',')[1]
                client_url = data.split(',')[2]
                print("client {0}' 完成爬取 {1}".format(client_id, client_url))
                task_list.done_task(client_url)
                conn.send("ok".encode("gbk"))
        except socket.timeout:
            print("Timeout!")
        conn.close()  # 关闭连接


if __name__ == '__main__':
    main()