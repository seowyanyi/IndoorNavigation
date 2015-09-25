import json
import urllib2
import networkx as nx
import matplotlib.pyplot as plt
import math

# -------------------------------------------------------------------------------------------------------------------
MapError = 'NO_MAP_FOUND_ERROR'
StartNodeError = 'NO_START_NODE_FOUND_ERROR'
EndNodeError = 'NO_END_NODE_FOUND_ERROR'
PathError = 'NO_VALID_PATH_ERROR'
InvalidReqError = 'INVALID_REQUEST_ERROR'
# -------------------------------------------------------------------------------------------------------------------
class MapInfoObj(object):
    buildingName = ""
    levelNum = 0
    mapJsonData = ""
    initialBearing = 0
    
    # The class "constructor" - It's actually an initializer
    def __init__(self, buildingName, levelNum, mapJsonData, initialBearing):
        self.buildingName = buildingName
        self.levelNum = levelNum
        self.mapJsonData = mapJsonData
        self.initialBearing = initialBearing

def getMapInfo(buildingName, levelNum, mapJsonData, initialBearing):
    mapDetails = MapInfoObj(buildingName, levelNum, mapJsonData, initialBearing)
    
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

class DirectionObj(object):
    distance = ""
    turningAngle = 0
    
    # The class "constructor" - It's actually an initializer
    def __init__(self, distance, turningAngle):
        self.distance = distance
        self.turningAngle = turningAngle

def getDirection(distance, turningAngle):
    direction = DirectionObj(distance, turningAngle)
    
    return direction
# -------------------------------------------------------------------------------------------------------------------
def calculate_distance(coordSrcX, coordSrcY, coordDestX, coordDestY):
    edge_weight = math.sqrt(math.pow((coordDestX - coordSrcX), 2)+math.pow((coordDestY - coordSrcY),2))
    
    return edge_weight

def calculate_bearing(coordSrcX, coordSrcY, coordDestX, coordDestY):
    bearing = math.atan2(coordDestY-coordSrcY, coordDestX-coordSrcX)
    bearing = math.degrees(bearing) + 90
    if bearing > 180:
        bearing = 180 - bearing
    
    return bearing

# -------------------------------------------------------------------------------------------------------------------

def download_map(buildingName, levelNum):
    mapJsonData = json.load(urllib2.urlopen('http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building=%s&Level=%d'%(buildingName,levelNum)))
    initialBearing = mapJsonData["info"]["northAt"]
    
    if (mapJsonData["info"] == None):
        raise ValueError(MapError)
    
    mapDetails = getMapInfo(buildingName, levelNum, mapJsonData, initialBearing)
    
    return mapDetails


def update_graph(mapDetails, graph, array):
    i = 0
    mapJsonData = mapDetails.mapJsonData
    length_map = len(mapJsonData["map"])
    
    while True:
        if i == length_map:
            break
        checkpoint = create_checkpoint(mapJsonData["map"][i]["nodeId"], mapJsonData["map"][i]["x"], mapJsonData["map"][i]["y"], mapJsonData["map"][i]["nodeName"], mapJsonData["map"][i]["linkTo"])
        checkpoint.nodeId = "%s-%d-%s" %(mapDetails.buildingName, mapDetails.levelNum, checkpoint.nodeId)
        array.append(checkpoint)
        graph.add_node(checkpoint.nodeId)
        # Create edges between the nodes using nodeId and LinkTo values
        length_linkTo = len(checkpoint.linkTo)
        j=0
        while True:
            if j == length_linkTo:
                break
            checkpoint.linkTo[j] = '%s-%d-%s' %(mapDetails.buildingName, mapDetails.levelNum, checkpoint.linkTo[j])
            graph.add_edge(checkpoint.nodeId, checkpoint.linkTo[j])
            j = j+1
        
        i = i+1
    
    return graph

def combine_graph(graph, array):
    p = 0
    length_array = len(array)
    while True:
        if p == length_array:
            break
        if "TO" in array[p].nodeName:
            nextLevelNode = (array[p].nodeName).split(' ')
            nextLevelNode = str(nextLevelNode[1])
            graph.add_edge(array[p].nodeId, nextLevelNode, weight=1)
        p = p+1
    
    return graph

def update_edges_with_weight(array, graph):
    m=0
    n=0
    length_array = len(array)
    while True:
        if m == length_array:
            break
        nodeEdgeSrc = array[m].nodeId
        nodeEdgeDest = array[n].nodeId
        if graph.has_edge(nodeEdgeSrc, nodeEdgeDest):
            coordSrcX = int(array[m].xCoord)
            coordSrcY = int(array[m].yCoord)
            coordDestX = int(array[n].xCoord)
            coordDestY = int(array[n].yCoord)
            edge_weight = calculate_distance(coordSrcX, coordSrcY, coordDestX, coordDestY)
            graph[nodeEdgeSrc][nodeEdgeDest]['weight'] = edge_weight
        if n == length_array-1:
            m=m+1
            n=0
        n=n+1
    
    return graph

