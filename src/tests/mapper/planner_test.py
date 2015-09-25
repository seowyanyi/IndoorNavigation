import unittest
import networkx as nx

import src.mapper.planner as planner


class DownloadMap(unittest.TestCase):
    def test_download_map_positive(self):
        mapObj = planner.download_map("COM1", 2)
        # Ensure we have direction of north
        northAt = abs(int(mapObj.initialBearing))
        self.assertTrue(0 <= northAt <= 360)
        # Ensure we have nodes
        nodes = mapObj.mapJsonData["map"]
        self.assertTrue(len(nodes) > 0)
        for node in nodes:
            nodeId = int(node["nodeId"])
            x = int(node["x"])
            y = int(node["y"])
            nodeName = node["nodeName"].strip()
            linkTo = node["linkTo"].split(', ')
            self.assertTrue(nodeId >= 1)
            self.assertTrue(x >= 0 and y >= 0)
            self.assertTrue(nodeName)
            self.assertTrue(len(linkTo) >= 1) # every node must have at least one link
            for item in linkTo:
                link = int(item.strip())
                self.assertTrue(link >= 1)

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

class PathPlanning(unittest.TestCase):
    def test_update_graph(self):
        sourceMap =  planner.download_map('COM2', 3)
        checkpoints = planner.get_checkpoints(sourceMap)
        graph = nx.Graph()
        planner.update_graph(checkpoints, graph)
        self.assertEquals(graph.number_of_nodes(), 16)
        self.assertEquals(graph.number_of_edges(), 15)

    def test_find_next_stage(self):
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

        com2Level2Map =  planner.download_map('COM2', 2)
        com2Level2chkpts = planner.get_checkpoints(com2Level2Map)

        nextStage = planner.find_next_stage(com2Level2chkpts, 'COM1', 2, [])
        self.assertEquals(nextStage['rank'], 1)
        self.assertEquals(nextStage['node'].localNodeId, '1')

        nextStage = planner.find_next_stage(com2Level2chkpts, 'COM2', 3, [])
        self.assertEquals(nextStage['rank'], 1)
        self.assertEquals(nextStage['node'].localNodeId, '16')

        # next stage not found yet
        nextStage = planner.find_next_stage(com2Level2chkpts, 'COM2', 2, [])
        otherNodes = nextStage['others']
        self.assertEquals(len(otherNodes), 1)

    def test_explore_and_build(self):
        pass