import unittest
import networkx as nx

import src.mapper.planner as planner

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

        bearing = planner.calculate_bearing_from_vertical(3475,1646,2988,1098) # glass door to P6
        self.assertEquals(round(bearing,2), 221.63)
        bearing = planner.calculate_bearing_from_vertical(2988,1098,3475,1646) # P6 to glass door
        self.assertEquals(round(bearing,2), 41.63)


class PathPlanning(unittest.TestCase):
    NUM_EDGES_COM1_2 = 41
    NUM_NODES_COM1_2 = 40

    NUM_EDGES_COM2_2 = 19
    NUM_NODES_COM2_2 = 20

    NUM_EDGES_COM2_3 = 15
    NUM_NODES_COM2_3 = 16

    def test_find_linkages(self):
        global_path = ['1-2-19', '1-2-22', '2-2-1', '2-2-15', '2-3-15', '6-7-15']
        expected_linkage_start = [1,3,4]
        self.assertEquals(planner.find_linkages(global_path), expected_linkage_start)
        no_linkages = ['1-2-19', '1-2-16', '1-2-22', '1-2-23']
        self.assertTrue(len(planner.find_linkages(no_linkages)) == 0)

    def test_update_graph(self):
        sourceMap =  planner.download_map('2', 3)
        checkpoints = planner.get_checkpoints(sourceMap)
        graph = nx.Graph()
        planner.update_graph(checkpoints, graph)
        self.assertEquals(graph.number_of_nodes(), self.NUM_NODES_COM2_3)
        self.assertEquals(graph.number_of_edges(), self.NUM_EDGES_COM2_3)


    def test_get_shortest_path(self):
        path = planner.get_shortest_path('2', 2, 6, '2', 2, 19)
        print path

    def test_add_additional_information(self):
        # no staircases here
        distBearingList = [{'curr_node_name': 'Another Door'}, {'curr_node_name': 'Stairwell'},
                           {'curr_node_name': 'Wooden Door'}, {'curr_node_name': 'Glass Door'}]
        planner.add_additional_information(distBearingList)
        expected = [{'curr_node_name': 'Another Door', 'type': 'supershort'}, {'curr_node_name': 'Stairwell', 'type': 'default'},
                    {'curr_node_name': 'Wooden Door', 'type': 'doorway'},{'curr_node_name': 'Glass Door', 'type': 'default'}]
        self.assertEquals(distBearingList, expected)

        # one flight of stairs
        distBearingList = [{'curr_node_name': 'Another Door'}, {'curr_node_name': 'Stairwell'},
                           {'curr_node_name': 'Halfway'}, {'curr_node_name': 'TO 2-3-11'}]
        planner.add_additional_information(distBearingList)
        expected = [{'curr_node_name': 'Another Door', 'type': 'supershort'}, {'curr_node_name': 'Stairwell', 'type': 'staircase'},
                    {'curr_node_name': 'Halfway', 'type': 'supershort'}, {'curr_node_name': 'TO 2-3-11', 'type': 'default'}]
        self.assertEquals(distBearingList, expected)


