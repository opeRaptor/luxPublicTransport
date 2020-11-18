# luxPublicTransport
A live timetable for public transport of Luxembourg running on the [SHA2017 badge](https://hackaday.com/2017/08/14/hands-on-with-the-shacamp-2017-badge/) written in microPython

Based on the [travelplanner.mobiliteit.lu JSON api](https://data.public.lu/en/datasets/departs-en-temps-reel-api/)

Hatchery link: https://badge.team/projects/luxpublictransport/

## Make app run on boot: ##
```python
import machine
machine.nvs_setstr("system", "default_app", "luxPublicTransport")
machine.reset()
```
## Force load the dashboard when other app is set to run on boot: ##

* Hold down START capacitive touch button located in the front of the badge
* Press and release the reset button located in the back of the badge

## Install app from store after pushing to Hatchery: ##
```python
import wifi, woezel,machine
wifi.connect()
wifi.wait()
woezel.install("luxPublicTransport")
machine.reset()
```
![timetable](https://github.com/opeRaptor/luxPublicTransport/blob/main/images/timetable.jpg)
