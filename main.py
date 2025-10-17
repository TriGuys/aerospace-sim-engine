from AlertModule import AlertModule
from FaultDetection import FaultDetection
from SensorIntegration import SensorIntegration
from Database import AlertDatabase

def main():
    done = False

    database = AlertDatabase()
    alert_module = AlertModule(database)
    fault_detection = FaultDetection()
    sensor_integration = SensorIntegration()

    while not done:
        pass

if __name__ == "__main__":
    main()