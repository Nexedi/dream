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

import json
import sys


def get_name(node):
  name = node.get_name()
  if name.startswith('"') and name.endswith('"'):
    name = name[1:-1]
  return name

def positionGraph(g):
  import pydot
  graph = pydot.Dot()
  for node in g['nodes']:
    graph.add_node(pydot.Node(node))
  for edge, (source, destination, data) in g['edges'].items():
    graph.add_edge(pydot.Edge(source, destination))

  new_graph = pydot.graph_from_dot_data(graph.create_dot())

  # calulate the ratio from the size of the bounding box
  ratio = new_graph.get_bb()
  origin_left, origin_top, max_left, max_top = [float(p) for p in
    new_graph.get_bb()[1:-1].split(',')]
  ratio_top = max_top - origin_top
  ratio_left = max_left - origin_left

  preference_dict = dict()
  for node in new_graph.get_nodes():
    # skip technical nodes
    if node.get_name() in ('graph', 'node', 'edge'):
      continue
    left, top = [float(p) for p in node.get_pos()[1:-1].split(",")]
    preference_dict[get_name(node)] = dict(
      top=1-(top/ratio_top),
      left=1-(left/ratio_left),)
  return preference_dict

def format(m):
  for node in m['nodes'].values():
    if node['_class'] in ('Dream.Source', 'Dream.BatchSource'):
      interarrivalTime = node['interarrivalTime']
      print interarrivalTime
      interarrivalTime['mean'] = float(interarrivalTime['mean'])
      entity = node['entity']
      if not entity.startswith('Dream.'):
        node['entity'] = 'Dream.%s' % entity

  return m

with open(sys.argv[1]) as infile:
  m = json.load(infile)

m.update(format(m))
#m.update(preferences=positionGraph(m))

with open(sys.argv[1], "w") as outfile:
  json.dump(m, outfile, sort_keys=True,
            indent=4, separators=(',', ': '))




