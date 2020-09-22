# 获取某年月的所有电影 /get_video/month?year=2013&month=01
@app.route("/get_video/month")
def get_video_month():
    yearStr = request.args.get("year")
    monthStr = request.args.get("month")
    try:
        one = extract('year', videos.replaceDateTime)
        two = extract('month', videos.replaceDateTime)
        # print(one)
        # print(two)

        videosRes = videos.query.filter(and_(one == yearStr, two == monthStr)).all()
        # videosRes = videos.query.filter(db.cast(videos.replaceDateTime, db.DATE) == db.cast('{dateMonth}'.format(dateMonth=dateMonthStr),db.DATE)).all()
        videoList = []
        for video in videosRes:
            # 剧照
            photoArr = []
            for photo in video.photoList:
                photoArr.append(photo.imgUrl)

            # 类型
            typeArr = []
            for ty in video.videoType:
                typeArr.append(ty.typeName)

            # 演员
            actorArr = []
            for ac in video.actorList:
                actorArr.append({"actorName": ac.actorName, "actorHeadUrl": ac.actorHeadUrl})
            # 编剧
            writerArr = []
            for wr in video.writeList:
                writerArr.append({"writerName": wr.writerName, "writerHeadUrl": wr.writerHeadUrl})
            # 导演
            directorArr = []
            for di in video.directorList:
                directorArr.append({"directorName": di.directorName, "directorHeadUrl": di.directorHeadUrl})

            data = {
                "id": video.id,
                "videoName": video.videoName,
                "videoId": video.videoId,
                "replaceDateTime": video.replaceDateTime,
                "videoInfoUrl": video.videoInfoUrl,
                "address": video.address,
                "coverImgUrl": video.coverImgUrl,
                "scenarioInfo": video.scenarioInfo,
                "createTime": video.createTime,
                "photoList": photoArr,
                "videoType": typeArr,
                "actorList": actorArr,
                "writerList": writerArr,
                "directorList": directorArr
            }
            videoList.append(data)
        return jsonify(code=200, msg="查询成功",data=videoList)

    except Exception as e:
        print(e)
        return jsonify(code=400,msg="查询错误")
