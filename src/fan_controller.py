"""
Author: Evelyn Boettcher, DiDacTex, LLC
Date: Aug 2022

This is a fan controller for a Minka Aire Fan

License MIT
"""

from cmath import pi
from threading import Thread
import RPi.GPIO as GPIO
import datetime
import time
import subprocess
import shlex


def send_command_many(FAN, command_str, n=3):
    time.sleep(.2)
    for ii in range(n):
        FAN.send_command(command_str)
        time.sleep(1)


def start_subprocess(command, str_cmd=False):
    """
    INPUTS:
    =======
        command: str
            bash command
        str_cmd: Bool
            if True runs as a true shell
    RETURNS:
    ========
        out: str
        err: str
    """
    if str_cmd:
        args = command
        with subprocess.Popen(args, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              shell=True) as p:
            out, err = p.communicate()
    else:
        args = shlex.split(command)
        with subprocess.Popen(args, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, ) as p:
            out, err = p.communicate()
    return out, err


class FanRemote(object):
    def __init__(self, *args, **kwargs):
        self.GPIO_pin = 4  # BCM 4 or Pi pin 7
        self.fan_type = "minka-aire"
        # 8 pin fan ID on back of controller near battery
        self.fan_id = "".join(["0000", "1000"])
        self.time = datetime.datetime.now()
        self.freq = str(304000000)
        self.status = {"fan-on": 2, "fan-off": 10}
        self.stop_itermittent = False
        self.GPIO_pinfan_off = True
        self.fan_light = 1 # Keep track of the light is on/off
        self.thread = None

    def run_command(self, command):
        if command is None:
            return
        current_time = datetime.datetime.now()
        if (current_time-self.time).seconds < 1:
            # Debounce (e.g making sure that if you double/multi 
            # click same command does not go through)
            return
        
        self.time = current_time
        if command == "light_on" and self.fan_light:
            command = "light_off"
            self.fan_light = 0
        else:
            self.fan_light = 1
        command_str = self.make_command(command)  
        if self.thread is not None:
            self.thread.join()
        self.thread = Thread(target=send_command_many, args=(self, command_str))
        self.thread.start()

    def make_command(self, command):
        sendook = "sudo rpitx/sendook "
        if command == "light_on" or "light_off":
            fan_signal_settings = " -0 333 -1 333 -r 2 -p 10000 "
        else:
            fan_signal_settings = " -0 333 -1 333 -r 4 -p 10000 "
        fan_id = ""
        for ii in range(8):
            ook = self.fan_ook()[self.fan_id[ii]]
            fan_id += ook
        fan_code = self.fan_codes(command)
        fan_command = ""
        for ii in range(5):
            ook = self.fan_ook()[fan_code[ii]]
            fan_command += ook
        cmd_str = sendook + " -f " + self.freq + fan_signal_settings + fan_id + fan_command
        print(cmd_str)
        return cmd_str

    def send_command(self, command_str):
        start_subprocess(command_str, False)

    def fan_sleep(self):
        # Clear the GPIO Pins
        GPIO.cleanup()
        return

    def fan_wakeup(self):
        # Activate the GPIO pins
        # Not Needed for RPITX b
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GPIO_pin, GPIO.IN)
        return

    def fan_ook(self):
        """
        Other fans can be added here
        Need to know what to send when the bit is a 1 or 0
        """
        fan = {"minka-aire": {"1": "101", "0": "100"}, }
        return fan.get(self.fan_type, {"1": "101", "0": "100"})

    def fan_codes(self, action):
        """
        Dictionary of fan bit codes
        """
        fan = {"light_on": "01010",
               "light_off": "10010",
               "fan_low": "00100",
               "fan_med": "01000",
               "fan_high": "10000",
               "fan_off": "10100",
               "fan_reverse": "00010",
            }

        return fan.get(action)







