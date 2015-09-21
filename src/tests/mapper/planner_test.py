import unittest

import src.mapper.planner as planner


class DownloadMap(unittest.TestCase):
    def test_download_map_positive(self):
        mapObj = planner.download_map("COM1", 2)
        # Ensure we have direction of north
        northAt = abs(int(mapObj["info"]["northAt"]))
        self.assertTrue(0 <= northAt <= 360)

        # Ensure we have nodes
        nodes = mapObj["map"]
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

class PathPlanning(unittest.TestCase):
    def test_path_planning_positive(self):
        path = planner.find_shortest_path("COM1", 2, 1, "COM1", 2, 33)
        # Can't really check whether the path is shortest.
        # So just check that the planned path is valid
        # get the map, ensure each node indeed has a link to the next node.

        # Check that there is only one stage if same building, same level

    def test_path_planning_near(self):
        # Test two nodes which are very near
        pass

    def test_path_planning_far(self):
        # Test two nodes which are very far e.g. across buildings
        pass

    def test_path_planning_go_up(self):
        # Test a path which requires us to go up the stairs
        pass

    def test_path_planning_go_down(self):
        # Test a path which requires us to go down the stairs
        pass