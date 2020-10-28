import RPi.GPIO as GPIO
from sgp30 import SGP30
import time
import signal
import sys
import lcd as lcd

sgp30 = SGP30()

def crude_progress_bar():
    sys.stdout.write('.')
    sys.stdout.flush()

#sgp30.start_measurement(crude_progress_bar)

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

def green():
    GPIO.output(17, True)
    GPIO.output(27, False)
    GPIO.output(22, False)

def yellow():
    GPIO.output(17, False)
    GPIO.output(27, True)
    GPIO.output(22, False)

def red():
    GPIO.output(17, False)
    GPIO.output(27, False)
    GPIO.output(22, True)

def getPollutionData():
    result = sgp30.get_air_quality()
#    print(str(result.equivalent_co2))
    return result.equivalent_co2

def printMessage(ppm):
#    print(ppm)
    lcd.lcd_string("CO2: " + str(ppm), 1)

def main():
    print("Start CO2Zero")
    signal.signal(signal.SIGINT, allLightsOff)


    while True:
        ppm = getPollutionData()
        print(str(ppm))
        if ppm in range(0, 800):
            green()
        elif ppm in range(801, 2000):
            yellow()
        else:
            red()

        printMessage(ppm)
        time.sleep(1)


if __name__ == "__main__":
    lcd.lcd_init()

    print("CO2Zero starting, please wait...")
    lcd.lcd_string("CO2Zero starting, please wait...", 1)

    main()
