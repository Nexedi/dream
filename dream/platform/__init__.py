import json
from pprint import pformat
from flask import Flask, jsonify, redirect, url_for
from flask import request

from dream.simulation.LineGenerationJSON import main as simulate_line_json

app = Flask(__name__)

@app.route("/")
def front_page():
  return redirect(url_for('static', filename='index.html'))

@app.route("/runSimulation", methods=["POST", "OPTIONS"])
def runSimulation():
  parameter_dict = request.json['json']
  app.logger.debug("running with:\n%s" % (pformat(parameter_dict,)))
  return jsonify(json.loads(simulate_line_json(input_data=json.dumps(parameter_dict))))

def main(*args):
  app.run(debug=True)

if __name__ == "__main__":
  main()
