#!/usr/bin/python3

import time, sys, socket
from collections import deque
from datetime import datetime
from gpiozero import LED
from gpiozero import PWMLED

# Temoperatursensor DHT11
# https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup
import board, Adafruit_DHT

# CO2 Sensor
from sgp30 import SGP30
import lcd as lcd

SLIDING_WINDOWS_SIZE = 30
sgp30 = SGP30()

def crude_progress_bar():
    sys.stdout.write('.')
    sys.stdout.flush()

# CO2-Sensor initialisieren
# sgp30.start_measurement(crude_progress_bar)

led_g = None
led_y = None
led_r = None

def init_leds():
    global led_g, led_y, led_r
    led_g = LED(17)
    led_y = LED(27)
    led_r = LED(22)

def allLightsOff():
    led_g.off()
    led_y.off()
    led_r.off()
    # sys.exit(0)

def green():
    led_g.on()
    led_y.off()
    led_r.off()

def yellow():
    led_g.off()
    led_y.on()
    led_r.off()

def red():
    led_g.off()
    led_y.off()
    led_r.on()

def getPollutionData():
    """
    Liefert den PPM-Wert fuer CO2
    :return: int
    """
    result = sgp30.get_air_quality()
#    print(str(result.equivalent_co2))
    return result.equivalent_co2


def main():
    # signal.signal(signal.SIGINT, allLightsOff)
    ppmQueue = deque(maxlen=SLIDING_WINDOWS_SIZE)

    while True:

        try:
            ppm = getPollutionData()
            ppmQueue.append(ppm)
            mov_average_ppm = int(sum(ppmQueue) / SLIDING_WINDOWS_SIZE)

            msg1 = "Aktuell: " + str(ppm)
            msg2 = "CO2 Wert: " + str(mov_average_ppm)
            temperatur = str(Adafruit_DHT.read_retry(11, 4))
            now = datetime.now()
            uhrzeit = now.strftime("%H:%M") 
            msg3 = temperatur[7:-1] + "C  " + uhrzeit + " Uhr"

            print(msg1 + ", " + msg2 + ", " + msg3)

            lcd.lcd_string(msg2, lcd.LCD_LINE_1)
            lcd.lcd_string(msg3, lcd.LCD_LINE_2)

            if mov_average_ppm in range(0, 1000):
                green()
            elif mov_average_ppm in range(1001, 2000):
                yellow()
            elif mov_average_ppm in range(2001, 3000):
                red()
            else:
                led_r.blink()

            time.sleep(1)
        except Exception as error:
            print(error)


if __name__ == "__main__":
    lcd.lcd_init()

    print("CO2Zero startet, bitte warten...")
    pwm_g = PWMLED(17)
    pwm_y = PWMLED(27)
    pwm_r = PWMLED(22)
    pwm_g.pulse()
    pwm_y.pulse()
    pwm_r.pulse()

    # hostname = socket.gethostname()
    # ip_address = socket.gethostbyname(hostname + ".local")
    lcd.lcd_string("CO2Zero startet, bitte warten...", lcd.LCD_LINE_1)
    # lcd.lcd_string(ip_address, lcd.LCD_LINE_2)

    # print("IP: " + ip_address)

    time.sleep(5)

    pwm_g.close()
    pwm_y.close()
    pwm_r.close()

    init_leds()

    main()

