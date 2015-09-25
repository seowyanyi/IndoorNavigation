import json
import urllib2
import networkx as nx
import math

# -------------------------------------------------------------------------------------------------------------------
MapError = 'NO_MAP_FOUND_ERROR'
StartNodeError = 'NO_START_NODE_FOUND_ERROR'
EndNodeError = 'NO_END_NODE_FOUND_ERROR'
PathError = 'NO_VALID_PATH_ERROR'
InvalidReqError = 'INVALID_REQUEST_ERROR'
# -------------------------------------------------------------------------------------------------------------------

class MapInfoObj:
    def __init__(self, buildingName, levelNum, mapJsonData, initialBearing):
        self.buildingName = buildingName
        self.levelNum = levelNum
        self.mapJsonData = mapJsonData
        self.initialBearing = initialBearing

class Checkpoint:    
    def __init__(self, buildingName, levelNum, nodeId, xCoord, yCoord, nodeName, linkTo):
        self.buildingName = buildingName
        self.levelNum = levelNum
        if type(nodeId) is int:
            self.localNodeId = str(nodeId)
        else:
            self.localNodeId = nodeId # this must be string
        self.xCoord = int(xCoord)
        self.yCoord = int(yCoord)
        self.nodeName = nodeName
        self.linkTo = linkTo.replace(' ', '').split(',')

    def get_global_id(self):
        return "{}-{}-{}".format(self.buildingName, self.levelNum, self.localNodeId)


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
    return math.sqrt(math.pow((coordDestX - coordSrcX), 2)+math.pow((coordDestY - coordSrcY),2))

def calculate_bearing(coordSrcX, coordSrcY, coordDestX, coordDestY):
    bearing = math.atan2(coordDestY-coordSrcY, coordDestX-coordSrcX)
    bearing = math.degrees(bearing) + 90
    if bearing > 180:
        bearing = 180 - bearing
    
    return bearing

# -------------------------------------------------------------------------------------------------------------------

def download_map(buildingName, levelNum):
    mapJsonData = json.load(urllib2.urlopen('http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building={}&Level={}'.format(buildingName,levelNum)))
    initialBearing = mapJsonData["info"]["northAt"]
    
    if mapJsonData["info"] is None:
        raise ValueError(MapError)
    
    return MapInfoObj(buildingName, levelNum, mapJsonData, initialBearing)

def is_link_to_other_maps(nodeName):
    """
    returns true if follows the below format:
    TO COM2-2-1 
    """
    nodeNameLowerCase = nodeName.lower()
    return nodeNameLowerCase.count('-') == 2 and "to" in nodeNameLowerCase

def get_linkage_building(nodeName):
    """
    Given TO COM2-3-1, returns COM2
    """
    removedTheWord_TO = nodeName[3:]
    noWhiteSpace = removedTheWord_TO.replace(' ', '')
    return noWhiteSpace.split('-')[0]


def get_linkage_level(nodeName):
    """
    Given TO COM2-3-1, returns 3 (int)
    """
    removedTheWord_TO = nodeName[3:]
    noWhiteSpace = removedTheWord_TO.replace(' ', '')
    return int(noWhiteSpace.split('-')[1])

def get_linkage_node(nodeName):
    """
    Given TO COM2-3-1, returns 1 (int)
    """      
    removedTheWord_TO = nodeName[3:]
    noWhiteSpace = removedTheWord_TO.replace(' ', '')
    return int(noWhiteSpace.split('-')[2])

def get_linkage_global_id(nodeName):
    """
    Given TO COM2-3-1, returns COM2-3-1 (int)
    """
    removedTheWord_TO = nodeName[3:]
    noWhiteSpace = removedTheWord_TO.replace(' ', '')
    return noWhiteSpace

def get_checkpoints(mapInfo):
    checkpoints_array = []
    mapJsonData = mapInfo.mapJsonData
    num_nodes = len(mapJsonData["map"])

    for i in range(0, num_nodes):
        currNode = mapJsonData["map"][i]
        checkpoint = Checkpoint(
            mapInfo.buildingName,
            mapInfo.levelNum,
            currNode["nodeId"],
            currNode["x"],
            currNode["y"],
            currNode["nodeName"],
            currNode["linkTo"])

        checkpoints_array.append(checkpoint)
    return checkpoints_array


def build_graph(sourceBuilding, sourceLevel, destBuilding, destLevel):
    sourceMap =  download_map(sourceBuilding, sourceLevel)
    sourceMapCheckpoints = get_checkpoints(sourceMap)
    graph = nx.Graph()
    update_graph(sourceMapCheckpoints, graph)

    if sourceBuilding == destBuilding and sourceLevel == destLevel:
        return graph
    else:
        explored = [sourceMap]
        explore_and_build(sourceMapCheckpoints, destBuilding, destLevel, graph, [], explored)

