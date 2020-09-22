#!/usr/bin/env python
#coding=utf-8

import re                       # 爬虫进么能够不用到正则表达式呢？
from bs4 import BeautifulSoup   # 需要安装的这个美丽的汤的：一个用着比较爽的html，xml解析模块
import urllib                  # 当然，你也可以用其他你用着比较爽的模块，httplib,urllib,pycurl
import requests
import json
import pymysql

from urllib.request import quote, unquote

# from urlparse import urlparse   # 虽然这个模块不是必需的，但有了它，url解析起码简单很多

def list_url():

    tmp_url = ['https://www.1905.com/mdb/film/calendaryear/2013']

    return tmp_url


# 开始1905 首页
def start_url():
    url_to_work = []

    for u in list_url():
        # print('爬取单个连接：',u)
        try:
            constent = requests.get(u)

            soup = BeautifulSoup(constent.content, 'lxml')

            link = soup.findAll('dl', {"class": "clear"})

            for dl in link:

                films = dl.findAll('a', {"class": "film"})
                timeTag = dl.findAll('dt',{'class':'nlColor'})
                timeStr = u.replace('https://www.1905.com/mdb/film/calendaryear/','') + '-' + timeTag[0].text.replace('月查看日历>','')

                for film in films:
                    videoTitle = film.get_text()
                    videoId = film['href']
                    videoId = videoId.replace('/mdb/film/','')
                    videoId = videoId.replace('/','')
                    videoUrl = 'https://www.1905.com/mdb/film/' + videoId + '/'

                    itemDict = {'replaceDateTime':timeStr,
                                'videoName': videoTitle,
                                'videoId':videoId,
                                'videoInfoUrl': videoUrl}
                    url_to_work.append(itemDict)

        except:
            print('获取失败')
            pass

        finally:
            startVideoUrl(url_to_work)



def startVideoUrl(videoArray):

    print('总个数：',videoArray.__len__())

    for index, videoDict in enumerate(videoArray):
        if index >= 15:
            print('大于2，停止')
            return
        else:
            print('小于2，继续执行')
            getVideoInfoUrl(videoDict)

# video详情页
def getVideoInfoUrl(videoDict):

    # print('视频详情页URL：' , videoDict)
    url = videoDict['videoInfoUrl']
    constent = requests.get(url)
    soup = BeautifulSoup(constent.content, 'lxml')

    # 上映时间
    videoTimeTag = soup.find('span', {"class": "information-item"})
    videoTime = videoTimeTag.get_text()
    # print("电影上映时间：" + videoTime)
    videoTime = videoTime.replace('(内地)', '')
    videoDict['replaceDateTime'] = videoTime


    # 标签
    videoInformationTag = soup.findAll('div',{'class':'information-list'})
    children = videoInformationTag[0].findAll('a', {'data-hrefexp':'fr=mdbypsy_jsy_lx'})
    typeTagArr = []
    for child in children:
        typeTagArr.append(child.get_text())
    videoDict['videoType'] = typeTagArr

    # 地区
    areaList = videoInformationTag[0].findAll('a', {'data-hrefexp': 'fr=mdbypsy_jsy_gj'})
    videoDict['address'] = areaList[0].get_text()



    # 电影封面
    imgUrls = soup.findAll('img',{'class':'poster'})
    videoDict['coverImgUrl'] = imgUrls[0].get('src')


    getPicInfo(videoDict)



# 剧照
def getPicInfo(videoDict):
    # https://www.1905.com/mdb/film/2214647/still/
    try:
        picUrl = 'https://www.1905.com/mdb/film/' + videoDict['videoId'] + '/still/'
        picConstent = requests.get(picUrl)
        picsoup = BeautifulSoup(picConstent.content, 'lxml')
        picTag = picsoup.findAll('ul', {'class': 'secPag-pics-list clearfloat width-img'})

        picArr = picTag[0].findAll('img')
        photoArr = []
        for imgTag in picArr:
            photoArr.append(imgTag.get('src'))
        videoDict['photoList'] = photoArr

    except:

        pass
    finally:
        get_ScenarioInfo(videoDict)


# 剧情
def get_ScenarioInfo(videoDict):
    # https://www.1905.com/mdb/film/2214647/scenario/
    try:
        Url = 'https://www.1905.com/mdb/film/' + videoDict['videoId'] + '/scenario/'
        Content = requests.get(Url)
        scenarioSoup = BeautifulSoup(Content.content, 'lxml')
        picTag = scenarioSoup.findAll('li', {'class': 'more-infos-plot showInfos'})
        picArr = picTag[0].findAll('p')
        videoDict['scenarioInfo'] = picArr[0].get_text()

    except:
        pass

    finally:
        get_performer(videoDict)

    # print('获取剧情结束:',videoDict)





