# Sencor SWS 12500 HA proxy server

## Introduction 
This project is meant to fix some issues with the Sencor SWS 12500 weather station, mainly that it is hard to set up locally.
It intercepts data from the weather station and sends it to home assistant or any other MQTT broker.


## Weather station config

Here you have two options:

#### 1. (Better) change local dns of rtupdate.wunderground.com to the machine that will be running this script - setup the station normally or if its already set up no reconfig required, just unplug and plug in the display of the station.

#### 2. (Flaky) enter the machine IP and port (+WUnderground key and ID if you want forwarding to wunderground) in the custom server section. This method did not always work so any feedback welcome! 

## Program Setup


### 1. Install dependencies
```shell
pip3 install -r requirements.txt
```

### 2. Copy config.example.ini -> config.ini and fill out values

### 3. Run the script :)
```shell
python3 sencor-sws-12500-ha.py
```

