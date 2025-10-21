import tkinter as tk

from AlertModule import AlertModule
from FaultDetection import FaultDetection
from SensorIntegration import SensorIntegration
from UserInterface import UserInterface
from Database import AlertDatabase

def main():
    root = tk.Tk()

    UI = UserInterface(root)  

    database = AlertDatabase()
    alert_module = AlertModule(database)
    fault_detection = FaultDetection()
    sensor_integration = SensorIntegration()

    UI.draw_window()
    root.mainloop()

if __name__ == "__main__":
    main()