#演员表
def get_performer(videoDict):
    # https://www.1905.com/mdb/film/2214647/info/
    try:
        Url = 'https://www.1905.com/mdb/film/' + videoDict['videoId'] + '/performer/'
        Content = requests.get(Url)
        performerSoup = BeautifulSoup(Content.content, 'lxml')
        # print('获取演员表结果', performerSoup)
        # return
        titleArr = performerSoup.findAll('h3', {'class': 'title-style-common'})


        directorArr = [] #导演
        writeArr = []  # 编剧
        actorArr = [] #演员

        for title in titleArr:
            titleStr = title.get_text()
            if titleStr.find('导演') != -1:
                parent = title.find_parent('div')
                directors = parent.findAll('img')
                for director in directors:
                    directorName = director.get('alt')
                    directorHeadUrl = director.get('src')
                    directorArr.append({'directorName': directorName, 'directorHeadUrl': directorHeadUrl, 'type': 'director'})

            elif titleStr.find('编剧') != -1:
                parent = title.find_parent('div')
                writes = parent.findAll('img')
                for write in writes:
                    writeName = write.get('alt')
                    writerHeadUrl = write.get('src')
                    writeArr.append(
                        {'writerName': writeName, 'writerHeadUrl': writerHeadUrl, 'type': 'scriptwrite'})

            elif titleStr.find('演员') != -1:
                parent = title.find_parent('div')
                actors = parent.findAll('img')
                for actor in actors:
                    actorName = actor.get('alt')
                    actorHeadUrl = actor.get('src')
                    actorArr.append(
                        {'actorName': actorName, 'actorHeadUrl': actorHeadUrl, 'type': 'actor'})


        # print('获取演员表结果', saveActorArr)
        videoDict['actorList'] = actorArr
        videoDict['writeList'] = writeArr
        videoDict['directorList'] = directorArr

    except:
        pass
    finally:
        # print('获取演员表结果', json.dumps(videoDict))
        saveToLocal(videoDict)


# 详细信息
def get_MoreInfo(videoDict):
    # https://www.1905.com/mdb/film/2214647/info/
    try:
        Url = 'https://www.1905.com/mdb/film/' + videoDict['videoId'] + '/info/'
        Content = requests.get(Url)
        moreInfoSoup = BeautifulSoup(Content.content, 'lxml')
        dtArr = moreInfoSoup.findAll('dt')

        for dt in dtArr:
            titleStr = dt.get_text()
            if titleStr.find('时') != -1 and titleStr.find('长') != -1:
                parent = dt.find_parent('dl')
                times = parent.findAll('dd')
                timeStr = times[0].get_text()
                videoDict['videoTime'] = timeStr
                break

        moreNameArr = moreInfoSoup.findAll('dt',{'class':'more-names'})
        moreChinaNames = []
        moreEngNames = []
        for nameDt in moreNameArr:
            nameTypeStr = nameDt.get_text()
            if nameTypeStr == '更多中文名':
                parent = nameDt.find_parent('dl')
                pTagArr = parent.findAll('p')
                for p in pTagArr:
                    moreChinaNames.append(p.get_text())
            elif nameTypeStr == '更多外文名':
                parent = nameDt.find_parent('dl')
                pTagArr = parent.findAll('p')
                for p in pTagArr:
                    moreEngNames.append(p.get_text())

        videoDict['moreChineseNames'] = moreChinaNames
        videoDict['moreForeignNames'] = moreEngNames

    except:
        pass

    finally:
        print('获取更多信息结束:', videoDict)



# 保存到数据库
def saveToLocal(postData):
    postJson = json.dumps(postData)
    # print('保存：', postJson)
    try:
        header = {'Content-Type':'application/json'}
        constent = requests.post('http://127.0.0.1:5000/addVideos', data=postJson,headers=header)
        print('保存成功：')
    except Exception as e:
        print('保存失败:')
        pass


# postData = {'dateTime': '2013-1', 'videoName': '美国队长3', 'videoId': '2224605', 'videoInfoUrl': 'https://www.1905.com/mdb/film/2214647/'}
# get_MoreInfo(postData) #剧情


start_url() # 1905网站开始方法


# postData = {'dateTime': '2013-1', 'videoName': '孤岛惊魂2', 'videoId': '2214647', 'videoInfoUrl': 'https://www.1905.com/mdb/film/2214647/'}
# saveToLocal(postData)



