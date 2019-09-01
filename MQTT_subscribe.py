import paho.mqtt.client as mqtt
from twilio.rest import Client
from app import db
from app.models import User, Temperature_Sensor, Device, Humidity_Sensor, Rainfall_Sensor, Smoke_Sensor, Fire_Sensor, Soil_Moisture_Sensor, GPS_Module, Image
import time
import json
from collections import Counter
import redis

ACCOUNT_SID= 'AC6c443352f12f7d72745b17fb6254267a'
AUTH_TOKEN= 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    client.subscribe("digitest/test1")  # Subscribe to the topic “digitest/test1”, receive any messages published on it


def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    print("Message received: " + msg.topic + " " + str(msg.payload))  # Print a received msg
    payload="""%s""" %(str(msg.payload))
    payload=payload[2:-1]
    msg_string = str(payload)
    msg_dict=json.loads(msg_string)
    
    device_id=msg_dict['device_id']
    temperature_id=msg_dict['temperature_id']
    temperature_reading=msg_dict['temperature_reading']
    humidity_id=msg_dict['humidity_id']
    humidity_reading=msg_dict['humidity_reading']
    rainfall_id=msg_dict['rainfall_id']
    rainfall_reading=msg_dict['rainfall_reading']
    smoke_id=msg_dict['smoke_id']
    smoke_reading=msg_dict['smoke_reading']
    fire_id=msg_dict['fire_id']
    fire_reading=msg_dict['fire_reading']
    soil_moisture_id=msg_dict['soil_moisture_id']
    soil_moisture_reading=msg_dict['soil_moisture_reading']
    GPS_latitude=msg_dict['GPS_latitude']
    GPS_longitude=msg_dict['GPS_longitude']
    image_bears=msg_dict['image_bears']
    image_deer=msg_dict['image_deer']
    image_lynx=msg_dict['image_lynx']
    image_wolves=msg_dict['image_wolves']

    d=Device.query.filter_by(device_id=device_id).first()
    t=Temperature_Sensor(sensor_id=temperature_id, reading=temperature_reading, device_id=d.id)
    h=Humidity_Sensor(sensor_id=humidity_id, reading=humidity_reading, device_id=d.id)
    r=Rainfall_Sensor(sensor_id=rainfall_id, reading=int(rainfall_reading), device_id=d.id)
    s=Smoke_Sensor(sensor_id=smoke_id, reading=int(smoke_reading), device_id=d.id)
    f=Fire_Sensor(sensor_id=fire_id, reading=int(fire_reading), device_id=d.id)
    sm=Soil_Moisture_Sensor(sensor_id=soil_moisture_id, reading=soil_moisture_reading, device_id=d.id)
    g=GPS_Module(latitude=GPS_latitude, longitude=GPS_longitude, device_id=d.id)
    i=Image(bears=int(image_bears), deer=int(image_deer), lynx=int(image_lynx), wolves=int(image_wolves), device_id=d.id)

    print("Adding New Data for Device " + str(device_id) + " to Database" )
    print("Adding New Temperature Data for Sensor " + str(temperature_id) + " to Database" )
    db.session.add(t)
    print("Adding New Humidity Data for Sensor " + str(humidity_id) + " to Database" )
    db.session.add(h)
    print("Adding New Rainfall Data for Sensor " + str(rainfall_id) + " to Database" )
    db.session.add(r)
    print("Adding New Smoke Data for Sensor " + str(smoke_id) + " to Database" )
    db.session.add(s)
    print("Adding New Fire Data for Sensor " + str(fire_id) + " to Database" )
    db.session.add(f)
    print("Adding New Soil Moisture Data for Device " + str(soil_moisture_id) + " to Database" )
    db.session.add(sm)
    print("Adding New GPS Latitude " + str(GPS_latitude) + " and Longitude " + str(GPS_longitude) +" to Database" )
    db.session.add(g)
    print("Adding New Image Data to Database" )
    db.session.add(i)
    db.session.commit()

    u=User.query.filter_by(id=d.user_id).first()
    print("fire reading is:" + str(fire_reading))
    if fire_reading == 1:
        send_alarm_msg("+17372153857", "+"+u.phone, device_id, GPS_latitude, GPS_longitude)
        # with open("msg_counter.json", 'r') as f:
        #     msg_counter = Counter(json.load(f))
        # if msg_counter[u.phone] % 5 == 0:
        #     msg_counter[u.phone] += 1
        #     send_alarm_msg("+17372153857", "+"+u.phone, device_id, GPS_latitude, GPS_longitude)

        # else:
        #     # don't send message but increment counter
        #     msg_counter[u.phone] += 1
        # with open("msg_counter.json", 'w') as f:
        #     json.dump(msg_counter, f)

def send_alarm_msg(from_num, to_num, device_id, gps_lat, gps_long):
    """ Send alarm message with Twilio if we found a fire. """
    client=Client(ACCOUNT_SID, AUTH_TOKEN)
    message=client.messages.create(body=f"Wildfire Detected - Device {device_id}. At Location {gps_lat}N {gps_long}W.",from_=from_num,to=to_num,)
    print(message.sid)

def mqtt_update_job():
    client = mqtt.Client("digi_mqtt_test")  # Create instance of client with client ID “digi_mqtt_test”
    client.on_connect = on_connect  # Define callback function for successful connection
    client.on_message = on_message  # Define callback function for receipt of a message
    print("connecting to broker")
    client.connect("test.mosquitto.org", 1883, 60)  # Connect to (broker, port, keepalive-time)
    #client.connect("broker.hivemq.com", 1883, 60)
    timeout = time.time() + 60*5 - 5   # 4:55 minutes from now
    while(True):
        if time.time() > timeout:
                break
        client.loop(timeout=60)
