from flask import Flask, jsonify
from flask import request
from crossdomain import crossdomain
from util import deunicodeData
app = Flask(__name__)

@app.route("/")
def welcome():
    app.logger.debug('welcome')
    return "Welcome to DREAM Simulation"

@app.route("/addModel")
def addModel():
  pass

def main(*args):
  app.run(debug=True)

@app.route("/someTest", methods=["POST", "OPTIONS"])
@crossdomain(origin='*')
def someTest():
  app.logger.debug('someTest')
  app.logger.debug(request)
  app.logger.debug(request.__dict__)
  app.logger.debug("request headers content type: %r" % (request.headers['Content-Type'],))
  app.logger.debug("request.json: %r" % (request.json,))
  response =request.json
  return jsonify(request.json)

@app.route("/setModel", methods=["POST", "OPTIONS"])
@crossdomain(origin='*')
def setModel():
  app.logger.debug('setModel')
  app.logger.debug("request.json: %r" % (request.json,))
  model = request.json
  app.logger.debug("model: %r" % (model,))
  response =request.json
  return jsonify(request.json)

if __name__ == "__main__":
  main()