def find_shortest_path(graph, sourceBuilding, sourceLevel, sourceNodeId, destBuilding, destLevel, destNodeId):
    
    nodeIdSrc = '%s-%d-%d' %(sourceBuilding, sourceLevel, sourceNodeId)
    nodeIdDest = '%s-%d-%d' %(destBuilding, destLevel, destNodeId)
    
    path = nx.dijkstra_path(graph, nodeIdSrc, nodeIdDest, 'weight')
    pathLength = nx.dijkstra_path_length(graph, nodeIdSrc, nodeIdDest, 'weight')
    
    if (pathLength == 0):
        raise IndexError(PathError)
    
    #    print pathLength
    return path

# -------------------------------------------------------------------------------------------------------------------
def convert_to_API(path):
    p=0
    r=0
    stage=1
    path_nodes = len(path)
    arrayNodes = []
    arrayStages = []
    level=0
    startingBuild = path[p].split('-')[0]
    startingLevel = path[p].split('-')[1]
    p=p+1
    while True:
        if p == path_nodes:
            break
        else:
            while True:
                if r == path_nodes:
                    break
                elif (path[r].split('-')[0] == startingBuild) and (path[r].split('-')[1] == startingLevel):
                    arrayNodes.append(path[r].split('-')[2])
                    r=r+1
                else:
                    stringNodes = ("[{0}]".format(", ".join(str(i) for i in arrayNodes))).replace(" ", "")
                    building = startingBuild
                    level = startingLevel
                    apiNode = '{"stage":%d,"building":"%s","level":%s,"path":%s}' %(stage, building, level, stringNodes)
                    arrayStages.append(apiNode)
                    arrayNodes = []
                    stage = stage+1
                    startingBuild = path[r].split('-')[0]
                    startingLevel = path[r].split('-')[1]

    p=p+1

stringNodes = ("[{0}]".format(", ".join(str(i) for i in arrayNodes))).replace(" ", "")
    building = startingBuild
    level = startingLevel
    apiNode = '{"stage":%d,"building":"%s","level":%s,"path":%s}' %(stage, building, level, stringNodes)
    arrayStages.append(apiNode)
    
    return "[{0}]".format(", ".join(str(i) for i in arrayStages))


def path_to_follow(graph, sourceBuilding, sourceLevel, sourceNodeId, destBuilding, destLevel, destNodeId, bearing):
    k=0
    path = find_shortest_path(graph, sourceBuilding, sourceLevel, sourceNodeId, destBuilding, destLevel, destNodeId)
    path_length = len(path)
    #    while True:
    #        if k == path_length:
    #            break
    #
    #        k=k+1
    
    API_MAP = convert_to_API(path)
    return API_MAP

def find_nearest_node(array, coord_X, coord_Y, dataReq):
    s=0
    array_length = len(array)
    pointX = int(array[s].xCoord)
    pointY = int(array[s].yCoord)
    distance_smallest = calculate_distance(coord_X, coord_Y, pointX, pointY)
    s=s+1
    while True:
        if s == array_length:
            break
        pointX = int(array[s].xCoord)
        pointY = int(array[s].yCoord)
        distance = calculate_distance(coord_X, coord_Y, pointX, pointY)
        if distance < distance_smallest:
            distance_smallest = distance
            point = s
        s=s+1
    
    if dataReq == 0:
        return array[point]
    elif dataReq == 1:
        return distance_smallest
    else:
        raise ValueError(InvalidReqError)

def orientate_user(graph, array, coord_X, coord_Y, bearing):
    nearestNode = find_nearest_node(array, coord_X, coord_Y, 0)
    nodeCoordX = int(nearestNode.xCoord)
    nodecoordY = int(nearestNode.yCoord)
    distanceToNode = find_nearest_node(array, coord_X, coord_Y, 1)
    intialBearing = bearing
    bearingToNode = calculate_bearing(coord_X, coord_Y, nodeCoordX, nodecoordY)
    
    turningAngle = bearingToNode - intialBearing
    direction = getDirection(distanceToNode,turningAngle)
    
    print nearestNode.nodeId
    return direction

# -------------------------------------------------------------------------------------------------------------------

G = nx.Graph()
checkpointList = []

map = download_map("COM1", 2)
G = update_graph(map, G, checkpointList)
G = update_edges_with_weight(checkpointList, G)

map = download_map("COM2", 2)
G = update_graph(map, G, checkpointList)
G = update_edges_with_weight(checkpointList, G)
G = combine_graph(G, checkpointList)

map = download_map("COM2", 3)
G = update_graph(map, G, checkpointList)
G = update_edges_with_weight(checkpointList, G)
G = combine_graph(G, checkpointList)

API = path_to_follow(G, "COM1", 2, 3, "COM2", 3, 12, 0)
print API
userMovement = orientate_user(G, checkpointList, 50, 100, 120)
print 'Turn %f degrees and walk straight for %f cm' %(userMovement.turningAngle, userMovement.distance)

