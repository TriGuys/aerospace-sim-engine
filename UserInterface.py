import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class UserInterface():
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HeMoSys - Aircraft Health Monitoring System")
        self.root.state('zoomed')
        self.root.configure(bg="white")

        # Configures the grid layout of two columns for button sidebar and main content
        self.root.grid_columnconfigure(0, weight=1, minsize=180)
        self.root.grid_columnconfigure(1, weight=4)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=3)
        self.root.grid_rowconfigure(1, weight=1)

    # Creates the left sidebar with alert filter buttons
    def CreateSidebar(self, parent):
        sidebar = tk.Frame(parent, bg="#e0f0ff", bd=1, relief="solid")
        sidebar.grid(row=0, column=0, sticky="nswe")

        # Loads the logo image
        logo_path = os.path.join(os.path.dirname(__file__), "Images", "logo.png")

        img = Image.open(logo_path)
        img = img.resize((160, 120), Image.Resampling.LANCZOS)
        logo_img = ImageTk.PhotoImage(img)
        logo_label = tk.Label(sidebar, image=logo_img, bg="#e0f0ff")
        logo_label.image = logo_img
        logo_label.pack(pady=(10, 5))

        tk.Label(
            sidebar, text="Alerts", 
            bg="#e0f0ff",
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
        style.theme_use("default")
        style.configure("Treeview", 
                    background="white",
                    fieldbackground="white",
                    rowheight=30,
                    font=("Arial", 10))
        style.map("Treeview", background=[("selected", "#cce5ff")])  # blue highlight on selection

        columns = ("Sensor ID", "Fault Code", "Severity", "Message", "Timestamp", "Status", "Actions")
        self.table = ttk.Treeview(frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=120, anchor=tk.CENTER)

        # Defines tag styles for severity levels
        self.table.tag_configure("critical", background="#ff9999")
        self.table.tag_configure("moderate", background="#ffd699")
        self.table.tag_configure("advisory", background="#ffff99")

        # Sample data for rows
        data = [
            ("01", "ENGTEMP", "Critical", "Engine temp exceeded", "13:48:01", "Active", "ℹ️  ❌"),
            ("02", "ENGPRESS", "Moderate", "Engine pressure too low", "13:52:04", "Active", "ℹ️  ❌"),
            ("03", "CABIN_PRESS", "Advisory", "Cabin pressure lost", "14:01:01", "Active", "ℹ️  ❌")
        ]

        # Inserts rows with appropriate tags based on severity
        for row in data:
            severity = row[2].lower()
            self.table.insert("", tk.END, values=row, tags=(severity,))

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