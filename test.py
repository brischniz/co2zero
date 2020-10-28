import RPi.GPIO as GPIO
import time
import signal
import sys

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

def allLightsOff(signal, frame):
    GPIO.output(17, False)
    GPIO.output(27, False)
    GPIO.output(22, False)
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, allLightsOff)
print('[Press CTRL + C to end the script!]')

while True:
    GPIO.output(22, True)
    time.sleep(1)
    GPIO.output(27, True)
    time.sleep(1)

    GPIO.output(27, False)
    GPIO.output(22, False)
    GPIO.output(17, True)
    time.sleep(1)

    GPIO.output(17, False)
    GPIO.output(27, True)
    time.sleep(1)
    GPIO.output(27, False)



