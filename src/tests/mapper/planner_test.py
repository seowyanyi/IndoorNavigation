import unittest
import networkx as nx

import src.mapper.planner as planner


# class DownloadMap(unittest.TestCase):
#     def test_download_map_positive(self):
#         mapObj = planner.download_map("COM1", 2)
#         # Ensure we have direction of north
#         northAt = abs(int(mapObj.initialBearing))
#         self.assertTrue(0 <= northAt <= 360)
#         # Ensure we have nodes
#         nodes = mapObj.mapJsonData["map"]
#         self.assertTrue(len(nodes) > 0)
#         for node in nodes:
#             nodeId = int(node["nodeId"])
#             x = int(node["x"])
#             y = int(node["y"])
#             nodeName = node["nodeName"].strip()
#             linkTo = node["linkTo"].split(', ')
#             self.assertTrue(nodeId >= 1)
#             self.assertTrue(x >= 0 and y >= 0)
#             self.assertTrue(nodeName)
#             self.assertTrue(len(linkTo) >= 1) # every node must have at least one link
#             for item in linkTo:
#                 link = int(item.strip())
#                 self.assertTrue(link >= 1)

class ParseNodeNames(unittest.TestCase):
    def test_is_link_to_other_maps(self):
        self.assertTrue(planner.is_link_to_other_maps('TO COM5-4-3'))
        self.assertFalse(planner.is_link_to_other_maps('Glass Door'))
        self.assertFalse(planner.is_link_to_other_maps('To Canteen'))

    def test_get_linkage(self):
        self.assertEquals(planner.get_linkage_building('TO COM5-4-3'), 'COM5')
        self.assertEquals(planner.get_linkage_level('TO COM5-4-3'), 4)
        self.assertEquals(planner.get_linkage_node('TO COM5-4-3'), 3)
        self.assertEquals(planner.get_linkage_building('TO     COM2 - 1 -   2  '), 'COM2')
        self.assertEquals(planner.get_linkage_global_id('TO COM5-4-3'), 'COM5-4-3')
        self.assertEquals(planner.get_linkage_global_id('TO   COM 5 -4 -3'), 'COM5-4-3')

class Direction(unittest.TestCase):
    def test_calculate_bearing(self):
        bearing = planner.calculate_bearing_from_vertical(0,0,5,7)
        self.assertEquals(round(bearing,2), 35.54)
        bearing = planner.calculate_bearing_from_vertical(5,7,0,0)
        self.assertEquals(round(bearing,2), 215.54)
        bearing = planner.calculate_bearing_from_vertical(15,15,10,20)
        self.assertEquals(round(bearing,2), 315)
        bearing = planner.calculate_bearing_from_vertical(2,10,10,2)
        self.assertEquals(round(bearing,2), 135)

