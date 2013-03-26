from flask import Flask, jsonify
from flask import request
from crossdomain import crossdomain
from util import deunicodeData
app = Flask(__name__)
global data
data = {'model': None,
        'simulation_parameters': {}}

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
  data['model'] = request.json
  data['simulation_parameters'] = {}
  app.logger.debug("model: %r" % (data['model'],))
  return "ok"

@app.route("/updateModel", methods=["POST", "OPTIONS"])
@crossdomain(origin='*')
def updateModel():
  app.logger.debug('updateModel')
  data['model'] = request.json
  return "ok"

@app.route("/setSimulationParameters", methods=["POST", "OPTIONS"])
@crossdomain(origin='*')
def setSimulationParameters():
  app.logger.debug('setSimulationParameters')
  parameter_dict = request.json
  app.logger.debug("parameter_dict: %r" % (parameter_dict,))
  data['simulation_parameters']['available_people'] = parameter_dict
  return "ok"

def _simulate():
  # Well, it's only dummy code now, but we will have to think about
  # running simulation later
  box_to_enable_list = [1, 2, 3, 7, 8, 9]
  people_dict = data['simulation_parameters'].get('available_people', {})
  available_people_list = [x for x in people_dict if people_dict[x]]
  to_enable = len(available_people_list) >= 6
  throughput = None
  for box in data['model']["box_list"]:
    box["worker"] = None
    box["enabled"] = False
    if int(box["id"][len("window"):]) in box_to_enable_list:
      box["enabled"] = to_enable
      if to_enable:
        box["worker"] = available_people_list.pop()
        if throughput is None:
          throughput = box["throughput"]
        throughput = min(throughput, box["throughput"])
        app.logger.debug('box and throughput : %r, %r' % (box, throughput))
  if throughput is None:
    throughput = 0
  data['model']["throughput"] = throughput

@app.route("/getModel", methods=["GET", "OPTIONS"])
@crossdomain(origin='*')
def getModel():
  app.logger.debug('getModel')
  _simulate()
  return jsonify(data['model'])

if __name__ == "__main__":
  main()
