from flask import Flask, jsonify
from flask import request
from crossdomain import crossdomain
from util import deunicodeData
app = Flask(__name__)
global model

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
  global model
  app.logger.debug('setModel')
  app.logger.debug("request.json: %r" % (request.json,))
  #model = deunicodeData(request.json)
  model = request.json
  app.logger.debug("model: %r" % (model,))
  return "ok"

@app.route("/setSimulationParameters", methods=["POST", "OPTIONS"])
@crossdomain(origin='*')
def setSimulationParameters():
  app.logger.debug('setSimulationParameters')
  parameter_dict = request.json
  app.logger.debug("parameter_dict: %r" % (parameter_dict,))
  box_to_enable_list = [1, 2, 3, 7, 8, 9]
  to_enable = len([x for x in parameter_dict if parameter_dict[x]]) >= 6
  for box in model["box_list"]:
    if int(box["id"][len("window"):]) in box_to_enable_list:
      box["enabled"] = to_enable
    else:
      box["enabled"] = False
  return "ok"

@app.route("/getModel", methods=["GET", "OPTIONS"])
@crossdomain(origin='*')
def getModel():
  global model
  app.logger.debug('getModel')
  return jsonify(model)

if __name__ == "__main__":
  main()
