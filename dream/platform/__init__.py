import json
import traceback
import multiprocessing

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

  try:
    timeout = int(parameter_dict['general']['processTimeout'])
  except (KeyError, ValueError, TypeError):
    timeout = 60

  queue = multiprocessing.Queue()
  process = multiprocessing.Process(
    target=_runSimulation,
    args=(parameter_dict, queue))
  process.start()
  process.join(timeout)
  if process.is_alive():
    # process still alive after timeout, terminate it
    process.terminate()
    process.join()
    return jsonify(dict(error='Timeout after %s seconds' % timeout))

  return jsonify(queue.get())

def _runSimulation(parameter_dict, queue):
  try:
    result = simulate_line_json(input_data=json.dumps(parameter_dict))
    queue.put(dict(success=json.loads(result)))
  except Exception, e:
    tb = traceback.format_exc()
    app.logger.error(tb)
    queue.put(dict(error=tb))


def main(*args):
  app.run(debug=True)

if __name__ == "__main__":
  main()