class PathPlanning(unittest.TestCase):
    NUM_EDGES_COM1_2 = 41
    NUM_NODES_COM1_2 = 40

    NUM_EDGES_COM2_2 = 19
    NUM_NODES_COM2_2 = 20

    NUM_EDGES_COM2_3 = 15
    NUM_NODES_COM2_3 = 16

    def test_find_linkages(self):
        global_path = ['COM1-2-19', 'COM1-2-22', 'COM2-2-1', 'COM2-2-15', 'COM2-3-15', 'COM6-7-15']
        expected_linkage_start = [1,3,4]
        self.assertEquals(planner.find_linkages(global_path), expected_linkage_start)
        no_linkages = ['COM1-2-19', 'COM1-2-16', 'COM1-2-22', 'COM1-2-23']
        self.assertTrue(len(planner.find_linkages(no_linkages)) == 0)

    def test_update_graph(self):
        sourceMap =  planner.download_map('COM2', 3)
        checkpoints = planner.get_checkpoints(sourceMap)
        graph = nx.Graph()
        planner.update_graph(checkpoints, graph)
        self.assertEquals(graph.number_of_nodes(), self.NUM_NODES_COM2_3)
        self.assertEquals(graph.number_of_edges(), self.NUM_EDGES_COM2_3)

    def test_find_next_stage(self):
        """
        COM1-2 ---- COM2-2 ---- COM2-3 ---- COM1-3 (missing)
        """
        #----------------------  COM 1 LEVEL 2 ------------------------
        sourceMap =  planner.download_map('COM1', 2)
        checkpoints = planner.get_checkpoints(sourceMap)

        nextStage = planner.find_next_stage(checkpoints, 'COM2', 2, [])
        self.assertEquals(nextStage['rank'], 1)
        self.assertEquals(nextStage['node'].localNodeId, '31')

        nextStage = planner.find_next_stage(checkpoints, 'COM2', 3, [])
        self.assertEquals(nextStage['rank'], 2)
        self.assertEquals(nextStage['node'].localNodeId, '31')

        nextStage = planner.find_next_stage(checkpoints, 'COM1', 2, [])
        self.assertEquals(nextStage['rank'], 3)
        self.assertEquals(nextStage['node'].localNodeId, '31')

        #----------------------  COM 2 LEVEL 2 ------------------------
        com2Level2Map =  planner.download_map('COM2', 2)
        com2Level2chkpts = planner.get_checkpoints(com2Level2Map)

        nextStage = planner.find_next_stage(com2Level2chkpts, 'COM1', 2, [])
        self.assertEquals(nextStage['rank'], 1)
        self.assertEquals(nextStage['node'].localNodeId, '1')

        nextStage = planner.find_next_stage(com2Level2chkpts, 'COM2', 3, [])
        self.assertEquals(nextStage['rank'], 1)
        self.assertEquals(nextStage['node'].localNodeId, '16')

        # final destination at least two stages away
        nextStage = planner.find_next_stage(com2Level2chkpts, 'COM1', 3, [])
        otherNodes = nextStage['others']
        self.assertEquals(len(otherNodes), 1)
        self.assertEquals(nextStage['rank'], 2)
        self.assertEquals(nextStage['node'].localNodeId, '1')

        com1_level_2_map = planner.MapInfoObj('COM1', 2, None, None)
        nextStage = planner.find_next_stage(com2Level2chkpts, 'COM1', 3, [com1_level_2_map])
        otherNodes = nextStage['others']
        self.assertEquals(len(otherNodes), 0) # only have one choice since COM1-2 is explored
        self.assertEquals(nextStage['rank'], 3)
        self.assertEquals(nextStage['node'].localNodeId, '16')


    def test_build_graph_negative(self):
        """
        COM1-2 ---- COM2-2 ---- COM2-3 ---- COM1-3 (missing)
        """
        # There is a link to the destination map, but destination map cannot be downloaded
        self.assertRaises(planner.DestinationNotFound,
                          planner.build_graph,
                          'COM2', 2, 'COM1', 3)

        # Destination map not found
        self.assertRaises(planner.DestinationNotFound,
                          planner.build_graph,
                          'COM2', 2, 'ABC', 12)

    def test_build_graph_positive(self):
        # source == destination
        graph = planner.build_graph('COM1', 2, 'COM1', 2)
        self.assertEquals(graph.number_of_edges(), self.NUM_EDGES_COM1_2)
        self.assertEquals(graph.number_of_nodes(), self.NUM_NODES_COM1_2)

        # source and destination maps are adjacent
        graph = planner.build_graph('COM1', 2, 'COM2', 2)
        self.assertEquals(graph.number_of_edges(),
                          self.NUM_EDGES_COM1_2 + self.NUM_EDGES_COM2_2 +1)
        self.assertEquals(graph.number_of_nodes(),
                          self.NUM_NODES_COM1_2 + self.NUM_NODES_COM2_2)

        # source and destination maps are at least two stages away
        graph = planner.build_graph('COM1', 2, 'COM2', 3)
        self.assertEquals(graph.number_of_edges(),
                          self.NUM_EDGES_COM1_2 + self.NUM_EDGES_COM2_2 + self.NUM_EDGES_COM2_3 + 2)
        self.assertEquals(graph.number_of_nodes(),
                          self.NUM_NODES_COM1_2 + self.NUM_NODES_COM2_2 + self.NUM_NODES_COM2_3)

    def test_get_shortest_path(self):
        path = planner.get_shortest_path('COM1', 2, 29, 'COM2', 2, 17)
        print path
