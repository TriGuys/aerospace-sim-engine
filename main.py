import tkinter as tk
from AlertModule import AlertModule
from FaultDetection import FaultDetection
from FaultDetection import Fault
from SensorIntegration import SensorIntegration

class Main:
    def __init__(self):
        self.alertModule = AlertModule()
        self.faultDetection = FaultDetection()
        self.sensorIntegration = SensorIntegration()

def main():
    root = tk.Tk()

    UI = Main()
    UI.alertModule 

    root.mainloop()


if __name__ == "__main__":
    main()