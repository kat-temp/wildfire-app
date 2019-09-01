from app import app, db
from app.models import User, Temperature_Sensor, Device, Humidity_Sensor, Rainfall_Sensor, Smoke_Sensor, Fire_Sensor, Soil_Moisture_Sensor, GPS_Module, Image

@app.shell_context_processor #register function as shell context function
def make_shell_context():
    return {'db': db, 'User': User, 'Device': Device, 'Temperature_Sensor': Temperature_Sensor, 'Humidity_Sensor': Humidity_Sensor, 'Rainfall_Sensor': Rainfall_Sensor, 'Smoke_Sensor': Smoke_Sensor, 'Soil_Moisture_Sensor': Soil_Moisture_Sensor, 'GPS_Module': GPS_Module, 'Image': Image}