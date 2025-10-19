from AlertModule import AlertModule
from FaultDetection import FaultDetection
from FaultDetection import Fault
from SensorIntegration import SensorIntegration

def main():
    alert_module = AlertModule()
    fault_detection = FaultDetection()
    sensor_integration = SensorIntegration()
    fault = Fault()

if __name__ == "__main__":
    main()