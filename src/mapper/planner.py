import json
import urllib2
import networkx as nx
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

<<<<<<< HEAD:src/mapper/planner.py



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
# Draws out the graph using the MatPlotLib
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
# pos = nx.spring_layout(G)
# nx.draw_networkx(G, pos, node_color='y')
# path_edges = zip(path,path[1:])
# nx.draw_networkx_nodes(G,pos,nodelist=path,node_color='r')
# nx.draw_networkx_edges(G,pos,edgelist=path_edges,edge_color='r',width=5)
# plt.show()
#--------------------------------------------------------------------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
# Public APIs
#--------------------------------------------------------------------------------------------------------------------------------------------------------------

def download_map(buildingName, levelNum):
    """
    Returns a python dictionary of the downloaded map
    :param buildingName: string
    :param levelNum: integer
    >> what's the behaviour of this function when map is not found?
    """
    if type(levelNum) is int:
        levelNum = str(levelNum)

    url = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building={}&Level={}'.format(buildingName, levelNum)
    return json.load(urllib2.urlopen(url))




def find_shortest_path(sourceBuilding, sourceLevel, sourceNodeId,
                       destBuilding, destLevel, destNodeId):
    """
    Returns the shortest path. Format given in documentation
    >> what's the behaviour when no path is found / no relevant map found?
    """

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Iterates through the JSON files, creates the 'checkpoint' object and adds them to an array.
    # This also adds the nodeID of the node into a Graph
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------

    mapObj = download_map(sourceBuilding, sourceLevel)
    checkpointPrefix = sourceBuilding + '-' + sourceLevel + '-'
    i=0
    while True:
        if i == length_map_COM2_3:
            break
        checkpoint = make_checkpoint(mapObj["map"][i]["nodeId"], mapObj["map"][i]["x"], mapObj["map"][i]["y"], mapObj["map"][i]["nodeName"], mapObj["map"][i]["linkTo"])
        checkpoint.nodeId = checkpointPrefix + checkpoint.nodeId
        arrayObj.append(checkpoint)
        G.add_node(checkpoint.nodeId)

=======
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
>>>>>>> mapping-mala:src/mapper/planner/RoutePlanning.py
        length_linkTo = len(checkpoint.linkTo)
        j=0
        while True:
            if j == length_linkTo:
                break
<<<<<<< HEAD:src/mapper/planner.py
            checkpoint.linkTo[j] = "COM2-3-%s" %checkpoint.linkTo[j]
            G.add_edge(checkpoint.nodeId, checkpoint.linkTo[j])
            j = j+1

        i = i+1

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
=======
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
>>>>>>> mapping-mala:src/mapper/planner/RoutePlanning.py
        if n == length-1:
            m=m+1
            n=0
        n=n+1

<<<<<<< HEAD:src/mapper/planner.py
    path = nx.dijkstra_path(G, arrayObj[src-1].nodeId, arrayObj[dest-1].nodeId, 'weight')
    print path
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Given the source and destination NodeId, the shortest route and the shortest route is calculated
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------

    print nx.dijkstra_path_length(G, arrayObj[src-1].nodeId, arrayObj[dest-1].nodeId, 'weight')
=======
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
>>>>>>> mapping-mala:src/mapper/planner/RoutePlanning.py
