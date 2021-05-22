import covider
from flask import Flask

print ("ready")

covider = covider.Covider()

print (covider.get_results())

#app = Flask(__name__)

#@app.route("/")
#def hello():
#    return "Hello, World!"
