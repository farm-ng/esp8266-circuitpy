#!/bin/bash -ex

# Argument passed is CIRCUITPY mounted drive (WSL)
# Expects boot.py to exist on CIRCUITPY drive already

cp esp8266.py /mnt/$1/
cp httpParser.py /mnt/$1/
cp example/http-get-post/main.py /mnt/$1/
touch /mnt/$1/NO_USB
