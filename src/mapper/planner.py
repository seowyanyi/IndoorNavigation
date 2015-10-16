import json
import urllib2
import requests
import networkx as nx
import math

# -------------------------------------------------------------------------------------------------------------------
MapError = 'NO_MAP_FOUND_ERROR'
StartNodeError = 'NO_START_NODE_FOUND_ERROR'
EndNodeError = 'NO_END_NODE_FOUND_ERROR'
PathError = 'NO_VALID_PATH_ERROR'
InvalidReqError = 'INVALID_REQUEST_ERROR'
DESTINATION_MAP_MISSING = 'Link to destination found, but the map is missing'
DESTINATION_NOT_FOUND = 'No links lead to destination'

# -------------------------------------------------------------------------------------------------------------------

class DestinationNotFound(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class MapInfoObj:
    def __init__(self, buildingName, levelNum, mapJsonData, initialBearing):
        self.buildingName = buildingName
        if type(levelNum) is str:
            self.levelNum = int(levelNum)
        else:
            self.levelNum = levelNum
        self.mapJsonData = mapJsonData
        self.initialBearing = initialBearing

class Checkpoint:    
    def __init__(self, buildingName, levelNum, nodeId, xCoord, yCoord, nodeName, linkTo, northAt):
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
        self.northAt = northAt

    def get_global_id(self):
        return "{}-{}-{}".format(self.buildingName, self.levelNum, self.localNodeId)


class Direction:
    def __init__(self, distance, turningAngle):
        self.distance = distance
        self.turningAngle = turningAngle

# -------------------------------------------------------------------------------------------------------------------
def calculate_distance(coordSrcX, coordSrcY, coordDestX, coordDestY):
    return math.sqrt(math.pow((coordDestX - coordSrcX), 2)+math.pow((coordDestY - coordSrcY),2))

def calculate_bearing_from_vertical(coordSrcX, coordSrcY, coordDestX, coordDestY):
    """
    Clockwise from vertical of source
    """
    bearing = -math.atan2(coordDestY-coordSrcY, coordDestX-coordSrcX)
    if abs(coordDestY-coordSrcY) == 0 and abs(coordDestX-coordSrcX) == 0:
        bearingDeg = abs(bearing)
        return bearingDeg
    bearingDeg = math.degrees(bearing) + 90
    if bearingDeg < 0:
        return 360 + bearingDeg

    return  bearingDeg

# -------------------------------------------------------------------------------------------------------------------

def download_map(buildingName, levelNum):
    url = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building={}&Level={}'.format(buildingName,levelNum)
    mapJsonData = json.load(urllib2.urlopen(url))
    if mapJsonData["info"] is None:
        raise ValueError(MapError)
    initialBearing = mapJsonData["info"]["northAt"]
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
    Given TO COM2-3-1, returns COM2-3-1
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
            currNode["linkTo"],
            mapInfo.initialBearing)

        checkpoints_array.append(checkpoint)
    return checkpoints_array


def build_graph(sourceBuilding, sourceLevel, destBuilding, destLevel):
    graph = nx.Graph()
    explore_and_build(sourceBuilding, sourceLevel, destBuilding, destLevel, graph, [], [])
    return graph

def explore_unexplored_maps(destBuilding, destLevel, graph, unexplored, explored):
    if len(unexplored) == 0:
        raise DestinationNotFound(DESTINATION_NOT_FOUND)

    unexploredNode = unexplored.pop()
    unexploredBuilding = get_linkage_building(unexploredNode.nodeName)
    unexploredLevel = get_linkage_level(unexploredNode.nodeName)
    graph.add_edge(unexploredNode.get_global_id(),
                   get_linkage_global_id(unexploredNode.nodeName),
                   weight=1)

    # print 'going to explore {}-{} next'.format(unexploredBuilding, unexploredLevel)
    explore_and_build(unexploredBuilding, unexploredLevel,
                      destBuilding, destLevel, graph, unexplored, explored)


