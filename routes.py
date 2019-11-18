from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, DeviceForm
from app.models import User, Device, Temperature_Sensor, Humidity_Sensor, Rainfall_Sensor, Soil_Moisture_Sensor, Smoke_Sensor, Fire_Sensor, GPS_Module, Image
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from sqlalchemy import desc

#route to home page 
#decorators to modify functions 
#for each of the following URLs Flask will pass the return value to the browserç
@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required #protects the main page from unauthorized viewers
def index():
    form=DeviceForm()
    if form.validate_on_submit(): 
        device=Device.query.filter_by(device_id=form.device_id.data).first()  # search the database for the user that has matching username 
        if device is None: # if the username is not in the database or the password is does not match
            flash('Invalid Device ID.')
            return redirect(url_for('index'))
        else:
            if device.user_id is None:
                device.user_id=current_user.id
                db.session.commit()
                return redirect(url_for('device', device_id=str(device.device_id)))
            else:
                if device.user_id == current_user.id:
                    return redirect(url_for('device', device_id=str(device.device_id)))
                elif device.user_id != current_user.id:
                    flash('Invalid Device ID.')
                    return redirect(url_for('index'))
    return render_template('index.html', title='Home', form=form)       # returns the template with the now filled in variables

@app.route('/device/<device_id>')
@login_required
def device(device_id):
    device_title=device_id
    device=Device.query.filter_by(device_id=device_id).first()
    single_device_id=device.id
    temp=Temperature_Sensor.query.filter_by(device_id=single_device_id).order_by(desc(Temperature_Sensor.timestamp)).first()  
    humd=Humidity_Sensor.query.filter_by(device_id=single_device_id).order_by(desc(Humidity_Sensor.timestamp)).first()    
    rain=Rainfall_Sensor.query.filter_by(device_id=single_device_id).order_by(desc(Rainfall_Sensor.timestamp)).first()  
    smoke=Smoke_Sensor.query.filter_by(device_id=single_device_id).order_by(desc(Smoke_Sensor.timestamp)).first()  
    fire=Fire_Sensor.query.filter_by(device_id=single_device_id).order_by(desc(Fire_Sensor.timestamp)).first() 
    sm=Soil_Moisture_Sensor.query.filter_by(device_id=single_device_id).order_by(desc(Soil_Moisture_Sensor.timestamp)).first()  
    gps=GPS_Module.query.filter_by(device_id=single_device_id).order_by(desc(GPS_Module.timestamp)).first()  
    images=Image.query.filter_by(device_id=single_device_id).order_by(desc(Image.timestamp)).first()  

    if fire.reading == 1:
        fire_reading = " Fire Detected"
    else:
        fire_reading = " No Fire Detected"
    
    if smoke.reading == 1:
        smoke_reading = " Smoke Detected"
    else:
        smoke_reading = " No Smoke Detected"

    if rain.reading == 1:
        rain_reading = " Current Rainfall Detected"
    else:
        rain_reading = " No Rain Detected"

    import requests

    gps_lat = gps.latitude
    gps_long = gps.longitude

    lat=gps_lat[:-1]
    lon=gps_long[:-1]
    current_weather_url = 'http://api.weatherstack.com/current?access_key=90a599db6293c173bdbabf8d63354946&query='
    final_current_weather_url = current_weather_url + lat + ',' + lon
    response = requests.get(final_current_weather_url)
    data = response.json()
    print("accessing weather data from apixu...")
    print("for latitude: "+lat+" and longitude: "+lon)
    print("the wind speed in mph is: " + str(data['current']['wind_speed']))
    print("the wind degree is: " + str(data['current']['wind_degree']))
    print("the wind direction is: " + str(data['current']['wind_dir']))
    wind = [
        {
            'data' : {'wind_data' : 'Wind Speed'},
            'reading' : str(data['current']['wind_speed'])
        },
        {
            'data' : {'wind_data' : 'Wind Degree'},
            'reading' : str(data['current']['wind_degree'])
        },
        {
            'data' : {'wind_data' : 'Wind Direction'},
            'reading' : str(data['current']['wind_dir'])
        }
    ]

    #precipitation=data['current']['precip_mm']


    sensors = [
        {
            'type' : 'Fire',
            'data' : {'sensor' : fire.sensor_id},
            'reading' : fire_reading,
            'unit' : ''
        },
        {
            'type' : 'Smoke',
            'data' : {'sensor' : smoke.sensor_id},
            'reading' : smoke_reading,
            'unit' :''
        },
        {
            'type' : 'Temperature',
            'data' : {'sensor' : temp.sensor_id},
            'reading' : temp.reading,
            'unit' :'° C'
        },
        {
            'type' : 'Humidity',
            'data' : {'sensor' : humd.sensor_id},
            'reading' : humd.reading,
            'unit' :'%'
        },
        {
            'type' : 'Rainfall',
            'data' : {'sensor' : rain.sensor_id},
            'reading' : rain_reading,
            'unit' :''
        },
        # {
        #     'type' : 'Precipitation',
        #     'data' : {'sensor' : rain.sensor_id},
        #     'reading' : precipitation,
        #     'unit' :'mm'
        # },
        {
            'type' : 'Soil Moisture',
            'data' : {'sensor' : sm.sensor_id},
            'reading' : sm.reading,
            'unit' :'%'
        },
    ]
    
    timestamp=temp.timestamp

    gps = [
        {
            'type' : 'Latitude',
            'reading' : gps.latitude,
            'unit' : ' '
        },
        {
            'type' : 'Longitude',
            'reading' : gps.longitude,
            'unit' : ' '            
        }
    ]
    
    images = [
        {
            'animal' : 'Bears',
            'reading' : images.bears
        },
        {
            'animal' : 'Deer',
            'reading' : images.deer
        },
        {
            'animal' : 'Lynx',
            'reading' : images.lynx
        },
        {
            'animal' : 'Wolves',
            'reading' : images.wolves
        }
    ]

    CBI=(((110-1.373*float(humd.reading))-0.54*(10.20-float(temp.reading)))*124*10**(-0.0142*float(humd.reading)))/60
    
    if CBI <= 50:
        fire_danger_level= "Low"
    elif 50 < CBI <= 75:
        fire_danger_level= "Moderate"
    elif 75 < CBI <= 90:
        fire_danger_level= "High"
    elif  90 < CBI <= 97.5:
        fire_danger_level= "Very High"
    elif CBI > 97.5:
        fire_danger_level= "Extreme"
    else:
        fire_danger_level= "Error"

    if 0 <= float(data['current']['wind_speed']) < 4:
        rate_of_spread=1
    elif 4 <= float(data['current']['wind_speed']) < 8:
        rate_of_spread=2
    elif 8 <= float(data['current']['wind_speed']) < 13:
        rate_of_spread=3
    elif 13 <= float(data['current']['wind_speed']) < 19:
        rate_of_spread=5
    elif 19 <= float(data['current']['wind_speed']) < 25:
        rate_of_spread=7
    elif 25 <= float(data['current']['wind_speed']) < 32:
        rate_of_spread=8
    elif 32 <= float(data['current']['wind_speed']) < 38:
        rate_of_spread=11
    elif 38 <= float(data['current']['wind_speed']):
        rate_of_spread=12
    else: 
        rate_of_spread=0



    no_fire_predictions = [
        {
            'type' : 'Fire Danger Level',
            'reading' : fire_danger_level
        },
        {
            'type' : 'CBI',
            'reading': CBI
        }
    ]

    fire_predictions = [
        {
            'type'  : 'Rate of Fire Spread',
            'reading' : rate_of_spread,
            'unit' : ' mph'
        },
        {
            'type'  : 'Direction of Fire Spread',
            'reading' : str(data['current']['wind_dir']),
            'unit' : ''
        }
    ]

    return render_template('device.html', title='Device Information', device_title=device_title, sensors=sensors, gps=gps, images=images, wind=wind, fire_alarm=fire.reading, no_fire_predictions=no_fire_predictions, fire_predictions=fire_predictions, timestamp=timestamp)

