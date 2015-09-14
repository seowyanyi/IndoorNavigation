import json
import urllib2
import networkx as nx
import matplotlib.pyplot as plt
import math

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
# Write the source nodeID in the format (buildingName-levelNum-nodeID)
src= 14
# Write the destination nodeId in the format (buildingName-levelNum-nodeID)
dest= 44

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
# Download and parse all available maps
#--------------------------------------------------------------------------------------------------------------------------------------------------------------

data_COM1_2 = json.load(urllib2.urlopen('http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building=COM1&Level=2'))
data_COM2_2 = json.load(urllib2.urlopen('http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building=COM2&Level=2'))
data_COM2_3 = json.load(urllib2.urlopen('http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building=COM2&Level=3'))

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
# All the initialisations of constants
#--------------------------------------------------------------------------------------------------------------------------------------------------------------

i=0
m=0
n=0
p=0
coords_src_x=0
coords_dest_x=0
coords_src_y=0
coords_dest_y=0

edge_weight=0
edge_dest=0
edge_src=0

G=nx.Graph()

length_map_COM1_2 = len(data_COM1_2["map"])
length_map_COM2_2 = len(data_COM2_2["map"])
length_map_COM2_3 = len(data_COM2_3["map"])

arrayObj = []

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
# Defining an object called checkpoint which holds all the information from the JSON file
#--------------------------------------------------------------------------------------------------------------------------------------------------------------

class Checkpoint(object):
    nodeId = 0
    x_coord = 0
    y_coord = 0
    nodeName = ""
    linkTo = [10]
    
    # The class "constructor" - It's actually an initializer
    def __init__(self, nodeId, x_coord, y_coord, nodeName, linkTo):
        self.nodeId = nodeId
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.nodeName = nodeName
        self.linkTo = linkTo.split(', ')

def make_checkpoint(nodeId, x_coord, y_coord, nodeName, linkTo):
    checkpoint = Checkpoint(nodeId, x_coord, y_coord, nodeName, linkTo)
    return checkpoint

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
# Iterates through the JSON files, creates the 'checkpoint' object and adds them to an array.
# This also adds the nodeID of the node into a Graph
#--------------------------------------------------------------------------------------------------------------------------------------------------------------

i=0
while True:
    if i == length_map_COM1_2:
        break
    checkpoint = make_checkpoint(data_COM1_2["map"][i]["nodeId"], data_COM1_2["map"][i]["x"], data_COM1_2["map"][i]["y"], data_COM1_2["map"][i]["nodeName"], data_COM1_2["map"][i]["linkTo"])
    checkpoint.nodeId = "COM1-2-%s" %checkpoint.nodeId
    arrayObj.append(checkpoint)
    G.add_node(checkpoint.nodeId)

    #Iterates through the nodeIds given in the linkTo and creates edges between the 2 points
    length_linkTo = len(checkpoint.linkTo)
    j=0
    while True:
        if j == length_linkTo:
            break
        checkpoint.linkTo[j] = "COM1-2-%s" %checkpoint.linkTo[j]
        G.add_edge(checkpoint.nodeId, checkpoint.linkTo[j])
        j = j+1

    i = i+1
#--------------------------------------------------------------------------------------------------------------------------------------------------------------

i=0
while True:
    if i == length_map_COM2_2:
        break
    checkpoint = make_checkpoint(data_COM2_2["map"][i]["nodeId"], data_COM2_2["map"][i]["x"], data_COM2_2["map"][i]["y"], data_COM2_2["map"][i]["nodeName"], data_COM2_2["map"][i]["linkTo"])
    checkpoint.nodeId = "COM2-2-%s" %checkpoint.nodeId
    arrayObj.append(checkpoint)
    G.add_node(checkpoint.nodeId)

    length_linkTo = len(checkpoint.linkTo)
    j=0
    while True:
        if j == length_linkTo:
            break
        checkpoint.linkTo[j] = "COM2-2-%s" %checkpoint.linkTo[j]
        G.add_edge(checkpoint.nodeId, checkpoint.linkTo[j])
        j = j+1

    i = i+1