def explore_and_build(nextBuilding, nextLevel, destBuilding, destLevel, graph, unexplored, explored):
    """
    Recursively explores maps to find destination map.
    Given next building and next level to search, this function first downloads the corresponding map
    and builds the graph

    :param graph: network x graph
    :param unexplored: array of checkpoints linking to unexplored maps
    :param explored: array of MapInfoObj of explored maps
    :return:
    """
    try:
        # Download map, update graph, mark as explored
        currMap =  download_map(nextBuilding, nextLevel)
        currMapCheckpoints = get_checkpoints(currMap)
        update_graph(currMapCheckpoints, graph)
        explored.append(currMap)
        print '------------------downloaded and updated: {}-{}'.format(currMap.buildingName,
                                                    currMap.levelNum)
    except ValueError:
        if nextBuilding == destBuilding and nextLevel == destLevel:
            raise DestinationNotFound(DESTINATION_MAP_MISSING)
        else:
            #try other unexplored maps
            explore_unexplored_maps(destBuilding, destLevel, graph, unexplored, explored)

    if nextBuilding == destBuilding and nextLevel == destLevel:
        # we have found our destination map
        # print 'destination map found. returning...'
        return

    # continue searching and augment graph with new nodes and edges
    nextStage = find_next_stage(currMapCheckpoints, destBuilding, destLevel, explored)
    if nextStage['node'] is not None:
        # add edge linking current stage to next stage
        graph.add_edge(nextStage['node'].get_global_id(),
                       get_linkage_global_id(nextStage['node'].nodeName),
                       weight=1)

        subsequentBuilding = get_linkage_building(nextStage['node'].nodeName)
        subsequentLevel = get_linkage_level(nextStage['node'].nodeName)
        # print 'going to explore {}-{} next'.format(subsequentBuilding, subsequentLevel)
        unexplored = nextStage['others'] + unexplored
        explore_and_build(subsequentBuilding, subsequentLevel,
                          destBuilding, destLevel, graph, unexplored, explored)
    elif len(unexplored) > 0:
        # print 'dead end !!'
        # dead end because no links exists from current map to other unexplored maps
        # try unexplored maps marked earlier
        explore_unexplored_maps(destBuilding, destLevel, graph, unexplored, explored)
    else:
        raise DestinationNotFound('No links lead to destination')


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

        toBuilding = get_linkage_building(node.nodeName)
        toLevel = get_linkage_level(node.nodeName)
        if toBuilding == destBuilding and toLevel == destLevel:
            return {'rank': 1, 'node': node, 'others': []}
        else:
            allNodes.append(node)

        if toBuilding == destBuilding:
            currentBestNode = node
            currentBestRank = 2
        elif currentBestRank == None:
            currentBestNode = node
            currentBestRank = 3

    if currentBestNode is not None:
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

def find_shortest_path_given_graph(graph, sourceBuilding, sourceLevel, sourceNodeId, destBuilding, destLevel, destNodeId):
    nodeIdSrc = '{}-{}-{}'.format(sourceBuilding, sourceLevel, sourceNodeId)
    nodeIdDest = '{}-{}-{}'.format(destBuilding, destLevel, destNodeId)
    return nx.dijkstra_path(graph, nodeIdSrc, nodeIdDest, 'weight')

# -------------------------------------------------------------------------------------------------------------------
def convert_to_API(path):
    p=0
    r=0
    stage=1
    path_nodes = len(path)
    arrayNodes = []
    arrayStages = []
    startingBuild = path[p].split('-')[0]
    startingLevel = path[p].split('-')[1]
    p += 1
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
                    stage += 1
                    startingBuild = path[r].split('-')[0]
                    startingLevel = path[r].split('-')[1]

        p += 1

    stringNodes = ("[{0}]".format(", ".join(str(i) for i in arrayNodes))).replace(" ", "")
    building = startingBuild
    level = startingLevel
    apiNode = '{"stage":%d,"building":"%s","level":%s,"path":%s}' %(stage, building, level, stringNodes)
    arrayStages.append(apiNode)
    
    return "[{0}]".format(", ".join(str(i) for i in arrayStages))


def convert_global_path_to_checkpoints(global_path, graph):
    listOfCheckpoints = []
    checkpoints = nx.get_node_attributes(graph, 'checkpoint')
    for point in global_path:
        listOfCheckpoints.append(checkpoints[point])
    return listOfCheckpoints


