from flask import jsonify, request, session
from message_Models import app,db,User,Admin,Tag,Message


@app.route("/")
def hello_word():
    return 'hello MessageData!'

# 管理员初始化
@app.route("/admin/init")
def init_admin():
    admin = Admin(username='admin',password="admin")
    try:
        db.session.add(admin)
        db.session.commit()
        return jsonify(code=200,msg="初始化管理员成功！")
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(code=400,msg="初始化管理员失败！")

# 管理员登录
@app.route("/admin/login",methods=["POST"])
def login_admin():
    req_data = request.get_json()
    user_name = req_data.get("username")
    passwordStr = req_data.get("password")
    if not all(['username','password']):
        return jsonify(code=400,msg="参数不完整！")
    # 查找管理员数据库
    admin = Admin.query.filter(Admin.username == user_name).first()
    if admin is None or passwordStr != admin.password:
        return jsonify(code=400,msg="账号或密码不正确")

    session['admin_name'] = user_name
    session['admin_id'] = admin.id
    return jsonify(code=200,msg="登录成功")

#检查管理员登录状态
@app.route("/admin/checksession")
def check_admin_session():
    admin_name = session.get("admin_name")
    admin_id = session.get("admin_id")
    if admin_name is not None:
        return jsonify(adminname=admin_name,adminid=admin_id)
    else:
        return jsonify(msg="出错了，没登录！")

# 管理员退出登录
@app.route("/admin/logout")
def logout_admin():
    session.clear()
    return jsonify(code=200,msg="退出登录成功！")

# 管理员增标签
@app.route("/admin/tag",methods=["POST"])
def add_tag():
    """
    tag_name
    :return: 
    """
    req_data = request.get_json()
    tagname = req_data.get("tag_name")
    admin_id = session.get("admin_id")
    if not all([tagname,admin_id]):
        return jsonify(code=400,msg="参数不完整或者未登录")
    tag = Tag(name=tagname,admin_id=admin_id)
    try:
        db.session.add(tag)
        db.session.commit()
        return jsonify(code=200,msg="添加标签成功！")
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(code=400,msg="添加标签失败！")

# 管理员删标签
@app.route("/admin/tag",methods=["DELETE"])
def delete_tag():
    req_data = request.get_json()
    tagname = req_data.get("tag_name")
    admin_id = session.get("admin_id")
    if not all([tagname, admin_id]):
        return jsonify(code=400, msg="参数不完整或者未登录")
    tag = Tag.query.filter(Tag.name==tagname).delete()
    try:
        db.session.commit()
        return jsonify(code=200, msg="删除标签成功！")
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(code=400, msg="删除标签失败！")

    pass
# 管理员删留言
@app.route("/admin/message",methods=["DELETE"])
def delete_message():
    req_data = request.get_json()
    message_id = req_data.get("message_id")
    admin_id = session.get("admin_id")

    if not all([message_id, admin_id]):
        return jsonify(code=400, msg="参数不完整")

    msg = Message.query.get(message_id)
    if msg is None:
        return jsonify(code=400, msg="留言不存在，无法删除")
    if admin_id is None:
        return jsonify(code=400, msg="管理员未登录，无法删除")
    try:
        m = Message.query.filter(Message.id == message_id).delete()
        db.session.commit()
        return jsonify(code=200, msg="删除成功！")
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(code=400, msg="删除失败！")
    pass



# 用户注册
@app.route("/user/register",methods=["POST"])
def user_register():
    req_data = request.get_json()
    username = req_data.get('username')
    password = req_data.get('password')
    user = User(username=username, password=password)
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(code=200, msg="用户注册成功！")
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(code=400, msg="用户注册失败！")

# 用户登录
@app.route("/user/login",methods=["POST"])
def user_login():
    req_data = request.get_json()
    user_name = req_data.get("username")
    passwordStr = req_data.get("password")
    if not all(['username', 'password']):
        return jsonify(code=400, msg="参数不完整！")

    user = User.query.filter(User.username == user_name).first()
    if user is None or passwordStr != user.password:
        return jsonify(code=400, msg="账号或密码不正确")

    session['user_name'] = user_name
    session['user_id'] = user.id
    return jsonify(code=200, msg="登录成功")

#检查管理员登录状态
@app.route("/user/checksession",methods=["GET"])
def check_user_session():
    user_name = session.get("user_name")
    user_id = session.get("user_id")
    if user_name is not None:
        return jsonify(user_name=user_name,user_id=user_id)
    else:
        return jsonify(msg="出错了，用户没登录！")

# 用户退出登录
@app.route("/user/logout")
def user_logout():
    session.clear()
    return jsonify(code=200,msg="退出登录成功！")

# 用户发布留言
@app.route("/user/message",methods=["POST"])
def user_post_message():
    req_data = request.get_json()
    content = req_data.get("content")
    tags = req_data.get("tags")
    user_id = session.get("user_id")
    if not all([content,tags]):
        return jsonify(code=400,msg="参数不完整")
    try:
         tags = Tag.query.filter(Tag.name.in_(tags)).all()
         message = Message(content=content,user_id=user_id)
         message.tags = tags
         db.session.add(message)
         db.session.commit()
         return jsonify(code=200,msg="发布留言成功！")
    except Exception as e:
        print(e)
        return jsonify(code = 400,msg="发布留言失败！")

# 用户删除留言
@app.route("/user/message",methods=["DELETE"])
def user_delete_message():
    '''
    messageid 留言的id
    userid 判断是不是原主人
    :return: 
    '''
    req_data = request.get_json()
    message_id = req_data.get("message_id")
    user_id = session.get("user_id")

    if not all([message_id,user_id]):
        return jsonify(code=400,msg="参数不完整")

    msg = Message.query.get(message_id)
    if msg is None:
        return jsonify(code=400,msg="留言不存在，无法删除")

    if user_id != msg.user.id:
        return jsonify(code=400,msg="你不是作者，无法删除该条留言")

    try:
        m = Message.query.filter(Message.id == message_id).delete()
        db.session.commit()
        return jsonify(code=200,msg="删除成功！")
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(code=400,msg="删除失败！")


    # 用户查看自己的留言记录
@app.route("/user/message/history",methods=["GET"])
def user_message_history():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify(code=400,msg="用户未登录！")

    messages = Message.query.filter(Message.user_id == user_id)
    playload = []
    for message in messages:
        content = message.content
        tags = message.tags
        tag_names = []
        for tag in tags:
            tag_names.append(tag.name)

        create_time = message.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        user_id = message.user_id
        data = {"content": content,
                "message_id": message.id,
                "tags": tag_names,
                "create_time": create_time,
                "user_id": user_id}
        playload.append(data)
    return jsonify(code=200, msg="查询成功！", data=playload)

# 留言区留言板
@app.route("/user/message/board",methods=["GET"])
def user_message_board():
    messages = Message.query.all()
    playload = []
    for message in messages:
        content = message.content
        tags = message.tags
        tag_names = []
        for tag in tags:
            print(tag)
            tag_names.append(tag.name)

        create_time = message.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        user_id = message.user_id
        data = {"content":content,
                "message_id":message.id,
                "tags":tag_names,
                "create_time":create_time,
                "user_id":user_id}
        print(data)
        playload.append(data)
    return jsonify(code=200,msg="查询成功！",data=playload)








if __name__ =="__main__":
    app.run(host='0.0.0.0')