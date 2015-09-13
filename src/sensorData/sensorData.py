class Sonar:
    Left, Right, Front, UpperShin, LowerShin = range(5)

class IMUData:
    def __init__(self, xAxis, yAxis, zAxis):
        self.xAxis = xAxis
        self.yAxis = yAxis
        self.zAxis = zAxis

def add_to_imu_queue(imuData):
    return "added " + str(imuData.xAxis) + " " + str(imuData.yAxis) + " " + str(imuData.zAxis)

def add_to_sonar_queue(sonarData, sonarType):
    if sonarType == Sonar.Left:
        return "added to left sonar queue"
    elif sonarType == Sonar.Right:
        return "added to right sonar queue"
    elif sonarType == Sonar.Front:
        return "added to front sonar queue"
    elif sonarType == Sonar.UpperShin:
        return "added to upper shin sonar queue"
    elif sonarType == Sonar.LowerShin:
        return "added to lower shin sonar queue"
    else:
        return "error"