def bearing_to_node(srcX, srcY, destX, destY, northAt, nextNode):
    """
    :return: {'bearing_to_next': a, 'distance_to_next': b}
    """
    # make sure bearing is positive to simplify calculations:
    distance = calculate_distance(srcX, srcY, destX, destY)
    bearing = calculate_bearing_from_vertical(srcX, srcY, destX, destY)
    bearingToNode = (360 - int(northAt)) + int(bearing)
    
    return {'bearing_to_next': bearingToNode, 'distance_to_next': distance, 'next_checkpoint': nextNode}

def is_link_change(curr, nextNode):
    currBuilding = curr.split('-')[0]
    currLevel = int(curr.split('-')[1])
    nextBuilding = nextNode.split('-')[0]
    nextLevel = int(nextNode.split('-')[1])
    return currBuilding != nextBuilding or currLevel != nextLevel


def find_linkages(global_path): # todo: not tested
    """
    Given global path like [COM2-1-19, COM2-1-22, COM2-2-1],
    find the linkages to the next map, if any
    Linkages are detected when the building or level changes.

    Returns the index of the linkage start: COM2-1-22 in the above example.
    COM2-1-22 --- COM2-2-1 is a linkage
    """
    linkages = []
    for i in range(0, len(global_path)-1):
        if is_link_change(global_path[i], global_path[i+1]):
            linkages.append(i)
    return linkages

def is_link_change(curr, nextNode):
    currBuilding = curr.split('-')[0]
    currLevel = int(curr.split('-')[1])
    nextBuilding = nextNode.split('-')[0]
    nextLevel = int(nextNode.split('-')[1])
    return currBuilding != nextBuilding or currLevel != nextLevel


def find_linkages(global_path): # todo: not tested
    """
    Given global path like [COM2-1-19, COM2-1-22, COM2-2-1],
    find the linkages to the next map, if any
    Linkages are detected when the building or level changes.

    Returns the index of the linkage start: COM2-1-22 in the above example.
    COM2-1-22 --- COM2-2-1 is a linkage
    """
    linkages = []
    for i in range(0, len(global_path)-1):
        if is_link_change(global_path[i], global_path[i+1]):
            linkages.append(i)
    return linkages


def find_dist_bearing_to_next_node(global_path, graph): # todo: test across different maps
    array=[]
    currentNodeIndex=0
    linkages = find_linkages(global_path)
    checkpointList = convert_global_path_to_checkpoints(global_path, graph)

    while True:
        if currentNodeIndex == len(checkpointList)-1:
            break
        currentNode = checkpointList[currentNodeIndex]
        nextNode = checkpointList[currentNodeIndex+1]
        coord_X = currentNode.xCoord
        coord_Y = currentNode.yCoord

        nextNode = checkpointList[currentNodeIndex+1]
        dist_and_bearing = bearing_to_node(coord_X, coord_Y, nextNode.xCoord, nextNode.yCoord, northAt, nextNode)
        array.append(dist_and_bearing)
        currentNodeIndex += 1
    return array

# -------------------------------------------------------------------------------------------------------------------

def get_shortest_path(sourceBuilding, sourceLevel, sourceNodeId, destBuilding, destLevel, destNodeId):
    graph = build_graph(sourceBuilding, sourceLevel, destBuilding, destLevel)
    path = find_shortest_path_given_graph(graph, sourceBuilding, sourceLevel, sourceNodeId,
                                          destBuilding, destLevel, destNodeId)
    return find_dist_bearing_to_next_node(path, graph)

def begin_test():
    test_path_finding()

def test_path_finding():
    buildingName = 'COM1'
    levelNum = '2'
    while True:
        startNode = raw_input('start node id: ')
        endNode  = raw_input('end node id: ')

        graph = build_graph(buildingName, int(levelNum), buildingName, int(levelNum))
        path = find_shortest_path_given_graph(graph, buildingName, int(levelNum), int(startNode),
                                          buildingName, int(levelNum), int(endNode))

        pathStr = convert_to_API(path)
        print 'path str: {}'.format(pathStr)
        pathObj = json.loads(pathStr)
        final_path = 'path: {}'.format(pathObj[0]['path'])
        print final_path
        url = 'http://localhost:3000/draw_path?path={}'.format(pathStr)
        try:
            res = requests.get(url)
            print 'visualize: {}'.format(res.json()["transaction_id"])
        except requests.exceptions.RequestException as e:
            pass


