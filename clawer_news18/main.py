import requests
from bs4 import BeautifulSoup
import traceback
import re


def gethtmlText(url, code="utf-8"):

    #print("text1")
    try:
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = code
        #print("text2")

        return r.text
    except requests.exceptions.ConnectionError:
        return ""


def getstockList(lst, stockURL):

    #print("1")
    html = gethtmlText(stockURL)
    soup = BeautifulSoup(html, 'html.parser')
    a = soup.find_all('a')
    for i in a:
        # noinspection PyBroadException
        try:
            href = i.attrs['href']
            lst.append(re.findall(r"[s][hz]\d{6}", href)[0])
        except:
            continue
    #print(lst)

def getstockInfo(lst,stockURL,path):

    #print("2")
    count = 0
    for stock in lst:
        url = stockURL + stock + ".html"
        html = gethtmlText(url)

        try:
            if html == "":
                continue
            infoDict = {}
            soup = BeautifulSoup(html, 'html.parser')
            stockInfo = soup.find('div', attrs={'class': 'stock-bets'})
            if stockInfo == None:
                continue
            name = stockInfo.find('a', attrs={'class': 'bets-name'})
            infoDict.update({'股票名': name.text.split()[0]})

            keyList = stockInfo.find_all('dt')

            valueList = stockInfo.find_all('dd')

            for i in range(len(keyList)):
                key = keyList[i].text
                val = valueList[i].text
                infoDict[key] = val

            with open(path, 'a', encoding='utf-8') as f:
                f.write(str(infoDict)+'\n')
                count = count + 1

                print("\r当前进度: {:.2f}%".format(count * 100 / len(lst)), end="")
        except:
            count = count + 1
            print("\r当前进度: {:.2f}%".format(count * 100 / len(lst)), end="")
            continue


def main():
    stock_list_url = 'http://quote.eastmoney.com/stocklist.html'
    stock_Info_url = 'https://gupiao.baidu.com/stock/'
    store = "stock_info.txt"
    list = []
    getstockList(list, stock_list_url)
    getstockInfo(list, stock_Info_url, store)


if __name__ == '__main__':
    main()


   #url_info = soup.find('div', attrs={'class': 'news_main'})
    #a = url_info.find('h', attrs={'a': 'href'})