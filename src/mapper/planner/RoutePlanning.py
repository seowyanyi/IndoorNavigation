import json
import urllib2
import networkx as nx
import matplotlib.pyplot as plt
import math
# ----------------------------------------------------------------------
G = nx.Graph()
checkpointList = []

MapError = 'NO_MAP_FOUND_ERROR'
StartNodeError = 'NO_START_NODE_FOUND_ERROR'
EndNodeError = 'NO_END_NODE_FOUND_ERROR'
PathError = 'NO_VALID_PATH_ERROR'
# -----------------------------------------------------------------------
class MapInfoObj(object):
    buildingName = ""
    levelNum = 0
    mapJsonData = ""
    
    # The class "constructor" - It's actually an initializer
    def __init__(self, buildingName, levelNum, mapJsonData):
        self.buildingName = buildingName
        self.levelNum = levelNum
        self.mapJsonData = mapJsonData

def getMapInfo(buildingName, levelNum, mapJsonData):
    mapDetails = MapInfoObj(buildingName, levelNum, mapJsonData)
    
    return mapDetails


class Checkpoint(object):
    nodeId = 0
    xCoord = 0
    yCoord = 0
    nodeName = ""
    linkTo = [10]
    
    # The class "constructor" - It's actually an initializer
    def __init__(self, nodeId, xCoord, yCoord, nodeName, linkTo):
        self.nodeId = nodeId
        self.xCoord = xCoord
        self.yCoord = yCoord
        self.nodeName = nodeName
        self.linkTo = linkTo.split(', ')

def create_checkpoint(nodeId, xCoord, yCoord, nodeName, linkTo):
    checkpoint = Checkpoint(nodeId, xCoord, yCoord, nodeName, linkTo)
    
    return checkpoint

# -----------------------------------------------------------------------
def calculate_edge_weight(coordSrcX, coordSrcY, coordDestX, coordDestY):
    edge_weight = math.sqrt(math.pow((coordDestX - coordSrcX), 2)+math.pow((coordDestY - coordSrcY),2))
        
    return edge_weight
# -----------------------------------------------------------------------

def download_map(buildingName, levelNum):
    mapJsonData = json.load(urllib2.urlopen('http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building=%s&Level=%d'%(buildingName,levelNum)))
        
    if (mapJsonData["info"] == None):
        raise ValueError(MapError)

    mapDetails = getMapInfo(buildingName, levelNum, mapJsonData)
    
    return mapDetails


def update_graph(mapDetails, G, checkpointList):
    i = 0
    mapJsonData = mapDetails.mapJsonData
    length_map = len(mapJsonData["map"])

    while True:
        if i == length:
            break
        checkpoint = create_checkpoint(mapJsonData["map"][i]["nodeId"], mapJsonData["map"][i]["x"], mapJsonData["map"][i]["y"], mapJsonData["map"][i]["nodeName"], mapJsonData["map"][i]["linkTo"])
        checkpoint.nodeId = "%s-%d-%s" %(mapDetails.buildingName, mapDetails.levelNum, checkpoint.nodeId)
        checkpointList.append(checkpoint)
        G.add_node(checkpoint.nodeId)
    
    # Create edges between the nodes using nodeId and LinkTo values
        length_linkTo = len(checkpoint.linkTo)
        j=0
        while True:
            if j == length_linkTo:
                break
            checkpoint.linkTo[j] = '%s-%d-%s' %(mapDetails.buildingName, mapDetails.levelNum, checkpoint.linkTo[j])
            G.add_edge(checkpoint.nodeId, checkpoint.linkTo[j])
            j = j+1
        
        i = i+1

def combine_graph(G, checkpointList):
    length_array = len(checkpointList)
    while True:
        if p == length_array:
            break
        if "TO" in checkpointList[p].nodeName:
            nextLevelNode = (checkpointList[p].nodeName).split(' ')
            nextLevelNode = str(nextLevelNode[1])
            G.add_edge(checkpointList[p].nodeId, nextLevelNode, weight=1)
        p = p+1

def update_edges_with_weight(checkpointList, G):
    length_array = len(checkpointList)
    while True:
        if m == length_array:
            break
        nodeEdgeSrc = checkpointList[m].nodeId
        nodeEdgeDest = checkpointList[n].nodeId
        if G.has_edge(nodeEdgeSrc, nodeEdgeDest):
            coordSrcX = int(checkpointList[m].xCoord)
            coordSrcY = int(checkpointList[m].yCoord)
            coordDestX = int(checkpointList[n].xCoord)
            coordDestY = int(checkpointList[n].yCoord)
            edge_weight = calculate_edge_weight(coordSrcX, coordSrcY, coordDestX, coordDestY)
            G[nodeEdgeSrc][nodeEdgeDest]['weight'] = edge_weight
        if n == length-1:
            m=m+1
            n=0
        n=n+1

def find_shortest_path(G, sourceBuilding, sourceLevel, sourceNodeId, destBuilding, destLevel, destNodeId):
    
    nodeIdSrc = '%s-%d-%d' %(sourceBuilding, sourceLevel, sourceNodeId)
    nodeIdDest = '%s-%d-%d' %(destBuilding, destLevel, destNodeId)
        
    path = nx.dijkstra_path(G, nodeIdSrc, nodeIdDest, 'weight')
    pathLength = nx.dijkstra_path_length(G, nodeIdSrc, nodeIdDest, 'weight')
    
    if (pathLength == 0):
        raise IndexError(PathError)
    
    print pathLength
    return path

def draw_graph(G):
    pos = nx.spring_layout(G)
    nx.draw_networkx(G, pos, node_color='y')
    path_edges = zip(path,path[1:])
    nx.draw_networkx_nodes(G,pos,nodelist=path,node_color='r')
    nx.draw_networkx_edges(G,pos,edgelist=path_edges,edge_color='r',width=5)
    plt.show()
