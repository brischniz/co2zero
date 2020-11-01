import time, signal, sys, socket
from collections import deque

# Temoperatursensor DHT11
# https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup
import board, adafruit_dht

# Ampel
# TODO https://gpiozero.readthedocs.io/en/stable/
import RPi.GPIO as GPIO

# CO2 Sensor
from sgp30 import SGP30
import lcd as lcd

SLIDING_WINDOWS_SIZE = 30
sgp30 = SGP30()

def crude_progress_bar():
    sys.stdout.write('.')
    sys.stdout.flush()

# CO2-Sensor initialisieren
sgp30.start_measurement(crude_progress_bar)

# Temperatursensor initialisieren
dhtDevice = adafruit_dht.DHT11(board.D4)

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
    """
    Liefert den PPM-Wert fuer CO2
    :return: int
    """
    result = sgp30.get_air_quality()
#    print(str(result.equivalent_co2))
    return result.equivalent_co2


def main():
    signal.signal(signal.SIGINT, allLightsOff)
    ppmQueue = deque(maxlen=SLIDING_WINDOWS_SIZE)

    while True:

        try:
            ppm = getPollutionData()
            ppmQueue.append(ppm)
            mov_average_ppm = int(sum(ppmQueue) / SLIDING_WINDOWS_SIZE)

            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity

            msg1 = "ppm: " + str(mov_average_ppm)
            msg2 = "{:.1f}C    {}% ".format(temperature_c, humidity)
            print(msg1 + ", " + msg2)
            lcd.lcd_string(msg1, lcd.LCD_LINE_1)
            lcd.lcd_string(msg2, lcd.LCD_LINE_2)

            if mov_average_ppm in range(0, 800):
                green()
            elif mov_average_ppm in range(801, 2000):
                yellow()
            else:
                red()

            time.sleep(1)
        except Exception as error:
            print(error)


if __name__ == "__main__":
    lcd.lcd_init()

    print("CO2Zero starting, please wait...")

    # hostname = socket.gethostname()
    # ip_address = socket.gethostbyname(hostname)
    lcd.lcd_string("CO2Zero starting, please wait...", 1)
    # lcd.lcd_string("IP: " + ip_address, 2)
    #
    # print("IP: " + ip_address)

    time.sleep(2)

    main()
