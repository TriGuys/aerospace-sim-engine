from Abstractions import AlertCreation, Alert
from Database import AlertDatabase

class AlertModule:
    def __init__(self, database: AlertDatabase):
        self.database = database
        self.alerts : list[Alert] = self.database.get_all()

    def create_alert(self, sensor_id: str, fault_code: str, severity: str, message: str, timestamp: str) -> Alert:
        """Create a new alert and store it in the database."""
        create_alert = AlertCreation(
            sensor_id = sensor_id,
            fault_code = fault_code,
            severity = severity,
            message = message,
            timestamp = timestamp
        )

        alert = self.database.create(create_alert)
        self.alerts.append(alert)
        return alert
    
    def get_all_alerts(self) -> list[Alert]:
        """Retrieve all alerts from the database."""
        self.alerts = self.database.get_all()
        return self.alerts
    
    def resolve_alert(self, alert_id: int) -> None:
        """Mark an alerts as resolved (Needs to be expanded to mark in database)."""
        pass

    def delete_alert(self, alert_id: int) -> bool:
        """Delete an alert from the database."""
        deleted = self.database.delete(alert_id)
        if deleted:
            self.alerts = [a for a in self.alerts if a.alert_id != alert_id]
        return deleted