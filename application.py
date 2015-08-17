from flask import Flask, render_template, url_for
application = Flask(__name__)


@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
    
    
    
    #return "hey, you made it to this point"



if __name__ == "__main__":
    application.run(debug=False)
