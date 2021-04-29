# -*- coding = utf-8 -*-
# @Time : 2020/11/5 21:28
# @Author : 罗斐月
# @File : spider.py
# @Software : PyCharm

import bs4       #网页解析，获取数据
import re        #正则表达式，进行文字匹配
import urllib.request,urllib.error      #制定URL，获取网页数据
import xlwt       #进行excel操作
import sqlite3    #进行SQLlite数据库操作
import urllib.request
from bs4 import BeautifulSoup

def main():
    baseurl = "https://movie.douban.com/top250?start="
    #1.爬取网页
    datalist = getData(baseurl)
    #savapath = ".\\豆瓣电影Top250.xls"

    dbpath = ("movie.db")
    #3.保存数据
    #savaData(datalist,savapath)
    savaDataDB(datalist,dbpath)

    #askURL("https://movie.douban.com/top250?start=")

#获取影片内容链接规则
findLink = re.compile(r'<a href="(.*?)">') #创建正则表达式，表示规则
#获取影片图片
findImgSrc = re.compile(r'<img.*src="(.*?)"',re.S)  #re.S 让换行符包含在其中
#获取影片片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
#获取影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
#获取影片评价人数
findJudge = re.compile(r'<span>(\d*)人评价</span>')
#获取概况
finIng = re.compile(r'<span class="inq">(.*?)</span>')
#获取影片相关内容
findBd = re.compile(r'<p class="">(.*?)</p>',re.S)


#1.爬取网页
def getData(baseurl):
    datalist = []
    for i in range(0,250,25):      #调用获取信息内容，25次
        url = baseurl + str(i)
        html = askURL(url)         #保存获取到的网页


        #逐一解析数据
        soup = BeautifulSoup(html,"html.parser")
        for item in soup.find_all('div',class_="item"):
            #print(item)
            data = []  #保存一部电影的所有信息
            item = str(item)

            #获取超链接
            link = re.findall(findLink,item)[0]
            data.append(link)

            imgSrc = re.findall(findImgSrc,item)[0]
            data.append(imgSrc)

            title = re.findall(findTitle,item)[0]
            data.append(title)
            # if(len(title) == 2):
            #     ctitle = title[0]                  #添加中文名
            #     data.append(ctitle)
            #     otitle = title[1].replace("/","")  #去掉无关符号
            #     data.append((otitle))              #添加外国名
            # else:
            #     data.append(title[0])
            #     data.append('')                   #外文名留空


            rating = re.findall(findRating,item)[0]
            data.append(rating)                    #添加评分

            judge = re.findall(findJudge,item)[0]
            data.append(judge)                     #添加评分人数

            ing = re.findall(finIng,item)      #添加概况
            if len(ing) != 0:
                ing = ing[0].replace("。","")      #去掉句号
                data.append(ing)
            else:
                data.append(" ")                  #留空
            #data.append(ing)

            bd = re.findall(findBd,item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?'," ",bd) #去掉<br>
            bd = re.sub('/'," ",bd)
            data.append(bd.strip())                #去掉前后空格

            

            datalist.append(data)                  #电影信息放入datalist


    #print(datalist)
    return datalist


#得到指定一个URL的网页内容
def askURL(url):
       #模拟浏览器头部信息
    head = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"}
       #用户代理

    request = urllib.request.Request(url,headers=head)
    html=""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        #print(html)
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html


#3.保存数据
def savaData(datalist,savapath):
    print("sava....")

    book = xlwt.Workbook(encoding="utf-8",style_compression=0)  # 创建workbook对象
    sheet = book.add_sheet('豆瓣电影top250',cell_overwrite_ok=True)  # 创建工作表
    col = ("电影详情链接","图片链接","影片中文名","评分","评价数","概况","相关内容")

    for i in range(0,7):
        sheet.write(0,i,col[i])
    for i in range(0,250):
        print("第%d条"%(i+1))
        data = datalist[i]
        for j in range(0,7):
            sheet.write(i+1,j,data[j])


    book.save(savapath)

def savaDataDB(datalist,dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            if index == 3 or index == 4:
                continue
            data[index] = '"'+(str)(data[index])+'"'
        sql = '''
                insert into movie250(
                info_link,pic_link,name,score,rated,instroduction,info
                )
                values(%s)'''%",".join(data)
        print(sql)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()


def init_db(dbpath):
    sql = '''
          create table if not exists movie250  
          (
          id integer primary key not null ,
          info_link text,
          pic_link text,
          name varchar ,
          score numeric ,
          rated numeric ,
          instroduction text,
          info text
          );
                
                
        '''                   #创建数据库
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()

#if __name__ == "__mian__":    #当程序执行时

# 调用函数
main()
#init_db("movietest.db")
print("爬取完毕")


