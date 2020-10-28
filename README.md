# CO2Zero

`git clone https://github.com/brischniz/co2zero`

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