#--------------------------------------------------------------------------------------------------------------------------------------------------------------

i=0
while True:
    if i == length_map_COM2_3:
        break
    checkpoint = make_checkpoint(data_COM2_3["map"][i]["nodeId"], data_COM2_3["map"][i]["x"], data_COM2_3["map"][i]["y"], data_COM2_3["map"][i]["nodeName"], data_COM2_3["map"][i]["linkTo"])
    checkpoint.nodeId = "COM2-3-%s" %checkpoint.nodeId
    arrayObj.append(checkpoint)
    G.add_node(checkpoint.nodeId)

    length_linkTo = len(checkpoint.linkTo)
    j=0
    while True:
        if j == length_linkTo:
            break
        checkpoint.linkTo[j] = "COM2-3-%s" %checkpoint.linkTo[j]
        G.add_edge(checkpoint.nodeId, checkpoint.linkTo[j])
        j = j+1

    i = i+1
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
# Iterates through the data to find nodes which have nodeNames like "TO COM1-2-11" and create and edge between this and the next one using weight of 1
#--------------------------------------------------------------------------------------------------------------------------------------------------------------

length = len(arrayObj)
print length
while True:
    if p == length:
        break
    if "TO" in arrayObj[p].nodeName:
        nextLevelNode = (arrayObj[p].nodeName).split(' ')
        nextLevelNode = str(nextLevelNode[1])
        G.add_edge(arrayObj[p].nodeId, nextLevelNode, weight=1)
    p = p+1

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
# Iterates through all the existing edges and calculates the weight using the coordinates given in the JSON file.
# Then adds this edge weight to the edge
#--------------------------------------------------------------------------------------------------------------------------------------------------------------

while True:
    if m == length:
        break
    nodeEdge_src = arrayObj[m].nodeId
    nodeEdge_dest = arrayObj[n].nodeId
    if G.has_edge(nodeEdge_src, nodeEdge_dest):
        coords_src_x = int(arrayObj[m].x_coord)
        coords_src_y = int(arrayObj[m].y_coord)
        coords_dest_x = int(arrayObj[n].x_coord)
        coords_dest_y = int(arrayObj[n].y_coord)
        edge_weight = math.sqrt(math.pow((coords_dest_x-coords_src_x), 2)+math.pow((coords_dest_y-coords_src_y),2))
        G[nodeEdge_src][nodeEdge_dest]['weight']=edge_weight
    if n == length-1:
        m=m+1
        n=0
    n=n+1

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
# Given the source and destination NodeId, the shortest route and the shortest route is calculated
#--------------------------------------------------------------------------------------------------------------------------------------------------------------

path = nx.dijkstra_path(G, arrayObj[src-1].nodeId, arrayObj[dest-1].nodeId, 'weight')
print path
print nx.dijkstra_path_length(G, arrayObj[src-1].nodeId, arrayObj[dest-1].nodeId, 'weight')

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
# Draws out the graph using the MatPlotLib
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
pos = nx.spring_layout(G)
nx.draw_networkx(G, pos, node_color='y')
path_edges = zip(path,path[1:])
nx.draw_networkx_nodes(G,pos,nodelist=path,node_color='r')
nx.draw_networkx_edges(G,pos,edgelist=path_edges,edge_color='r',width=5)
plt.show()
#--------------------------------------------------------------------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
# Public APIs
#--------------------------------------------------------------------------------------------------------------------------------------------------------------

def download_map(buildingName, levelNum):
    """
    Returns a python dictionary of the downloaded map
    :param buildingName: string
    :param levelNum: integer
    """
    print 'do your stuff here'


def find_shortest_path(sourceBuilding, sourceLevel, sourceNodeId,
                       destBuilding, destLevel, destNodeId):
    """
    Returns the shortest path. Format given in documentation
    """
    print 'do your stuff here'

