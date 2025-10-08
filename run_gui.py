import tkinter as tk
from UserInterface import UserInterface

if __name__ == "__main__":
    root = tk.Tk()
    ui = UserInterface(root)
    ui.draw_window()
    root.mainloop()