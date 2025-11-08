import tkinter as tk
from UserInterface import UserInterface
from AlertModule import AlertModule
from Database import AlertDatabase

def main():
    """Main orcherstrator method intialising database, alert module, UI and tkinter main loop."""
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