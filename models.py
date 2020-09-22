from flask import Flask,json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:654321@localhost:3306/haoVideo?charset=UTF8MB4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['SECRET_KEY'] = '123456'

db = SQLAlchemy(app)


# 用户
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(32),unique=True,index=True,nullable=False)
    password = db.Column(db.String(64),nullable=False)
    create_time = db.Column(db.DateTime,default=datetime.now())

# 电影表
class videos(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    replaceDateTime = db.Column(db.DateTime,index=True)
    videoId = db.Column(db.String(256),unique=True,nullable=False)
    videoName = db.Column(db.String(256),nullable=False)
    videoInfoUrl = db.Column(db.String(256))
    address = db.Column(db.String(256))
    coverImgUrl = db.Column(db.String(256))
    scenarioInfo = db.Column(db.TEXT)
    createTime = db.Column(db.DateTime, default=datetime.now)  # 时间
    photoList = db.relationship('PhotoList',backref="videos",lazy="dynamic",cascade='all, delete-orphan', passive_deletes = True) #剧照
    videoType = db.relationship('VideoTypes',backref="videos",secondary="t_videos_types") #类型
    actorList = db.relationship('ActorList',backref="videos",secondary="t_videos_actors")  # 演员
    directorList = db.relationship('Director',backref="videos",secondary="t_videos_director")  # 导演
    writeList = db.relationship('Writer',backref="videos",secondary="t_videos_writer")  #编剧


# 编剧表
class Writer(db.Model):
    __tablename__ = "writer"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    writerName = db.Column(db.String(256),nullable=False,unique=True)
    writerHeadUrl = db.Column(db.String(256),nullable=False)

# 电影-编剧 中间表
t_videos_writer=db.Table('t_videos_writer',db.Column('video_id',db.String(256),db.ForeignKey("videos.videoId", ondelete='CASCADE')),
                         db.Column('writer_id',db.Integer,db.ForeignKey('writer.id', ondelete='CASCADE')))

# 导演表
class Director(db.Model):
    __tablename__ = "director"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    directorName = db.Column(db.String(256),nullable=False,unique=True)
    directorHeadUrl = db.Column(db.String(512),nullable=False)

# 电影-导演 中间表
t_videos_director=db.Table('t_videos_director',db.Column('video_id',db.String(256),db.ForeignKey('videos.videoId', ondelete='CASCADE')),
                           db.Column('director_id',db.Integer,db.ForeignKey('director.id', ondelete='CASCADE')))

# 演员表
class ActorList(db.Model):
    __tablename__ = "actorlist"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    actorName = db.Column(db.String(256), nullable=False,unique=True)
    actorHeadUrl = db.Column(db.String(256), nullable=False)

# 电影-演员 中间表
t_videos_actors=db.Table('t_videos_actors',db.Column('video_id',db.String(256),db.ForeignKey('videos.videoId', ondelete='CASCADE')),
                         db.Column('actor_id',db.Integer,db.ForeignKey('actorlist.id', ondelete='CASCADE')))


# 类型表
class VideoTypes(db.Model):
    __tablename__ = "videotypes"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    typeName = db.Column(db.String(256),nullable=False,unique=True)

# 电影-类型 中间表
t_videos_types=db.Table('t_videos_types',db.Column('video_id',db.String(256),db.ForeignKey('videos.videoId', ondelete='CASCADE')),
                         db.Column('type_id',db.Integer,db.ForeignKey('videotypes.id', ondelete='CASCADE')))


# 剧照表
class PhotoList(db.Model):
    __tablename__ = 'photolist'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    imgUrl = db.Column(db.String(256),nullable=False)
    videoId = db.Column(db.String(256),db.ForeignKey('videos.videoId',ondelete='CASCADE'))


if __name__ == '__main__':
    # db.drop_all()
    db.create_all()