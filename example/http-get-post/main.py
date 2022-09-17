# from machine import UART, Pin
from busio import UART
from microcontroller import pin
from esp8266 import ESP8266
import time, sys


print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("RPi-Pico MicroPython Ver:", sys.version)
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

SSID = "WIFI_NETWORK_NAME"
PASSWORD = "foo-bar-baz-password"

## Create On-board Led object
# led=pin(25,pin.OUT)

## Create an ESP8266 Object
esp01 = ESP8266()
esp8266_at_ver = None

print("StartUP", esp01.startUP())
# print("ReStart",esp01.reStart())
print("StartUP", esp01.startUP())
print("Echo-Off", esp01.echoING())
print("\r\n\r\n")

"""
Print ESP8266 AT comand version and SDK details
"""
esp8266_at_ver = esp01.getVersion()
if esp8266_at_ver != None:
    print(esp8266_at_ver)

"""
set the current WiFi in SoftAP+STA
"""
esp01.setCurrentWiFiMode()

# apList = esp01.getAvailableAPs()
# for items in apList:
#    print(items)
# for item in tuple(items):
#    print(item)

print("\r\n\r\n")

"""
Connect with the WiFi
"""
print("Try to connect with the WiFi..")
while 1:
    if "WIFI CONNECTED" in esp01.connectWiFi(SSID, PASSWORD):
        print("ESP8266 connect with the WiFi..")
        break
    else:
        print(".")
        time.sleep(2)


print("\r\n\r\n")
print("Now it's time to start HTTP Get/Post Operation.......\r\n")

# while(1):

# led.toggle()
time.sleep(1)

"""
Going to do HTTP Get Operation with www.httpbin.org/ip, It return the IP address of the connected device
"""
# httpCode, httpRes = esp01.doHttpGet("www.httpbin.org","/ip","Amiga-dashboard", port=80)
# httpCode, httpRes = esp01.doHttpGet("api.thingspeak.com","/channels/1417/feeds.json","Amiga-dashboard", port=80)
# httpCode, httpRes = esp01.doHttpGet("api.thingspeak.com","/channels/1417/feeds.json?results=1","Amiga-dashboard", port=80)
httpCode, httpRes = esp01.doHttpGet(
    "www.google.com",
    "/images/branding/googlelogo/2x/googlelogo_color_120x44dp.png",
    "Amiga-dashboard",
    port=80,
)
# httpCode, httpRes = esp01.doHttpGet("www.github.com", "/farm-ng/amiga-dev-kit/releases/download/amiga-dash-v0.0.3/amiga-dash-v0.0.3.zip","Amiga-dashboard", port=80)
# httpCode, httpRes = esp01.doHttpGet("www.github.com","/farm-ng/amiga-dev-kit/raw/main/website/static/img/farm-ng_favicon.png","Amiga-dashboard", port=80)
# httpCode, httpRes = esp01.doHttpGet("raw.githubusercontent.com","/farm-ng/amiga-dev-kit/main/website/static/img/farm-ng_favicon.png","Amiga-dashboard", port=80)
print("------------- www.httpbin.org/ip Get Operation Result -----------------------")
print("HTTP Code:", httpCode)
# print("HTTP Response:",httpRes)
print(
    "-----------------------------------------------------------------------------\r\n\r\n"
)


print(type(httpRes))

if httpRes is not None:
    print("Writing to disk")
    with open("test.txt", "wb") as f:
        f.write(httpRes)

    print("Writing as image")
    with open("test.png", "wb") as f:
        f.write(httpRes)
else:
    print("No http response to write")

# storage.remount("/", True)

"""
Going to do HTTP Post Operation with www.httpbin.org/post
"""
post_json = '{"name":"Noyel"}'
httpCode, httpRes = esp01.doHttpPost(
    "www.httpbin.org",
    "/post",
    "Amiga-dashboard",
    "application/json",
    post_json,
    port=80,
)
print(
    "------------- www.httpbin.org/post Post Operation Result -----------------------"
)
print("HTTP Code:", httpCode)
print("HTTP Response:", httpRes)
print(
    "--------------------------------------------------------------------------------\r\n\r\n"
)


import os
import microcontroller

os.remove("/NO_USB")
microcontroller.reset()
