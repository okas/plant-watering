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


@mod.route('/hello/', defaults={'name':None})
@mod.route('/hello/<name>')
def hello(name):
	return render_template('page.html',
							index_url=url_for('.index_page'),
							name=name)

#=======================================================================

@mod.route('/led-red')
def led_control():
	led = PWMLED(17)
	led.on()
	sleep(2)
	led.off()
	led.close()
	flash('Red LED was lit for 2 seconds, right?')
	return render_template('led_control.html')


led_blue = None

@mod.route('/led-blue')
def led_pulse():
	global led_blue
	if led_blue == None:
		led_blue = PWMLED(22)
		led_blue.pulse()
		message1 = 'off'
		message2 = 'pulsing'
	else:
		led_blue.close()
		led_blue = None
		message1 = 'pulsing'
		message2 = 'off'
	
	flash('Blue LED was %s and now is %s, right?' % (message1, message2))
	return render_template('led_control.html', go_to=message1)


@mod.route('/button-state')
def button_state():
	return "Button is %s" % Button(13).value
	
