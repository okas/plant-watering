from flask import (
    Blueprint,
    render_template,
    url_for,
    flash,
    g,
    current_app as app
    )
from gpiozero import Button, PWMLED
from time import sleep
from .. services import test_svc

mod = Blueprint('test', __name__)

#=======================================================================
count = 0
count += 1
print(count)
@mod.after_request
def after_request(response):
    global count
    count += 1
    print (count)
    return response

#=======================================================================

@mod.route('/index')
@mod.route('/')
def index_page():
    #for plant in app.plant_waterer.plants:
        #measurement = plant.measure()
        #flash('Plant: {0.id} | state: {0.state} | '\
              #'needed moisture: {0.moist_level} | '\
              #'current moisture: {1:3f}'
              #.format(plant, measurement[1]))
    return render_template('index.html')
