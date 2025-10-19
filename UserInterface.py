import tkinter as tk
from tkinter import ttk

class UserInterface():
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HeMoSys - Aircraft Health Monitoring System")
        self.root.geometry("1000x600")
        self.root.configure(bg="white")
        self.root.grid_rowconfigure(0, weight=3)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.state('zoomed')

        # Configures the grid layout of two columns for button sidebar and main content)
        self.root.grid_columnconfigure(0, weight=1, minsize=180)
        self.root.grid_columnconfigure(1, weight=4)
        self.root.grid_rowconfigure(0, weight=1)

    # Creates the left sidebar with alert filter buttons
    def CreateSidebar(self, parent):
        sidebar = tk.Frame(parent, bg="#f2f2f2", bd=1, relief="solid")
        sidebar.grid(row=0, column=0, sticky="nswe")

        tk.Label(
            sidebar, text="Alerts", bg="#f2f2f2",
            font=("Arial", 12, "bold")
        ).pack(pady=(15, 10))

        buttons = ["All Alerts", "Critical Alerts", "Moderate Alerts", "Advisory Alerts"]
        for text in buttons:
            b = tk.Button(sidebar, text=text, width=20, font=("Arial", 10))
            b.pack(pady=5)

        return sidebar

    def CreateAlert(self):
        pass

    # Creates the main alert table
    def CreateAlertTable(self, parent):
        frame = tk.Frame(parent, bg="white")
        frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Treeview", rowheight=30)

        columns = ("Sensor ID", "Fault Code", "Severity", "Message", "Timestamp", "Status", "Actions")
        self.table = ttk.Treeview(frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=120, anchor=tk.CENTER)

        data = [
            ("01", "ENGTEMP", "Critical", "Engine temperature exceeded", "13:48:01", "Active", "i  X"),
            ("02", "ENGPRESS", "Moderate", "Engine pressure too low", "13:52:04", "Active", "i  X"),
            ("03", "CABIN_PRESS", "Critical", "Cabin pressure lost", "14:01:01", "Active", "i  X")
        ]

        for row in data:
            self.table.insert("", tk.END, values=row)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)

        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    # Creates the alert graph window
    def CreateAlertGraph(self, parent):
        frame = tk.Frame(parent, bg="#e9e9e9", height=200, bd=1, relief="solid")
        frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=(0, 10))
        frame.grid_propagate(False)

        tk.Label(
            frame,
            text="(Graph placeholder for alerts over time)",
            bg="#e9e9e9",
            font=("Arial", 10, "italic")
        ).pack(pady=40)

    def DrawWindow(self):
        self.CreateSidebar(self.root)
        self.CreateAlertTable(self.root)
        self.CreateAlertGraph(self.root)