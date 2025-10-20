import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

class UserInterface():
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HeMoSys - Aircraft Health Monitoring System")
        self.root.state('zoomed')
        self.root.configure(bg="white")

        # Configures the grid layout of two columns for button sidebar and main content
        self.root.grid_columnconfigure(0, weight=1, minsize=200)
        self.root.grid_columnconfigure(1, weight=4)
        self.root.grid_rowconfigure(0, weight=3)
        self.root.grid_rowconfigure(1, weight=1)

    # Creates the left sidebar with alert filter buttons
    def CreateSidebar(self, parent):
        sidebar = tk.Frame(parent, bg="#e0f0ff", bd=1, relief="solid")
        sidebar.grid(row=0, column=0, sticky="nswe", padx=5, pady=(10, 0))

        # Loads the logo image
        logo_path = os.path.join(os.path.dirname(__file__), "Images", "logo.png")

        img = Image.open(logo_path)
        img = img.resize((160, 120), Image.Resampling.LANCZOS)
        logo_img = ImageTk.PhotoImage(img)
        logo_label = tk.Label(sidebar, image=logo_img, bg="#e0f0ff")
        logo_label.image = logo_img
        logo_label.pack(pady=(10, 5))

        # Alerts section label
        tk.Label(
            sidebar, text="Alerts", 
            bg="#e0f0ff",
            font=("Arial", 12, "bold")
        ).pack(pady=(15, 10))

        # Defines the buttons and their filter functions
        button_actions = {
            "All Alerts": self.ShowAllAlerts,
            "Critical Alerts": self.ShowCriticalAlerts,
            "Moderate Alerts": self.ShowModerateAlerts,
            "Advisory Alerts": self.ShowAdvisoryAlerts
        }

        for text, command in button_actions.items():
            b = tk.Button(
                sidebar,
                text=text,
                width=20,
                font=("Arial", 10),
                command=command
            )
            b.pack(pady=5)

        return sidebar
    
    # Creates box for uploading CSV files
    def CreateFileUploadBox(self, parent):
        upload_box = tk.Frame(parent, bg="#e0f0ff", bd=1, relief="solid")
        upload_box.grid(row=1, column=0, sticky="nsew", padx=5, pady=(10, 10))
        upload_box.grid_propagate(False)
        upload_box.grid_rowconfigure(0, weight=1)
        upload_box.grid_columnconfigure(0, weight=1)

        tk.Label(
            upload_box,
            text="Upload Sensor Data",
            bg="#e0f0ff",
            font=("Arial", 11, "bold")
        ).pack(pady=(15, 5))

        tk.Button(
            upload_box,
            text="Select CSV File",
            font=("Arial", 10),
            bg="#f7fbff",
            activebackground="#d0eaff",
            command=self.UploadCSV
        ).pack(pady=10)

    # File upload logic
    def UploadCSV(self):
        file_path = filedialog.askopenfilename(
            title="Select Sensor Data CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not file_path:
            return
        
        if not file_path.lower().endswith(".csv"):
            messagebox.showerror(
                "Invalid File",
                "Please select a valid CSV file (with .csv extension)."
            )
            return
    
        # Placeholder for when file_path will be sent to sensor integration module
        if file_path:
            messagebox.showinfo("File Uploaded", f"Loaded: {os.path.basename(file_path)}")

    def CreateAlert(self):
        pass

    # Creates the main alert table
    def CreateAlertTable(self, parent):
        frame = tk.Frame(parent, bg="white")
        frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                    background="white",
                    fieldbackground="white",
                    rowheight=30,
                    font=("Arial", 10))
        style.map("Treeview", background=[("selected", "#a7c7e7")])

        columns = ("Alert ID", "Sensor ID", "Fault Code", "Severity", "Message", "Timestamp", "Status", "Actions")
        self.table = ttk.Treeview(frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.table.heading(col, text=col)
            width = 80 if col in ("Alert ID", "Sensor ID", "Status") else 120
            self.table.column(col, width=width, anchor=tk.CENTER)

        # Defines tag styles for severity levels
        self.table.tag_configure("critical", background="#ff9999")
        self.table.tag_configure("moderate", background="#ffd699")
        self.table.tag_configure("advisory", background="#ffff99")
        self.table.tag_configure("resolved", background="#d4edda")

        # Sample data for rows
        self.all_alerts = [
            ("", "01", "ENGTEMP", "Critical", "Engine temp exceeded", "13:48:01", "Active", "✅    ❌"),
            ("", "02", "ENGPRESS", "Moderate", "Engine pressure low", "13:52:04", "Active", "✅    ❌"),
            ("", "03", "CABIN_PRESS", "Advisory", "Cabin pressure lost", "14:01:01", "Active", "✅    ❌")
        ]

        # Inserts rows with appropriate tags based on severity
        self.DisplayAlerts(self.all_alerts)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)

        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.table.bind("<Button-1>", self.OnTableClick)

    def DisplayAlerts(self, alerts):
        for item in self.table.get_children():
            self.table.delete(item)

        for row in alerts:
            severity = row[3].lower()
            self.table.insert("", tk.END, values=row, tags=(severity,))

    def ShowAllAlerts(self):
        self.DisplayAlerts(self.all_alerts)

    # Shows critical alerts when button is pressed
    def ShowCriticalAlerts(self):
        critical_alerts = [a for a in self.all_alerts if a[3].lower() == "critical"]
        self.DisplayAlerts(critical_alerts)

    # Shows moderate alerts when button is pressed
    def ShowModerateAlerts(self):
        moderate_alerts = [a for a in self.all_alerts if a[3].lower() == "moderate"]
        self.DisplayAlerts(moderate_alerts)

    # Shows advisory alerts when button is pressed
    def ShowAdvisoryAlerts(self):
        advisory_alerts = [a for a in self.all_alerts if a[3].lower() == "advisory"]
        self.DisplayAlerts(advisory_alerts)

    def OnTableClick(self, event):
        # Identifies which cell was clicked
        region = self.table.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.table.identify_row(event.y)
        column = self.table.identify_column(event.x)

        if column == "#8":
            values = list(self.table.item(row_id, "values"))
            if not values:
                return

            # Checks where in the Actions column user clicked (left for resolve and right for delete)
            bbox = self.table.bbox(row_id, column)
            if not bbox:
                return

            x_offset = event.x - bbox[0]
            if x_offset < bbox[2] / 2:
                self.ResolveAlert(row_id)
            else:
                self.DeleteAlert(row_id)

    # Marks alert as resolved
    def ResolveAlert(self, row_id):
        values = list(self.table.item(row_id, "values"))
        if not values:
            return

        values[6] = "Resolved"
        values[7] = "☑    ❌"
        self.table.item(row_id, values=values)
        self.table.item(row_id, tags=("resolved",))

        alert_id = values[0] if values[0] else "(No ID)"
        messagebox.showinfo("Alert Resolved", f"Alert {alert_id} marked as resolved.")

    # Deletes an alert
    def DeleteAlert(self, row_id):
        values = self.table.item(row_id, "values")
        if not values:
            return

        confirm = messagebox.askyesno("Delete Alert", f"Are you sure you want to delete alert {values[0] or '(No ID)'}?")
        if confirm:
            self.table.delete(row_id)
            self.all_alerts = [a for a in self.all_alerts if a[1] != values[1]]

    # Creates the alert graph window placeholder
    def CreateAlertGraph(self, parent):
        frame = tk.Frame(parent, bg="#e9e9e9", height=200, bd=1, relief="solid")
        frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=(0, 10))
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
        self.CreateFileUploadBox(self.root)
        self.CreateAlertGraph(self.root)