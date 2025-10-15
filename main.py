from AlertModule import AlertModule
from FaultDetection import FaultDetection
from FaultDetection import Fault
from SensorIntegration import SensorIntegration
from UserInterface import UserInterface

def main():
    root = tk.Tk()

    UI = UserInterface(root)  

    alert_module = AlertModule()
    fault_detection = FaultDetection()
    sensor_integration = SensorIntegration()
    fault = Fault()
    UI.DrawWindow()
    root.mainloop()

if __name__ == "__main__":
    main()

class Main():

    def __init__(self):
        self.alertModule = AlertModule()
        self.faultDetection = FaultDetection()
        self.sensorIntegration = SensorIntegration()

    def alert(self, message: str):
        self.alertModule.alert(message)