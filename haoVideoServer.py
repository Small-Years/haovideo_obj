from flask import Flask

app = Flask(__name__)

@app.route('/',methods=['GET'])
def hello_world():
    return 'Hello World! haoVideos'



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')



