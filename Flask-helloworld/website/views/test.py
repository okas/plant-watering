from flask import Blueprint, render_template, url_for, flash, g
from gpiozero import Button, PWMLED
from time import sleep
from .. services import test_svc

mod = Blueprint('test', __name__)

#=======================================================================
count = 0
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
        return render_template('index.html')
