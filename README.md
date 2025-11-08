# HeMoSys - Health Monitoring System

## Overview

**HeMoSys** (Health Monitoring System) is a modular Python-based application for analysing aircraft sensor data, detecting system faults and displaying alerts in a intuitive, user-friendly graphical interface.  

It integrates data validation, fault detection, alert management and data visualisation into one cohesive system.

The system was designed with Object Oriented Principles (OOP) in mind, including encapsulation, abstraction, inheritance and polymorphism, to ensure modularity, scalability and maintainability.

![HeMoSys GUI Screenshot](Images/HeMoSys_GUI.png)

---

## Key Features

- **CSV Sensor Data Upload**  
  Upload aircraft sensor data via the Graphical User Interface (GUI) for automated analysis.

- **Fault Detection Engine**  
  Detects anomalies in sensor readings based on predefined JSON fault rules.

- **Alert Management**  
  Creates, stores, resolves and deletes alerts using a persistent database backend.

- **Interactive Graphical Interface (Tkinter)**  
  Displays all alerts in a sortable table and visualises alert frequency in an hourly bar chart.

- **Fault Rules Configuration**  
  Fault thresholds are defined in a JSON file, enabling easy rule updates without changing source code.

- **Error Handling and Logging**  
  Handles invalid input, file errors and database connection issues gracefully, with detailed log entries.

---

## System Architecture

HeMoSys follows a layered modular architecture:

| Module | Responsibilities |
|-------|------------------|
| **UserInterface** | Handles user inputs, CSV upload and displays currently active alerts in the GUI. |
| **SensorIntegration** | Handles data validation and passes cleaned pandas DataFrame to the FaultDetection module. |
| **FaultDetection** | Detects faults in the cleaned DataFrame based on predetermined fault rules. Passes Fault objects to the AlertModule to be raised as Alerts. |
| **AlertModule** | Creates alerts from applicable faults and passes them to the Database. Managed alert data. |
| **Database** | Stores alert records persistently in an SQLite database that is auto-created at runtime. |

### Data Flow Summary
1. The user uploads a sensor CSV via the GUI.  
2. `SensorIntegration` validates and cleans the data.  
3. `FaultDetection` checks values against fault rules (JSON).  
4. Detected faults are converted into alerts via the `AlertModule`.  
5. Alerts are stored in the database and displayed in the GUI table and graph.

---

## Module Overview

### **UserInterface (Tkinter)**
- Provides the main application window, table view and alert graph.  
- Supports uploading CSVs, filtering alerts by severity and performing resolve/delete actions.  
- Embeds a Matplotlib graph showing alert frequency per hour.

### **SensorIntegration**
- Handles reading, cleaning and validating CSV sensor data.  
- Ensures data consistency before passing it to `FaultDetection`.

### **FaultDetection**
- Loads predefined fault rules from `fault_rules.json`.  
- Compares validated sensor readings to thresholds.  
- Generates `Fault` objects when rule conditions are met.

### **AlertModule**
- Manages creation, retrieval and deletion of alerts.  
- Interacts with the database to persist alerts.  
- Supports updating alert statuses (active/resolved).

### **Database**
- Implements CRUD operations using SQLite.  
- Abstracted through a data access class to maintain encapsulation.

---

##  Testing

- Unit tests verify functionality across all modules (data processing, fault detection and alert management).  
- Requirements-based testing ensures each functional and non-functional requirement is validated.  
- Mock database and test CSV files are used to simulate end-to-end workflows.

---

## Setup & Run
```
git clone https://github.com/TriGuys/aerospace-sim-engine.git
cd aerospace-sim-engine
pip install
python main.py
```

---

## Configuration

- **Fault Rules**: Defined in `fault_rules.json` (editable without code changes).
- **Database**: alerts.db auto-created at runtime.
- **Logs**: Generated in hemosys.log for debugging and system monitoring.

---

## Contributors 
[Dom Brown](https://github.com/dombrown95) - Fault Detection and User Interface </br>
[Flinn Mort](https://github.com/nnilf) - Alert Module and Database </br>
[Kyle Rothery](https://github.com/KMarshall33) - Sensor Integration and Automated Testing