from flask import (
    Blueprint,
    render_template,
    url_for,
    flash,
    g,
    current_app as app
    )

mod = Blueprint('index', __name__)

#=======================================================================

@mod.after_request
def after_request(response):
    return response

#=======================================================================

@mod.route('/index')
@mod.route('/')
def index_page():
    for plant in app.plant_waterer.plants:
        measurement = plant.measure(True)
        flash('Plant: {0.name} | state: {0.state} | '\
              'needed moisture: {0.moist_level} | '\
              'current moisture: {1:.2f}'
              .format(plant, measurement[1]))



    return render_template('index.html')
