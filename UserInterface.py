import tkinter as tk
from tkinter import ttk

class UserInterface():
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HeMoSys - Aircraft Health Monitoring System")
        self.root.geometry("1000x600")
        self.root.configure(bg="white")

    def CreateAlert(self):
        pass

    # Creates the main alert table
    def CreateAlertTable(self):
        columns = ("ID", "Sensor", "Severity", "Time", "Status", "Actions")
        table = ttk.Treeview(self.root, columns=columns, show="headings")

        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=120, anchor=tk.CENTER)

        data = [
            ("01", "001", "Severe", "01:00", "Active", "i  X"),
            ("02", "003", "Moderate", "10:00", "Active", "i  X"),
            ("03", "004", "Advisory", "16:00", "Active", "i  X")
        ]

        for row in data:
            table.insert("", tk.END, values=row)

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=table.yview)
        table.configure(yscroll=scrollbar.set)

        table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def DrawWindow(self):
        self.CreateAlertTable()