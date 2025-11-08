import os
import tkinter as tk
import logging
import re

from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from FaultDetection import FaultDetection
from SensorIntegration import SensorIntegration

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

hour_minute_second = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$")

class UserInterface():
    """Tkinter based user interface for the HeMoSys Aircraft Health Monitoring System."""

    def __init__(self, root: tk.Tk, alert_module = None) -> None:
        """Initialise the main application window and grid layout."""
        self.root = root
        self.alert_module = alert_module
        self.fault_detection = FaultDetection()
        self.sensor_integration = SensorIntegration()
        self.root.title("HeMoSys - Aircraft Health Monitoring System")
        self.root.state('zoomed')
        self.root.configure(bg="white")

        # Configure the grid layout of two columns for button sidebar and main content.
        self.root.grid_columnconfigure(0, weight=1, minsize=200)
        self.root.grid_columnconfigure(1, weight=4)
        self.root.grid_rowconfigure(0, weight=3)
        self.root.grid_rowconfigure(1, weight=1, minsize=260)

    def create_sidebar(self, parent: tk.Widget) -> tk.Frame:
        """Create the left sidebar with alert filter buttons."""
        sidebar = tk.Frame(parent, bg="#e0f0ff", bd=1, relief="solid")
        sidebar.grid(row=0, column=0, sticky="nswe", padx=5, pady=(10, 0))

        # Loads and resizes the logo image.
        logo_path = os.path.join(os.path.dirname(__file__), "Images", "logo.png")
        img = Image.open(logo_path).resize((160, 120), Image.Resampling.LANCZOS)
        logo_img = ImageTk.PhotoImage(img)

        logo_label = tk.Label(sidebar, image=logo_img, bg="#e0f0ff")
        logo_label.image = logo_img
        logo_label.pack(pady=(10, 5))

        # Alerts section label.
        tk.Label(
            sidebar, text="Alerts", 
            bg="#e0f0ff",
            font=("Arial", 12, "bold")
        ).pack(pady=(15, 10))

        # Defines the buttons and their filter functions.
        button_actions = {
            "All Alerts": self.show_all_alerts,
            "Critical Alerts": self.show_critical_alerts,
            "Moderate Alerts": self.show_moderate_alerts,
            "Advisory Alerts": self.show_advisory_alerts,
            "Resolved Alerts": self.show_resolved_alerts
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
    
    def create_file_upload_box(self, parent: tk.Widget) -> None:
        """Create a box for uploading sensor data CSV files."""
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
            command=self.upload_csv
        ).pack(pady=10)

    def upload_csv(self) -> None:
        """Handle CSV file selection and basic validation for file type."""
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
    
        try:
            # Load CSV into a pandas DataFrame.
            df = self.sensor_integration.read_csv(file_path)

            # Detect faults in the DataFrame.
            rules_path = os.path.join(os.path.dirname(__file__), "fault_rules.json")
            self.fault_detection.loadRules(rules_path)

            faults = self.fault_detection.detectFromBatch(df)

            # Create alerts from each fault.
            for fault in faults:
                self.alert_module.create_alert (
                    sensor_id=fault.sensor_id,
                    fault_code=fault.fault_id,
                    severity=fault.severity.name,
                    message=fault.description,
                    timestamp=fault.timestamp
                )
                
            # Reload the table with the latest alerts.
            self.all_alerts = [
                (
                    alert.alert_id,
                    alert.sensor_id,
                    alert.fault_code,
                    alert.severity,
                    alert.message,
                    alert.timestamp,
                    "Active",
                    "✅    ❌"
                )
                for alert in self.alert_module.get_all_alerts()
            ]

            self.display_alerts(self.all_alerts)
            logging.info(f"Raised {len(faults)} alert(s) from {file_path}")
            messagebox.showinfo("Success", f"Processed and raised {len(faults)} alert(s) from {file_path}")

        except Exception as e:
            messagebox.showerror("Processing Error", f"An error occurred while processing the file:\n{e}")

    def create_alert_table(self, parent: tk.Widget) -> None:
        """Create the main table showing active alerts."""
        frame = tk.Frame(parent, bg="white")
        frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
                    "Treeview", 
                    background="white",
                    fieldbackground="white",
                    rowheight=30,
                    font=("Arial", 10),
                    bordercolor="#000000",
                    borderwidth=1,
                    relief="solid"
        )
        style.map("Treeview", background=[("selected", "#a7c7e7")])

        columns = ("Alert ID", "Sensor ID", "Fault Code", "Severity", "Message", "Timestamp", "Status", "Actions")
        self.table = ttk.Treeview(frame, columns=columns, show="headings", height=10)  

        for col in columns:
            self.table.heading(col, text=col)

            if col == "Alert ID":
                width = 60
            elif col  == "Status":
                width = 90
            elif col == "Fault Code":
                width = 180
            elif col in ("Severity", "Timestamp", "Actions"):
                width = 100
            elif col == "Message":
                width = 260
            else:
                width = 120

            self.table.column(col, width=width, anchor=tk.CENTER)

        # Define tag styles for severity levels.
        self.table.tag_configure("critical", background="#ff9999")
        self.table.tag_configure("moderate", background="#ffd699")
        self.table.tag_configure("advisory", background="#ffff99")
        self.table.tag_configure("resolved", background="#d4edda")

        # Load alerts dynamically from the backend.
        if self.alert_module:
            self.all_alerts = [
                (
                    alert.alert_id,
                    alert.sensor_id,
                    alert.fault_code,
                    alert.severity,
                    alert.message,
                    alert.timestamp,
                    "Active",
                    "✅    ❌"
                )
                for alert in self.alert_module.get_all_alerts()
            ]
        else:
        # Fallback to show placeholder demo data.
            self.all_alerts = [
                ("", "01", "ENGTEMP", "Critical", "Engine temp exceeded", "13:48:01", "Active", "✅    ❌"),
                ("", "02", "ENGPRESS", "Moderate", "Engine pressure low", "13:52:04", "Active", "✅    ❌"),
                ("", "03", "CABIN_PRESS", "Advisory", "Cabin pressure lost", "14:01:01", "Active", "✅    ❌")
            ]

        # Insert rows with appropriate tags based on severity.
        self.display_alerts(self.all_alerts)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)

        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.table.bind("<Button-1>", self.on_table_click)

    def display_alerts(self, alerts: list[tuple]) -> None:
        """Populate the alert table with data."""
        for item in self.table.get_children():
            self.table.delete(item)

        # Insert new rows with proper color tags
        for row in alerts:
            severity = row[3].lower() if len(row) > 3 else "advisory"
            status = row[6].lower() if len(row) > 6 else "active"

            # Use resolved colour if status is resolved
            tag = "resolved" if status == "resolved" else severity
            self.table.insert("", tk.END, values=row, tags=(tag,))

        if hasattr(self, "graph_ax"): # hasattr checks graph exists and avoids exception if it doesn't
            # Use the rows just displayed (not necessarily all_alerts if filtered)
            visible = [self.table.item(i, "values") for i in self.table.get_children("")]
            self.sort_and_display_alerts(visible)

    def show_all_alerts(self) -> None:
        """Display all alerts."""
        self.display_alerts(self.all_alerts)

    def show_critical_alerts(self) -> None:
        """Display only critical alerts."""
        critical_alerts = [a for a in self.all_alerts if a[3].lower() == "critical"]
        self.display_alerts(critical_alerts)

    def show_moderate_alerts(self) -> None:
        """Display only moderate alerts."""
        moderate_alerts = [a for a in self.all_alerts if a[3].lower() == "moderate"]
        self.display_alerts(moderate_alerts)

    def show_advisory_alerts(self) -> None:
        """Display only advisory alerts."""
        advisory_alerts = [a for a in self.all_alerts if a[3].lower() == "advisory"]
        self.display_alerts(advisory_alerts)

    def show_resolved_alerts(self) -> None:
        """Display only resolved alerts."""
        resolved_alerts = [a for a in self.all_alerts if a[6].lower() == "resolved"]
        self.display_alerts(resolved_alerts)

    def on_table_click(self, event: tk.Event) -> None:
        """Identify and handle user clicks in the alert table."""
        region = self.table.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.table.identify_row(event.y)
        column = self.table.identify_column(event.x)

        if column == "#8":
            values = list(self.table.item(row_id, "values"))
            if not values:
                return

            # Check where in the Actions column user clicked (left for resolve and right for delete).
            bbox = self.table.bbox(row_id, column)
            if not bbox:
                return

            x_offset = event.x - bbox[0]
            if x_offset < bbox[2] / 2:
                self.resolve_alert(row_id)
            else:
                self.delete_alert(row_id)

    def resolve_alert(self, row_id: str) -> None:
        """Toggle alert between active and resolved."""
        values = list(self.table.item(row_id, "values"))
        if not values:
            return
        
        alert_id = values[0]
        current_status = values[6]

        # Check that alert_id is not empty or invalid.
        if not alert_id or str(alert_id).strip() == "":
            messagebox.showwarning("Invalid Alert", "Cannot modify an alert without a valid ID.")
            return   

        try:
            # Toggle status in the database
            if current_status == "Active":
                self.alert_module.resolve_alert(int(alert_id))
                values[6] = "Resolved"
                values[7] = "☑    ❌"
                self.table.item(row_id, values=values, tags=("resolved",))
                messagebox.showinfo("Alert Resolved", f"Alert {alert_id} marked as resolved.")
            else:
            # Mark as active again
                self.alert_module.unresolve_alert(int(alert_id))
                values[6] = "Active"
                values[7] = "✅    ❌"
                severity_tag = values[3].lower() if len(values) > 3 else "active"
                self.table.item(row_id, values=values, tags=(severity_tag,))
                messagebox.showinfo("Alert Reactivated", f"Alert {alert_id} reactivated.")
        
        except ValueError:
            messagebox.showerror("Error", f"Invalid alert ID: {alert_id}")
            return
    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update alert: {e}")
            return
        
         # Update self.all_alerts so filters reflect the new alert status
        self.all_alerts = [
            tuple(values) if str(a[0]) == str(alert_id) else a
            for a in self.all_alerts
        ]

        if hasattr(self, "graph_ax"):
            visible = [self.table.item(i, "values") for i in self.table.get_children("")]
            self.sort_and_display_alerts(visible)

    def delete_alert(self, row_id: str) -> None:
        """Delete a selected alert after confirmation from the user."""
        values = self.table.item(row_id, "values")
        if not values:
            return
        
        alert_id = values[0]

        # Check that alert_id is not empty or invalid.
        if not alert_id or str(alert_id).strip() == "":
            messagebox.showwarning("Invalid Alert", "Cannot delete an alert without a valid ID.")
            return

        confirm = messagebox.askyesno("Delete Alert", f"Are you sure you want to delete alert {alert_id or '(No ID)'}?")
        if confirm:
            # Only delete from User Interface if backend deletion succeeds.
            try:
                deleted = self.alert_module.delete_alert(int(alert_id))
                if not deleted:
                    messagebox.showwarning("Delete Failed", f"Alert {alert_id} could not be deleted from the database.")
                    return
            except ValueError:
                messagebox.showerror("Error", f"Invalid alert ID: {alert_id}")
                return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete alert: {e}")
                return

            self.table.delete(row_id)
            self.all_alerts = [a for a in self.all_alerts if str(a[0]) != str(alert_id)]
            messagebox.showinfo("Alert Deleted", f"Alert {alert_id} deleted successfully.")

        if hasattr(self, "graph_ax"):
            visible = [self.table.item(i, "values") for i in self.table.get_children("")]
            self.sort_and_display_alerts(visible)

    def sort_and_display_alerts(self, alerts: list[tuple]) -> None:
        counts = [0] * 24 # Create bin for each hour of the day
        
        for row in alerts:
            timestamp = str(row[5])
            if hour_minute_second.match(timestamp): # verify timestamp is in HH:MM:SS format
                counts[int(timestamp[0:2])] += 1 # add it to the correct HH bin

        ax = self.graph_ax 
        ax.clear()
        ax.bar(range(24), counts) # establish 24 bars

        ax.set_xlim(-0.5, 23.5)           # 00–23 fixed
        ax.set_ylim(bottom=0)
        ax.set_title("Alerts per hour")
        ax.set_xlabel("Hour of day (24h)")
        ax.set_ylabel("Alert count")

        ticks = list(range(0, 24, 3)) # set labels/ticks for every 3 hours over 24 hour period
        ax.set_xticks(ticks, [f"{h:02d}:00" for h in ticks]) # sets tick position
        for label in ax.get_xticklabels():
            label.set_fontsize(8)

        ax.yaxis.get_major_locator().set_params(integer=True) # ensure its purely hour ticks no decimal
        self.graph_canvas.draw_idle()

    def create_alert_graph(self, parent: tk.Widget) -> None:
        """Create a placeholder frame for the alert graph window."""
        self.graph_frame = tk.Frame(parent, bg="#e9e9e9", height=240, bd=1, relief="solid")
        self.graph_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=(0, 10))
        self.graph_frame.grid_propagate(False)

        # Figure + canvas (reserve bottom margin for tick labels)
        self.graph_fig = Figure(figsize=(7.5, 2.4), dpi=100)
        self.graph_ax = self.graph_fig.add_subplot(111)
        self.graph_fig.subplots_adjust(bottom=0.28, left=0.08, right=0.98, top=0.88)

        self.graph_canvas = FigureCanvasTkAgg(self.graph_fig, master=self.graph_frame)
        self.graph_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Draw
        self.sort_and_display_alerts(getattr(self, "all_alerts", []))

    def draw_window(self) -> None:
        """Render all of the user interface components."""
        self.create_sidebar(self.root)
        self.create_alert_table(self.root)
        self.create_file_upload_box(self.root)
        self.create_alert_graph(self.root)