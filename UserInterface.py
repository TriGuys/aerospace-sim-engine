import tkinter as tk
from tkinter import ttk

class UserInterface():
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Aircraft Health Monitoring")
        self.root.geometry("800x400")

    def CreateAlert(self):
        pass

    def CreateTable(self):
        columns = ("Name", "Age", "Country")
        table = ttk.Treeview(self.root, columns=columns, show="headings")

        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=120, anchor=tk.CENTER)

        data = [
            ("Alice", 25, "UK"),
            ("Bob", 30, "USA"),
            ("Charlie", 22, "Canada"),
        ]

        for row in data:
            table.insert("", tk.END, values=row)

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=table.yview)
        table.configure(yscroll=scrollbar.set)

        table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def DrawWindow(self):
        self.CreateTable()