# def orientate_user(srcX, srcY, destX, destY, currBearing):
#     """
#     :param currBearing: user's compass heading w.r.t north of map.
#     :return: {'turning_angle': a, 'distance_to_node': b}
#     if a < 0, turn CCW. If a > 0, turn CW
#
#     the NorthAt of the map should be taken into consideration given that the
#     current bearing is based on the north of the map and not the true north
#     """
#     # make sure bearing is positive to simplify calculations:
#     if currBearing < 0:
#         currBearing += 360
#     distance = calculate_distance(srcX, srcY, destX, destY)
#     bearingToNode = calculate_bearing_from_vertical(srcX, srcY, destX, destY)
#     if bearingToNode == 0:
#         turningAngle = 0
#     else:
#         turningAngle = bearingToNode - currBearing
#
#     if abs(turningAngle) < 180:
#         return {'turning_angle': turningAngle, 'distance_to_node': distance}
#     if turningAngle < 0:
#         return {'turning_angle': turningAngle+360, 'distance_to_node': distance}
#     # Turning angle > 0, and abs(angle) > 180
#     return {'turning_angle': - (360 - turningAngle), 'distance_to_node': distance}

# def convert_path_to_checkpoints(local_path, graph, buildingName, levelNum):
#     """
#     :param path: list of local node ids along the path (int)
#     :param graph: the networkx graph
#     :param buildingName: building the path belongs to
#     :param levelName: level the path belongs to
#     :return: list of Checkpoint objects
#     """
#     listOfCheckpoints = []
#     for point in local_path:
#         for nxNode,data in graph.nodes_iter(data=True):
#             node = data['checkpoint']
#             if node.buildingName != buildingName or node.levelNum != levelNum:
#                 continue
#             if int(node.localNodeId) == int(point):
#                 listOfCheckpoints.append(node)
#                 break
#
#     return listOfCheckpoints

# def find_nearest_node_in_graph(graph, coord_X, coord_Y):
#     """
#     Finds nearest node in the graph from the current location
#     This only works for a single map
#     :param graph: the network x graph
#     """
#     currShortestDist = None
#     currNearestNode = None
#     for nxNode,data in graph.nodes_iter(data=True):
#         node = data['checkpoint']
#         x = node.xCoord
#         y = node.yCoord
#         if x == coord_X and y == coord_Y:
#             # same node
#             return {'nearest_node_on_path': node, 'distance_to_node': 0}
#         distance = calculate_distance(coord_X, coord_Y, x, y)
#         if currShortestDist is None or distance < currShortestDist:
#             currShortestDist = distance
#             currNearestNode = node
#     return {'nearest_node_on_path': currNearestNode, 'distance_to_node': currShortestDist}

# def find_nearest_next_node(checkpointList, coord_X, coord_Y):
#     """
#     Finds nearest next node in the path from the current location
#     This only works for a single map
#     e.g. A -> B -> C
#     If user not on the path but nearest to B, nearest next node is B
#     If user is on B, the nearest next node is C
#     If user is on C (destination), return None
#     :param checkpointList: list of checkpoints along the path
#     """
#     currShortestDist = None
#     currNearestNode = None
#     length = len(checkpointList)
#     counter = 0
#     go_next = False
#
#     for node in checkpointList:
#         counter += 1
#         x = node.xCoord
#         y = node.yCoord
#         if x == coord_X and y == coord_Y:
#             if counter == length:
#                 # already at destination
#                 return None
#             else:
#                 go_next = True
#                 continue
#
#         distance = calculate_distance(coord_X, coord_Y, x, y)
#         if go_next:
#             return node
#         if currShortestDist is None or distance < currShortestDist:
#             currShortestDist = distance
#             currNearestNode = node
#     return currNearestNode

if __name__ == "__main__":
    begin_test()
