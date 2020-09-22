from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:654321@localhost:3306/messageData?charset=UTF8MB4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['SECRET_KEY'] = '123456'

db = SQLAlchemy(app)



# 管理员

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(32),unique=True,index=True,nullable=False)
    password = db.Column(db.String(64),nullable=False)
    tags = db.relationship("Tag",backref="admin")



# 用户
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(32),unique=True,index=True,nullable=False)
    password = db.Column(db.String(64),nullable=False)
    messages = db.relationship("Message",backref="user")

# 留言表
class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    content = db.Column(db.String(256),nullable=False)
    create_time = db.Column(db.DateTime,default=datetime.now)  #时间
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"))
    tags = db.relationship("Tag",secondary="message_to_tag",backref="tag")

# 标签表
class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String(10),nullable=False,unique=True)
    admin_id = db.Column(db.Integer,db.ForeignKey("admin.id"))

# 中间表
class MessageToTag(db.Model):
    __tablename__ = 'message_to_tag'
    id = db.Column(db.Integer,primary_key=True)
    message_id = db.Column(db.Integer,db.ForeignKey("message.id"))
    tag_id = db.Column(db.Integer,db.ForeignKey("tag.id"))

if __name__ == '__main__':
    db.create_all()