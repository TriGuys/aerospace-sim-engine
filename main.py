import tkinter as tk
from UserInterface import UserInterface
from AlertModule import AlertModule
from Database import AlertDatabase
from FaultDetection import FaultDetection
from FaultDetection import Fault
from SensorIntegration import SensorIntegration

def main():
    root = tk.Tk()

    # Initialise the backend.
    database = AlertDatabase()
    alert_module = AlertModule(database)

    # Pass backend to the User Interface.
    ui = UserInterface(root, alert_module)

    # Draw the interface.
    ui.draw_window()

    # Start the main Tkinter loop.
    root.mainloop()

if __name__ == "__main__":
    main()