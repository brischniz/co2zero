# CO2Zero

`git clone https://github.com/brischniz/co2zero`

## Installation
```
sudo apt install python3-gpiozero
sudo apt-get install python-influxdb

```

## Autostart

```
sudo cp co2zero.service /etc/systemd/system/
sudo systemctl start co2zero.service
sudo systemctl enable co2zero.service
``


## /boot/config.txt

```
dtoverlay=i2c-gpio,bus=4,i2c_gpio_delay_us=1,i2c_gpio_sda=23,i2c_gpio_scl=24
```

## Links
- http://raspberrypi.ws/

### I2C aktivieren
- https://developer-blog.net/raspberry-pi-i2c-aktivieren/

### Temperatursensor
- https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup
- https://www.circuitbasics.com/how-to-set-up-the-dht11-humidity-sensor-on-the-raspberry-pi/
