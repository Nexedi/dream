# ===========================================================================
# Copyright 2013 Nexedi SA
#
# This file is part of DREAM.
#
# DREAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DREAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with DREAM.  If not, see <http://www.gnu.org/licenses/>.
# ===========================================================================

import sys
import os
import argparse
import json
import urllib
import xlrd
import traceback
import multiprocessing
import Queue
from dream.KnowledgeExtraction.DistributionFitting import DistFittest
from dream.KnowledgeExtraction.ImportExceldata import ImportExceldata
from dream.plugins.plugin import PluginRegistry

import os.path
import logging
import simpy

from flask import Flask
from flask import request
from flask import jsonify, redirect, url_for
from flask.json import JSONEncoder

app = Flask(__name__)

class InfinityJSONEncoder(JSONEncoder):
  # we don't serialise inf, as javascript does not load it.
  def iterencode(self, *args, **kw):
    for j in JSONEncoder.iterencode(self, *args, **kw):
      if "Infinity" in str(j): # XXX the replace should not be so "global"
        j = j.replace("Infinity", str(2**64))
      yield j
app.json_encoder = InfinityJSONEncoder

@app.route("/")
def front_page():
  return redirect(url_for('static', filename='dream/index.html'))

@app.route("/positionGraph", methods=["POST", "OPTIONS"])
def positionGraph():
  """Uses graphviz to position nodes of the graph.
  """
  try:
    import pydot
  except ImportError:
    return jsonify({})

  graph = pydot.Dot()

  for node_id, node in request.json['nodes'].iteritems():
    graph.add_node(pydot.Node(node_id))
  for edge in request.json['edges'].itervalues():
    graph.add_edge(pydot.Edge(edge[0], edge[1]))

  new_graph = pydot.graph_from_dot_data(graph.create_dot())

  # calulate the ratio from the size of the bounding box
  ratio = new_graph.get_bb()
  origin_left, origin_top, max_left, max_top = [float(p) for p in
    new_graph.get_bb().strip('"').split(',')]
  ratio_top = max_top - origin_top
  ratio_left = max_left - origin_left

  preference_dict = dict()
  for node in new_graph.get_nodes():
    # skip technical nodes
    if node.get_name() in ('graph', 'node', 'edge'):
      continue
    left, top = [float(p) for p in node.get_pos()[1:-1].split(",")]
    preference_dict[node.get_name().strip('"')] = dict(
      top=1-(top/ratio_top),
      left=1-(left/ratio_left),)

  return jsonify(preference_dict)

class TimeoutError(Exception):
  pass

def runWithTimeout(func, timeout, *args, **kw):
  queue = multiprocessing.Queue()
  process = multiprocessing.Process(
    target=_runWithTimeout,
    args=(queue, func, args, kw))
  process.start()
  try:
    return queue.get(timeout=timeout)
  except Queue.Empty:
    process.terminate()
    raise TimeoutError()
  finally:
    process.join()

def _runWithTimeout(queue, func, args, kw):
  import signal
  import traceback

  if hasattr(signal, 'SIGUSR1'):
    signal.signal(signal.SIGUSR1, lambda sig, stack: traceback.print_stack(stack))
    print "To see current traceback:"
    print "  kill -SIGUSR1 %s" % os.getpid()

  # print a traceback when terminated.
  def handler(sig, stack):
    app.logger.error("Terminating")
    app.logger.info("".join(traceback.format_stack(stack)))
    sys.exit(0)
  signal.signal(signal.SIGTERM, handler)

  queue.put(func(*args, **kw))

@app.route("/postJSONData", methods=["POST", "OPTIONS"])
def postJSONData():
  """Returns posted JSON data as it is for Export button"""
  data = json.loads(request.form.get('data'))
  response = jsonify(data)
  response.headers['Content-Disposition'] = 'attachment; filename=dream.json'
  return response

@app.route("/runSimulation", methods=["POST", "OPTIONS"])
def runSimulation():
  parameter_dict = request.json
  try:
    timeout = int(parameter_dict['general']['processTimeout'])
  except (KeyError, ValueError, TypeError):
    timeout = 60

  try:
    result = runWithTimeout(_runSimulation, timeout, parameter_dict)
    return jsonify(result)
  except TimeoutError:
    return jsonify(dict(error="Timeout after %s seconds" % timeout))

def _runSimulation(parameter_dict):
  try:
    registry = PluginRegistry(app.logger, parameter_dict)
    return dict(success=True, data=registry.run(parameter_dict))
  except Exception:
    # Use simpy._compat to format exception chain in python2
    if hasattr(simpy._compat, 'format_chain'):
      exc_type, exc_value, exc_traceback = sys.exc_info()
      tb = ''.join(simpy._compat.format_chain(exc_type, exc_value, exc_traceback))
    else:
#       assert sys.version_ == 3
      tb = traceback.format_exc()
    app.logger.error(tb)
    return dict(error=tb)

@app.route("/runKnowledgeExtraction", methods=["POST", "OPTIONS"])
def runKnowledgeExtraction():
  parameter_dict = request.json
  try:
    timeout = int(parameter_dict['general']['processTimeout'])
  except (KeyError, ValueError, TypeError):
    timeout = 60

  try:
    result = runWithTimeout(_runKnowledgeExtraction, timeout, parameter_dict)
    return jsonify(result)
  except TimeoutError:
    return jsonify(dict(error="Timeout after %s seconds" % timeout))

def _runKnowledgeExtraction(parameter_dict):
  try:
    workbook = xlrd.open_workbook(
        file_contents=urllib.urlopen(parameter_dict['general']['ke_url']).read())
    worksheets = workbook.sheet_names()
    worksheet_ProcessingTimes = worksheets[0]   #It defines the worksheet_ProcessingTimes as the first sheet of the Excel file

    A=ImportExceldata()            #Call the Import_Excel object 
    B=DistFittest()             #Call the Distribution Fitting object
    ProcessingTimes= A.Input_data(worksheet_ProcessingTimes, workbook)  #Create a dictionary with the imported data from the Excel file

    data = parameter_dict                            #It loads the file
#     nodes = data['nodes'] 
    nodes = data['graph']['node']

    for station, values in ProcessingTimes.items():             #This loop searches the elements of the Excel imported data and if these elements exist in json file append the distribution fitting results in a dictionary   
      if station in nodes: 
        temp= B.ks_test(values)
        dist=temp['distributionType']
        del temp['distributionType']
        temp={dist:temp, "distribution": dist}
        from pprint import pprint
        pprint(temp)
        parameter_dict['graph']['node'][station]['processingTime'] = temp
    return dict(success=True, data=parameter_dict)
  except Exception, e:
    tb = traceback.format_exc()
    app.logger.error(tb)
    return dict(error=tb)

def main(*args):
  parser = argparse.ArgumentParser(description='Launch the DREAM simulation platform.')
  parser.add_argument('--port', default=5000, type=int,
                      help='Port number to listen on')
  parser.add_argument('--host', default="127.0.0.1", help='Host address')
  parser.add_argument('--logfile', help='Log to file')
  parser.add_argument('--debug', help='Debug mode', action='store_true')
  arguments = parser.parse_args()
  if arguments.logfile:
    file_handler = logging.FileHandler(arguments.logfile)
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)

  if arguments.debug:
    # Serve static file with no cache
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

  # start the server
  app.run(debug=arguments.debug, host=arguments.host, port=arguments.port, threaded=True)

if __name__ == "__main__":
  main()
