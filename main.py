from AlertModule import AlertModule
from FaultDetection import FaultDetection
from SensorIntegration import SensorIntegration

class Main():

    def __init__(self):
        self.alertModule = AlertModule()
        self.faultDetection = FaultDetection()
        self.sensorIntegration = SensorIntegration()

    def alert(self, message: str):
        self.alertModule.alert(message)