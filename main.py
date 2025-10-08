from AlertModule import AlertModule
from FaultDetection import FaultDetection
from FaultDetection import Fault
from SensorIntegration import SensorIntegration

class Main():

    def __init__(self):
        self.alertModule = AlertModule()
        self.faultDetection = FaultDetection()
        self.sensorIntegration = SensorIntegration()
        self.fault = Fault()

    def alert(self, message: str):
        self.alertModule.alert(message)