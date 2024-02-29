import pandas as pd
from bs4 import BeautifulSoup
import json
import requests
import re
import time
from tqdm import tqdm







headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}


# 請填10個搜尋詞彙
keywords = ['乾拌麵','牛肉麵','去骨雞腿排','排骨','豆花','軟糖','水果軟糖','喉糖','夾心','米果']

# '鮮奶','鮮奶茶','豆花','軟糖','水果軟糖','喉糖','夾心','米果'

pages = 6
urls = []
df = []
for keyword in keywords:
    for page in range(1, pages):
        url = 'https://m.momoshop.com.tw/search.momo?_advFirst=N&_advCp=N&curPage={}&searchType=1&cateLevel=2&ent=k&searchKeyword={}&_advThreeHours=N&_isFuzzy=0&_imgSH=fourCardType'.format(page, keyword)
        print(url)
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, features="lxml")
            """
            #利用for迴圈得到畫面上所有商品的連結，並儲存到urls陣列裡面
            """
            for item in soup.select('li.goodsItemLi > a'):
                urls.append('https://m.momoshop.com.tw'+item['href'])
        else:
            print("沒有資料")
            break
        #urls = list(set(urls))
        #print(len(urls))
            
    


        
        #檢查是否有重複的urls並排除
        

for i, url in enumerate(tqdm(urls)):
    columns = []
    values = []
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, features="lxml")
    # 標題
    try:
        title = soup.find('meta', {'property': 'og:title'})['content']
    except:
        title = ''

    # 品牌
    try:
        brand = soup.find('meta',{'property':'product:brand'})['content']
    except:
        title =''
    # 連結
    try:
        link = soup.find('meta',{'property':'og:url'})['content']
    except:
        link = ''

    # 原價
    try:
        price = re.sub( '\r\n| ','',soup.find('del').text) 
    except:
        price = ''
    # 特價
    try:
        amount = soup.find('meta',{'property':'product:price:amount'})['content']
    except:
        amount = ''
    # 類型
    try:
        cate = ''.join([i.text for i in soup.findAll('article', {'class': 'pathArea'})])
        cate = re.sub('\n|\xa0', ' ', cate)
    except:
        cate =""
    

    # 描述
    try:
        desc = soup.find('div', {'class': ' '}).text
        desc = re.sub('\r|\n| ', '', desc)
    except:
        desc = 'Nan'

    print('==================  {}  =================='.format(i))
    print(title)
    print(brand)
    print(link)
    print(amount)
    print(cate)

    columns += ['title', 'brand', 'link', 'price', 'amount', 'cate', 'desc']
    values += [title, brand, link, price, amount, cate, desc]

    # 規格
    for i in soup.select('div.attributesArea > table > tr'):
        try:
            # 整理規格的內容
            column = i.find().text
            column = re.sub('\n|\r| ', '', column)
            value = ''.join([j.text for j in i.findAll('li')])
            value = re.sub('\n|\r| ', '', value)
            columns.append(column)
            values.append(value)
        except:
            pass
    ndf = pd.DataFrame(data=values, index=columns).T
    df.append(ndf)
df = pd.concat(df, ignore_index=True)
df.info()

#local_time = time.localtime(time.time())
#year = local_time.tm_year
#month = local_time.tm_mon
#day = local_time.tm_mday







# 儲存檔案


class_ = "食品・零食・飲料・生鮮"


df.to_excel(f'./{class_}.xlsx')




