from flask import Flask


app = Flask(__name__)


@app.route("/")
def index():
    """ home page """
    return "Hello World!"
