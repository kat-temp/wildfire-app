#database models

from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash #library invoked to hash user's password
from flask_login import UserMixin

class User(UserMixin, db.Model):    #UserMixin is a class that includes the appropriate implementations for user model classes
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phone = db.Column(db.String(15), index=True)
    password_hash = db.Column(db.String(128))
    devices = db.relationship('Device', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Device(db.Model):   
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(64), index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    temperature_sensors = db.relationship('Temperature_Sensor', backref='device', lazy='dynamic')
    humidity_sensors = db.relationship('Humidity_Sensor', backref='device', lazy='dynamic')
    rainfall_sensors = db.relationship('Rainfall_Sensor', backref='device', lazy='dynamic')
    smoke_sensors = db.relationship('Smoke_Sensor', backref='device', lazy='dynamic')
    fire_sensors = db.relationship('Fire_Sensor', backref='device', lazy='dynamic')
    soil_moisture_sensors = db.relationship('Soil_Moisture_Sensor', backref='device', lazy='dynamic')
    gps_modules = db.relationship('GPS_Module', backref='device', lazy='dynamic')
    images = db.relationship('Image', backref='device', lazy='dynamic')

    def __repr__(self):
        return '<Device {}>'.format(self.device_id)


class Temperature_Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.String(20))
    reading = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))

    def __repr__(self):
        return '<Temperature_Sensor {}>'.format(self.reading)


class Humidity_Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.String(20))
    reading = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))

    def __repr__(self):
        return '<Humidity_Sensor {}>'.format(self.reading)

class Rainfall_Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.String(20))
    reading = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))

    def __repr__(self):
        return '<Rainfall_Sensor {}>'.format(self.reading)

class Smoke_Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.String(20))
    reading = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))

    def __repr__(self):
        return '<Smoke_Sensor {}>'.format(self.reading)

class Fire_Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.String(20))
    reading = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))

    def __repr__(self):
        return '<Fire_Sensor {}>'.format(self.reading)

class Soil_Moisture_Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.String(20))
    reading = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))

    def __repr__(self):
        return '<Soil_Moisture_Sensor {}>'.format(self.reading)

class GPS_Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.String(10))
    longitude = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))

    def __repr__(self):
        return '<GPS_Module {}>'.format(self.latitude)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bears = db.Column(db.Integer)
    deer = db.Column(db.Integer)
    lynx = db.Column(db.Integer)
    wolves = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))

    def __repr__(self):
        return '<Image {}>'.format(self.bears)

@login.user_loader  #retrieve the id of the user everytime the user navigates to a new page
def load_user(id):
    return User.query.get(int(id))  #loading the user id from the database's user model
