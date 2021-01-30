#!/usr/bin/python3

import configparser
import time
import sys
from collections import deque
from datetime import datetime

# Temoperatursensor DHT11
# https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup
import Adafruit_DHT
from gpiozero import LED
from gpiozero import PWMLED
from influxdb import InfluxDBClient

import lcd as lcd
# CO2 Sensor
from sgp30 import SGP30

config_system_host_name = ""
config_influxdb_host = ''
config_influxdb_port = '8086'
config_influxdb_db_name = ''
config_influxdb_user = ''
config_influxdb_pass = ''
SLIDING_WINDOWS_SIZE = 30

config = configparser.ConfigParser()
sgp30 = SGP30()

def crude_progress_bar():
    sys.stdout.write('.')
    sys.stdout.flush()

# CO2-Sensor initialisieren
sgp30.start_measurement(crude_progress_bar)

client = None
influxdb_available = True
def init_influxdb():
    global client, influxdb_available
    try:
        client = InfluxDBClient(
            host=config_influxdb_host,
            port=config_influxdb_port,
            database=config_influxdb_db_name,
            username=config_influxdb_user,
            password=config_influxdb_pass
        )
        influxdb_version = client.ping()
        print("Connected to InfluxDB " + influxdb_version + " at " + config_influxdb_host + ":" + config_influxdb_port)
    except Exception:
        influxdb_available = False
        print("InfluxDB is not available...Continuing anyway")
        pass

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

def log_to_influxdb(data):
    if not influxdb_available:
        return

    json_body = [{
        "measurement": "air_quality",
        "tags": {
            "host": config_system_host_name
        },
        "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "fields": {
            "co2": data["co2"],
            "temp": data["temp"],
            "humidity": data["humidity"]
        }
    }]
    client.write_points(json_body)

def read_config():
    global config_system_host_name, config_influxdb_host, config_influxdb_db_name, config_influxdb_port, config_influxdb_user, config_influxdb_pass
    # TODO start script anpassen - working dir
    config.read("/home/pi/co2zero/settings.conf")

    config_system_host_name = config['co2zero']['system_host_name']
    config_influxdb_host = config['co2zero']['influxdb_host']
    config_influxdb_db_name = config['co2zero']['influxdb_db_name']
    config_influxdb_port = config['co2zero']['influxdb_port']
    config_influxdb_user = config['co2zero']['influxdb_user']
    config_influxdb_pass = config['co2zero']['influxdb_pass']
    print(config_influxdb_host)

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
            humidity, temperature = Adafruit_DHT.read_retry(11, 4)
            humidity = round(humidity, 2)
            temperature = round(temperature, 2)

            uhrzeit = datetime.now().strftime("%H:%M")
            msg3 = str(temperature) + "C  " + uhrzeit + " Uhr"

            print(msg1 + ", " + msg2 + ", " + msg3)

            lcd.lcd_string(msg2, lcd.LCD_LINE_1)
            lcd.lcd_string(msg3, lcd.LCD_LINE_2)

            if mov_average_ppm in range(0, 1001):
                green()
            elif mov_average_ppm in range(1001, 2001):
                yellow()
            elif mov_average_ppm in range(2001, 3000):
                red()
            else:
                led_r.blink()

            data = {"co2": ppm, "temp": temperature, "humidity": humidity}
            log_to_influxdb(data)

            time.sleep(1)
        except Exception as error:
            print(error)


if __name__ == "__main__":

    print("CO2Zero startet, bitte warten...")
    pwm_g = PWMLED(17)
    pwm_y = PWMLED(27)
    pwm_r = PWMLED(22)
    pwm_g.pulse()
    pwm_y.pulse()
    pwm_r.pulse()

    read_config()
    init_influxdb()
    lcd.lcd_init()

    lcd.lcd_string("CO2Zero startet,", lcd.LCD_LINE_1)
    lcd.lcd_string("bitte warten ...", lcd.LCD_LINE_2)

    time.sleep(5)

    pwm_g.close()
    pwm_y.close()
    pwm_r.close()

    init_leds()

    main()

