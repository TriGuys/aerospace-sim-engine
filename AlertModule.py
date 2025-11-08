import logging
from typing import List
from Abstractions import AlertCreation, Alert, Status
from Database import AlertDatabase

# Configure logging for module.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class AlertModule:
    def __init__(self, database: AlertDatabase) -> None:
        """Initialise the AlertModule with a reference to the AlertDatabase."""
        self.database: AlertDatabase = database
        self.alerts: List[Alert] = self.database.get_all()
        logging.info("AlertModule initialised with %d existing alerts.", len(self.alerts))

    def create_alert(self, sensor_id: str, fault_code: str, severity: str, message: str, timestamp: str) -> Alert:
        """
        Creates a new alert and stores it in the database.

        Args:
            sensor_id: str
            fault_code: str
            severity: str
            message: str
            timestamp: str

        Returns:
            Alert: Alert created.
        """
        try:
            alert_data = AlertCreation(
                sensor_id=sensor_id,
                fault_code=fault_code,
                severity=severity,
                message=message,
                timestamp=timestamp
            )

            alert: Alert = self.database.create(alert_data)
            self.alerts.append(alert)

            logging.info(
                "Created alert for sensor '%s' with fault '%s' (severity: %s, timestamp: %s).",
                sensor_id, fault_code, severity, timestamp
            )
            return alert
        
        except Exception as e:
            logging.error("Failed to create alert for sensor '%s': %s", sensor_id, e)
            raise
    
    def get_all_alerts(self) -> List[Alert]:
        """Retrieve all alerts from the database."""
        try:
            self.alerts = self.database.get_all()
            logging.info("Retrieved %d alerts from the database.", len(self.alerts))
            return self.alerts
        except Exception as e:
            logging.error("Error retrieving alerts from database: %s", e)
            raise
    
    def resolve_alert(self, alert_id: int) -> bool:
        """Mark an alert as resolved in the database."""
        try:
            updated = self.database.update_status(alert_id, Status.RESOLVED)
            if updated:
                logging.info("Marked alert ID %d as resolved.", alert_id)
                return True
            else:
                logging.warning("Attempted to resolve alert ID %d but it was not found.", alert_id)
                return False
        except Exception as e:
            logging.error("Failed to resolve alert ID %d: %s", alert_id, e)
            raise

    def unresolve_alert(self, alert_id: int) -> bool:
        """Mark a resolved alert as active again in the database."""
        try:
            updated = self.database.update_status(alert_id, Status.ACTIVE)
            if updated:
                logging.info("Reactivated alert ID %d (set to Active).", alert_id)
                return True
            else:
                logging.warning("Attempted to reactivate alert ID %d but it was not found.", alert_id)
                return False
        except Exception as e:
            logging.error("Failed to reactivate alert ID %d: %s", alert_id, e)
            raise

    def delete_alert(self, alert_id: int) -> bool:
        """Delete an alert from the database."""
        try:
            alert_id = int(alert_id)
            deleted: bool = self.database.delete(alert_id)
            if deleted:
                self.alerts = [a for a in self.alerts if a.alert_id != alert_id]
                logging.info("Deleted alert ID %d successfully.", alert_id)
            else:
                logging.warning("Attempted to delete alert ID %d, but it was not found.", alert_id)
            return deleted
        except ValueError:
            logging.error("Invalid alert ID provided: %s (must be numeric)", alert_id)
            return False
        except Exception as e:
            logging.error("Failed to delete alert ID %d: %s", alert_id, e)
            raise