def explore_and_build(currLevelCheckpoints, destBuilding, destLevel, graph, unexplored, explored):
    """
    Recursively explores maps to find destination map

    :param currLevelCheckpoints: array of Checkpoints of the current map
    :param graph: network x graph
    :param unexplored: array of checkpoints linking to unexplored maps
    :param explored: array of MapInfoObj of explored maps
    :return:
    """
    # find next stage and augment graph with new nodes and edges
    nextStage = find_next_stage(currLevelCheckpoints, destBuilding, destLevel, explored)
    nextBuilding = get_linkage_building(nextStage['node'].nodeName)
    nextLevel = get_linkage_level(nextStage['node'].nodeName)
    nextMap = download_map(nextBuilding, nextLevel)
    nextCheckpoints = get_checkpoints(nextMap)
    update_graph(nextCheckpoints, graph)

    # add edge linking this stage to next stage
    graph.add_edge(nextStage['node'].get_global_id(),
                   get_linkage_global_id(nextStage['node'].nodeName)
                   , weight=1)

    explored.append(nextMap)
    unexplored = nextStage['others'] + unexplored

    if nextStage['rank'] == 1:
        # we have found our destination map
        return
    elif nextStage['rank'] == 2 or nextStage['rank'] == 3:
        # we haven't found our destination map, but there are some nodes left to explore
        explore_and_build(nextCheckpoints, destBuilding, destLevel, graph, unexplored, explored)
    elif len(nextStage['others']) == 0 and len(unexplored) > 0:
        # dead end!
        # try unexplored maps
        unexploredNode = unexplored.pop()
        unexploredMap =  download_map(unexploredNode.buildingName, unexploredNode.levelNum)
        unexploredMapCheckpoints = get_checkpoints(unexploredMap)
        explored.append(unexploredMap)
        explore_and_build(unexploredMapCheckpoints, destBuilding, destLevel, graph, unexplored, explored)
    else:
        # dead end and we have no unexplored maps
        print 'UNABLE TO FIND PATH'
        return

def is_explored(node, explored):
    toBuilding = get_linkage_building(node.nodeName)
    toLevel = get_linkage_level(node.nodeName)
    for exploredMap in explored:
        if exploredMap.buildingName == toBuilding and exploredMap.levelNum == toLevel:
            return True
    return False

def find_next_stage(checkpointArr, destBuilding, destLevel, explored):
    """
    Finds the linkage to the next stage. If not found, returns the most plausible link
    To be used if the destination checkpoint is not at the current level
    Heuristic used:
        Rank 1. Link matches destination building and level
        Rank 2. Link matches destination building
        Rank 3. Any other links
    Returns {rank: x, node: the_node_which_links_to_next_stage, others: other_linkages}
    """
    currentBestNode = None
    currentBestRank = None
    allNodes = []
    for node in checkpointArr:
        if not is_link_to_other_maps(node.nodeName):
            continue
        if is_explored(node, explored):
            continue
        allNodes.append(node)
        toBuilding = get_linkage_building(node.nodeName)
        toLevel = get_linkage_level(node.nodeName)
        if toBuilding == destBuilding and toLevel == destLevel:
            return {'rank': 1, 'node': node, 'others': []}
        if toBuilding == destBuilding:
            currentBestNode = node
            currentBestRank = 2
        elif currentBestRank == None:
            currentBestNode = node
            currentBestRank = 3

    allNodes.remove(currentBestNode)
    return {'rank': currentBestRank, 'node': currentBestNode, 'others': allNodes}


def get_link_node(localNodeId, checkpointsArr):
    """
    given a list of checkpoints in a single level and a node id,
    returns the checkpoint corresponding to the node id
    returns None if not found
    """
    for checkpoint in checkpointsArr:
        if localNodeId == checkpoint.localNodeId:
            return checkpoint
    return None

def update_graph(checkpointsArr, graph):
    """
    Adds nodes and weighted edges into the networkx graph.
    """
    for checkpoint in checkpointsArr:
        graph.add_node(checkpoint.get_global_id(), checkpoint=checkpoint)
        # links here are definitely on the same level
        for nodeId in checkpoint.linkTo:
            linkNode = get_link_node(nodeId, checkpointsArr)
            edgeWeight = calculate_distance(checkpoint.xCoord, checkpoint.yCoord, linkNode.xCoord, linkNode.yCoord)
            graph.add_edge(checkpoint.get_global_id(), linkNode.get_global_id(), weight=edgeWeight)

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
    
    nodeIdSrc = '{}-{}-{}'.format(sourceBuilding, sourceLevel, sourceNodeId)
    nodeIdDest = '{}-{}-{}'.format(destBuilding, destLevel, destNodeId)
    
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

def find_nearest_node(array, coord_X, coord_Y):
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
    
    return {'nearest_node': array[point], 'distance_to_node': distance_smallest}

