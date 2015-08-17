from flask import Flask
application = Flask(__name__)


@application.route('/')
@application.route('/index')
def index():
    return "hello world"



if __name__ == "__main__":
    application.run(debug=False)
