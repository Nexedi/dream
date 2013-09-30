
import json
import pydot


def get_name(node):
  name = node.get_name()
  if name.startswith('"') and name.endswith('"'):
    name = name[1:-1]
  return name

def positionGraph(g):
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
  edges = m.pop('edges')
  m['edges'] = {}
  for i, (s, d, data) in enumerate(edges):
    m['edges'][i] = d, s, data
  return m

with open(sys.argv[1]) as infile:
  m = json.load(infile)
m.update(format(m))
m.update(preferences=positionGraph(m))
print m
with open(sys.argv[1], "w") as outfile:
  json.dump(m, outfile, sort_keys=True,
            indent=4, separators=(',', ': '))




