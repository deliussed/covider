import covider
import json
from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast

app = Flask(__name__)
api = Api(app)

print ("ready")

covider = covider.Covider()

#print (covider.get_results())

class RNumbers(Resource):
    # methods go here
    def get(self):
        #covider = covider.Covider()
        data    = covider.get_results()
        #data    = json.loads(data) # convert dataframe to dict
        return {'data': data}, 200  # return data and 200 OK

api.add_resource(RNumbers, '/rs')  # rs is entrypoint

if __name__=="__main__":
    app.run(host='0.0.0.0',port=4455,debug=True)



#app = Flask(__name__)

#@app.route("/")
#def hello():
#    return "Hello, World!"
