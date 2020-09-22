from flask import request, jsonify, session
from models import app, db, User, videos, VideoTypes, PhotoList,ActorList,Director,Writer
from sqlalchemy import extract,and_
from Tool import queryToDict,remove_duplicate

@app.route("/")
def hello_word():
    return "hello Word! haoVideos"

@app.route("/addVideos", methods=["POST"])
# 添加video记录
def add_videos():
    req_Data = request.get_json()

    videoIdStr = req_Data.get("videoId")
    videoName = req_Data.get("videoName")
    replaceDateTimeStr = req_Data.get("replaceDateTime")
    videoInfoUrl = req_Data.get("videoInfoUrl")
    videoTypeStr = req_Data.get("videoType")
    address = req_Data.get("address")
    coverImgUrl = req_Data.get("coverImgUrl")
    photoListStr = req_Data.get("photoList")
    scenarioInfo = req_Data.get("scenarioInfo")

    # actorListStr = req_Data.get("actorList")
    # writeListStr = req_Data.get("writeList")
    # directorListStr = req_Data.get("directorList")
    actorListStr = remove_duplicate(req_Data.get("actorList"), "actorName", "actorHeadUrl")
    writeListStr = remove_duplicate(req_Data.get("writeList"), "writerName", "writerHeadUrl")
    directorListStr = remove_duplicate(req_Data.get("directorList"), "directorName", "directorHeadUrl")
    # print("传过来的数据处理前：", req_Data.get("actorList"))
    # print("传过来的数据处理后：", actorListStr)
    if not all(['videoId', 'videoName']):
        return jsonify(code=400, msg='参数不完整')

    videoItem = videos(videoId=videoIdStr,
                       videoName=videoName,
                       videoInfoUrl=videoInfoUrl,
                       address=address,
                       coverImgUrl=coverImgUrl,
                       scenarioInfo=scenarioInfo,
                       replaceDateTime = replaceDateTimeStr
                       )

    needSaveArr = []
    # 剧照
    for urlStr in photoListStr:
        ph = PhotoList(imgUrl=urlStr, videoId=videoIdStr)
        videoItem.photoList.append(ph)

    # 类型
    type_list = []
    for typeItem in videoTypeStr:
        if VideoTypes.query.filter_by(typeName=typeItem).first():
            type_list.append(VideoTypes.query.filter_by(typeName=typeItem).first())
        else:
            type_list.append(VideoTypes(typeName=typeItem))
    videoItem.videoType = type_list

    # 演员
    list_actors = []

    for actorItem in actorListStr:
        acName = actorItem.get('actorName')
        acUrl = actorItem.get('actorHeadUrl')
        if ActorList.query.filter_by(actorName=acName).first():
            list_actors.append(ActorList.query.filter_by(actorName=acName).first())
        else:
            list_actors.append(ActorList(actorName=acName,actorHeadUrl=acUrl))
    videoItem.actorList = list_actors

    # 编剧
    list_writers = []
    for writerItem in writeListStr:
        wrName = writerItem.get('writerName')
        wrUrl = writerItem.get('writerHeadUrl')
        if Writer.query.filter_by(writerName=wrName).first():
            list_writers.append(Writer.query.filter_by(writerName=wrName).first())
        else:
            list_writers.append(Writer(writerName=wrName, writerHeadUrl=wrUrl))
    videoItem.writeList = list_writers

    # 导演
    list_directors = []
    for directorItem in directorListStr:
        diName = directorItem.get('directorName')
        diUrl = directorItem.get('directorHeadUrl')
        if Director.query.filter_by(directorName=diName).first():
            list_directors.append(Director.query.filter_by(directorName=diName).first())
        else:
            list_directors.append(Director(directorName=diName, directorHeadUrl=diUrl))
    videoItem.directorList = list_directors

    needSaveArr.insert(0, videoItem)

    try:
        db.session.add_all(needSaveArr)
        db.session.commit()
        return jsonify(code=200, msg=videoName + ':保存成功')
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify(code=400, msg=videoName + ':失败')

# 删除视频
@app.route("/deletevideo",methods=["DELETE"])
def delete_video_item():
    req_data = request.get_json()
    videoIdStr = req_data.get('videoId')
    video = videos.query.filter_by(videoId=videoIdStr).first()
    if video:
        try:
            db.session.delete(video)
            db.session.commit()
            return jsonify(code=200, msg=video.videoName + '删除成功!')
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify(code = 400,msg='删除失败!')
    else:
        return jsonify(code=400, msg='视频不存在!')


# 获取某年月的所有电影 /get_video/month?year=2013&month=01
@app.route("/get_video/month")
def get_video_month():
    yearStr = request.args.get("year")
    monthStr = request.args.get("month")
    try:
        one = extract('year', videos.replaceDateTime)
        two = extract('month', videos.replaceDateTime)

        videosRes = videos.query.filter(and_(one == yearStr, two == monthStr)).all()
        newList = queryToDict(videosRes)
        # print(newList)
        return jsonify(code=200, data=newList)

    except Exception as e:
        print(e)
        return jsonify(code=400,msg="查询错误")


# 获取列表
@app.route("/get_video/all")
def get_video_all():
    req_data = request.args
    pageNo = req_data.get("pageNo")
    pageSize = req_data.get("pageSize")

    try:
        videosRes = []
        if pageNo and pageSize:
            print('分页访问')
            videosRes = videos.query.paginate(page=int(pageNo),per_page=int(pageSize)).items
        else:
            print('不分页')
            videosRes = videos.query.all()
            
        newList = queryToDict(videosRes)
        # print(newList)
        return jsonify(code=200, data=newList)
    except Exception as e:
        print(e)
        return jsonify(code=400, msg="获取列表失败")





if __name__ == "__main__":
    app.run()
