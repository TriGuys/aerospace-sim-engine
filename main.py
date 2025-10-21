import tkinter as tk
from AlertModule import AlertModule
from FaultDetection import FaultDetection
from FaultDetection import Fault
from SensorIntegration import SensorIntegration

def main():
    alert_module = AlertModule()
    fault_detection = FaultDetection()
    sensor_integration = SensorIntegration()

    UI.draw_window()
    root.mainloop()

if __name__ == "__main__":
    main()