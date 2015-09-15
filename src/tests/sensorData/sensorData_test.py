import unittest
import src.sensorData.sensorData as sensorData


class QueueAPI(unittest.TestCase):
    def test_add_imu_queue_positive(self):
        imuData = sensorData.IMUData(xAxis=123, yAxis=456, zAxis=789)
        dataAdded = sensorData.add_to_imu_queue(imuData)
        self.assertEquals('added 123 456 789', dataAdded)

    def test_add_sonar_queue_positive(self):
        negativeDataAdded = sensorData.add_to_sonar_queue(-9938, sensorData.Sonar.Left)
        self.assertEquals('added to left sonar queue', negativeDataAdded)
        positiveDataAdded = sensorData.add_to_sonar_queue(9938, sensorData.Sonar.Left)
        self.assertEquals('added to left sonar queue', positiveDataAdded)