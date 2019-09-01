import collections
from flask import Flask     #importing classes from modules
from config import Config
from flask_sqlalchemy import SQLAlchemy #importing flask extensions
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from redis import Redis
import rq
from rq_scheduler import Scheduler
from datetime import datetime
from flask_bootstrap import Bootstrap

app = Flask(__name__)       #predetermined python variable to config Flask correctly
                            #creates an app package that is an instance of class Flask
app.config.from_object(Config)

db = SQLAlchemy(app)       #object that represents database
migrate = Migrate(app, db)  #object that represents migration engine
login = LoginManager(app)   #object that represents user logged-in state manager
login.login_view='login'    #user will always be redirected to login page until they are successfully logged in
bootstrap = Bootstrap(app)
moment=Moment(app)


from celery import Celery
from celery.schedules import crontab
from celery import Celery

def make_celery(app):
    celery = Celery(
        app.import_name,
        result_backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
celery = make_celery(app)
#celery.conf.task_routes = {'mqtt': {'queue': 'mqtt'}}

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    #Calls test('hello') every 300seconds.
    sender.add_periodic_task(300.0, mqtt_test.s(), name='add every 300.0')
app.text_counter = collections.Counter()
from app import MQTT_subscribe
@celery.task()
def mqtt_test():
    try:
        MQTT_subscribe.mqtt_update_job()
    except Exception as e:
	    #self.retry(z)
        pass

#app.redis = Redis.from_url(app.config['REDIS_URL'])
#app.task_queue = rq.Queue('wildfire', connection=app.redis)
#job = app.task_queue.enqueue('app.MQTT_subscribe.mqtt_update_job')

# app.scheduler = Scheduler(queue=app.task_queue, connection=app.redis)
# app.scheduler.schedule(
#      scheduled_time=datetime.utcnow(), # Time for first execution, in UTC timezone
#      func=MQTT_subscribe.mqtt_update_job,                     # Function to be queued
#      args=[],
#      kwargs={},
#      interval=300,                   # Time before the function is called again, in seconds
#      repeat=None,                   # Repeat this number of times (None means repeat forever)
#      meta={'foo': 'bar'}            # Arbitrary pickleable data on the job itself
#  )

from app import routes, models     #instanced at the bottom to avoid circular imports