def orientate_user(graph, array, coord_X, coord_Y, bearing):
    nearestNode = find_nearest_node(array, coord_X, coord_Y)['nearest_node']
    nodeCoordX = int(nearestNode.xCoord)
    nodecoordY = int(nearestNode.yCoord)
    distanceToNode = find_nearest_node(array, coord_X, coord_Y)['distance_to_node']
    intialBearing = bearing
    bearingToNode = calculate_bearing(coord_X, coord_Y, nodeCoordX, nodecoordY)
    
    turningAngle = bearingToNode - intialBearing
    direction = getDirection(distanceToNode,turningAngle)
    
    print nearestNode.nodeId
    return direction

# -------------------------------------------------------------------------------------------------------------------

def get_shortest_path(sourceBuilding, sourceLevel, sourceNodeId, destBuilding, destLevel, destNodeId):
    graph = nx.Graph()
    checkpointList = []

    startingMapInfo =  download_map(sourceBuilding, sourceLevel)
    graph = nx.Graph()
    update_graph(startingMapInfo, graph, checkpointList, graph)

    if sourceBuilding == destBuilding and sourceLevel == destLevel:
        destMapInfo = startingMapInfo
    else:
        destMapInfo = download_map(destBuilding, destLevel)

    destAndWeightedStartingGraph = update_graph(destMapInfo, weightedStartingGraph, checkpointList)
    weightedOverallGraph = update_edges_with_weight(checkpointList, destAndWeightedStartingGraph)
    finalGraph = combine_graph(weightedOverallGraph, checkpointList)

    path = find_shortest_path(finalGraph, sourceBuilding, sourceLevel, sourceNodeId, destBuilding, destLevel, destNodeId)
    return convert_to_API(path)


def begin_test():
    testType = int(raw_input('Enter test type. 1 for path finding. 2 for giving directions: '))
    while testType != 1 and testType != 2:
        testType = int(raw_input('Enter test type. 1 for path finding. 2 for giving directions: '))

    if testType == 1:
        test_path_finding()
    else:
        test_giving_directions()    


def test_path_finding():
    buildingName = raw_input('building name: ')
    levelNum = raw_input('level num: ')
    while True:
        startNode = raw_input('start node id: ')
        endNode  = raw_input('end node id: ')
        pathStr = get_shortest_path(buildingName, int(levelNum), int(startNode), 
            buildingName, int(levelNum), int(endNode))
        pathObj = json.loads(pathStr)
        print 'path: {}'.format(pathObj[0]['path'])
        response = json.load(urllib2.urlopen('http://localhost:3000/draw_path?path={}'.format(pathStr)))
        print 'visualize: {}'.format(response['transaction_id'])



def test_giving_directions():
    buildingName = raw_input('building name: ')
    levelNum = raw_input('level num: ')
    startNode = raw_input('start node id: ')
    endNode  = raw_input('end node id: ')
    pathStr = get_shortest_path(buildingName, int(levelNum), int(startNode), 
        buildingName, int(levelNum), int(endNode))
    pathObj = json.loads(pathStr)
    print 'path: {}'.format(pathObj[0]['path'])
    response = json.load(urllib2.urlopen('http://localhost:3000/draw_path?path={}'.format(pathStr)))
    print 'visualize: {}'.format(response['transaction_id'])

    while True:
        initial_x = int(raw_input('initial x: '))
        initial_y = int(raw_input('initial y: '))
        heading = int(raw_input('heading: '))
        if heading < 0:
            heading = 360 + heading
            # nearestNode = get_nearest_node(graph, initial_x, initial_y)
            # turningAngle = get_turning_angle(graph, nearestNode, initial_x, initial_y)
            # distance = get_distance_to_next(graph, nextNode, initial_x, initial_y)

            # print 'turn {} degrees'.format(turningAngle)
            # print 'walk {} cm'.format(distance)

            #get_turning_angle(graph, initial_x, initial_y, heading)



if __name__ == "__main__":
    begin_test()

# G = nx.Graph()
# checkpointList = []

# map = download_map("COM1", 2)
# G = update_graph(map, G, checkpointList)
# G = update_edges_with_weight(checkpointList, G)

# map = download_map("COM2", 2)
# G = update_graph(map, G, checkpointList)
# G = update_edges_with_weight(checkpointList, G)
# G = combine_graph(G, checkpointList)

# map = download_map("COM2", 3)
# G = update_graph(map, G, checkpointList)
# G = update_edges_with_weight(checkpointList, G)
# G = combine_graph(G, checkpointList)

# API = path_to_follow(G, "COM1", 2, 3, "COM2", 3, 12, 0)
# print API
# userMovement = orientate_user(G, checkpointList, 50, 100, 120)
# print 'Turn %f degrees and walk straight for %f cm' %(userMovement.turningAngle, userMovement.distance)