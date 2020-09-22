DEBUG = True

DIALCT = 'mysql'
# DRIVER = 'mysqldb'
DRIVER = 'pymysql'
USERNAME = 'root'
PASSWORD = '654321'
HOST = '127.0.0.1'
PORT = '3306'
DBNAME = 'haoVideo'
SQLALCHEMY_DATABASE_URI = '{}+{}://{}:{}@{}:{}/{}?charset=UTF8MB4'.format(DIALCT,DRIVER,USERNAME,PASSWORD,HOST,PORT,DBNAME)
SQLALCHEMY_TRACK_MODIFICATIONS = True        #没有此配置会导致警告