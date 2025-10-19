from Abstractions import AlertCreation, Alert
from Database import AlertDatabase

class AlertModule():

    def __init__(self, database: AlertDatabase):
        self.database = database
        self.alerts : list = AlertDatabase.get_all()

    def create_alert(self, sensor_id: str, fault_code: str, severity: str, message: str, timestamp: str):

        create_alert = AlertCreation(
            sensor_id = sensor_id,
            fault_code = fault_code,
            severity = severity,
            message = message,
            timestamp = timestamp
        )

        alert: Alert = self.database.create(create_alert)
        
        self.alerts.append(alert)

        