@app.route('/login', methods=['GET', 'POST'])       #view function accepts post get and post requests, rather than just get request default
def login():
    if current_user.is_authenticated:   # if user is currently logged in
            return redirect('/index')   # do not allow the user to go to the login page and redirect to index
    form = LoginForm()
    if form.validate_on_submit():       # validating user information
        user=User.query.filter_by(username=form.username.data).first()  # search the database for the user that has matching username 
        if user is None or not user.check_password(form.password.data): # if the username is not in the database or the password is does not match
            flash('Invalid username or password')     #show a message to the user that password was incorrect
            return redirect(url_for('login'))   # navigate back to login page upon unsuccessful login
        login_user(user, remember=form.remember_me.data)    # user is logged in and is now current_user
        next_page=request.args.get('index')  # get the URL of the page that the anonymous user wanted to visit
        if not next_page or url_parse(next_page).netloc != '':  # if there is not a next page or the next page is not a page on the site
            next_page=url_for('index')
        return redirect(next_page)   # navigate to the page the user tried to access upon successful login
    return render_template('login.html', title='Sign In', form=form)    # information to pass to html login form

@app.route('/logout')
def logout():
    logout_user()   # logout user by using Flask-Login's logout function
    return redirect(url_for('index'))   # redirect user to index page

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, phone=form.phone.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user_help')
@login_required 
def user_help():
    return render_template('user_help.html', title='User Help')
