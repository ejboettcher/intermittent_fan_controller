"""
Author: Evelyn Boettcher, DiDacTex, LLC
Date: Aug 2022

This is a Flask App that adjusts when a fan is on or off

License MIT
"""

from flask import Flask, flash, redirect,  \
    render_template,  request, session
import time
import sys
import os
from fan_controller import FanRemote as Fan
from threading import Thread
import datetime

app = Flask(__name__)
PERMANENT_SESSION_LIFETIME = 180
app.config.update(SECRET_KEY=os.urandom(24))
app.config.from_object(__name__)



#-------FAN FLASK APP
@app.route('/popsession')
def popsession():
    session.pop('Username', None)
    return "Session Deleted"


def sleep_check(sleep_time, check_interval, stop=lambda: False):
    """
    sleep for an overall period of time, waking up to check for a 
    stop at a given interval
     
    Inputs:
    ======
    sleep_time :: overall time to sleep in min
    check_interval :: period before semaphore checking, seconds
    stop :: semaphore function, returns True when time to exit

    Returns:
    =======
    None
    """

    # get initial time when starting
    start_time = datetime.datetime.now()

    while True:
        # check for stop, if present return
        if stop():
            return None

        # sleep for check interval
        time.sleep(check_interval)
        # get current time
        curr_time = datetime.datetime.now()
        # exit criteria is when current time i
        if (curr_time - start_time).seconds >= sleep_time * 60:
        	return None
        elif (curr_time - start_time).seconds %15 ==0:
            print(curr_time)
            


def run_intermittent(fan_speed, stop=lambda: False):
    """
    Running this as a thread with a the ability to stop this 
    thread when the fan status changes

    """
    while True:
        if fan_speed == "fan_off":
            FAN.fan_off = True
        if int(FAN.status["fan-off"]) + int(FAN.status["fan-on"]) == 0:
            FAN.fan_off = True
        if FAN.fan_off:
            break
        
        FAN.fan_wakeup()
        FAN.run_command(fan_speed)
        sleep_check(FAN.status["fan-on"], 1, stop )

        # after waking from sleep, see if we should stop
        if stop():
            print('thread exiting')
            break

        # set fan off for 50 minutes
        FAN.fan_wakeup()
        FAN.run_command("fan_off")
        sleep_check(FAN.status["fan-off"], 1, stop)

        # after waking from sleep, see if we should stop
        if stop():
            print('thread exiting')
            break


@app.route("/", methods=['GET', 'POST'])
def main():
    global at, stop_thread
    
    button = request.form.to_dict(flat=False)
    print("button", button)
    fan_command = None
    if 'light' in button:
        FAN.run_command("light_on")
        # Turn light On off
        return render_template('index.html', web_status=FAN.status)
    elif 'off' in button:
        FAN.fan_off = True
        fan_command = "fan_off"
    elif 'low' in button:
        FAN.fan_off = False
        fan_command = "fan_low"
    elif 'med' in button:
        FAN.fan_off = False
        fan_command = "fan_med"
    elif 'high' in button:
        fan_command = "fan_high"
        FAN.fan_off = False
    if at is not None:
        stop_thread = True
        at.join()  
    
    # Set the On OFF time for fan
    FAN.status['fan-on'] = int(button.get("fan-on", [2])[0])
    FAN.status['fan-off'] = int(button.get("fan-off", [20])[0])
    FAN.run_command(fan_command)
    if fan_command != "fan_off":
        stop_thread = False
        at = Thread(target=run_intermittent, args=(fan_command, lambda:stop_thread))
        at.start()
    return render_template('index.html', web_status=FAN.status)


def start_app():
    try:
        app.run(host="0.0.0.0", port=5000, threaded=True,)
        return app
    except OSError:
        print('OSError', OSError)


if __name__ == "__main__":
    at = None
    FAN = Fan()
    start_app()
