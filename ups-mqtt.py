# ups-mqtt.py

import os
import subprocess
import time
from time import sleep, localtime, strftime
import datetime
from configparser import ConfigParser
import shutil

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from paho.mqtt.reasoncodes import ReasonCode

if not os.path.exists('conf/config.ini'):
    shutil.copy('config.ini', 'conf/config.ini')

# Load configuration file
config_dir = os.path.join(os.getcwd(), 'conf/config.ini')
config = ConfigParser(delimiters=('=',), inline_comment_prefixes=('#'))
config.optionxform = str
config.read(config_dir)

cached_values = {}
base_topic = config['MQTT'].get('base_topic', 'home/ups')
if not base_topic.endswith('/'):
    base_topic += '/'

ups_name = config['UPS'].get('name', 'ups')
ups_host = config['UPS'].get('hostname', 'localhost')
mqtt_host = config['MQTT'].get('hostname', 'localhost')
mqtt_port = config['MQTT'].getint('port', 1883)
mqtt_user = config['MQTT'].get('username', None)
mqtt_password = config['MQTT'].get('password', None)
interval = config['GENERAL'].getint('interval', 60)

mqtt_client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
mqtt_client.username_pw_set(username=mqtt_user, password=mqtt_password)
mqtt_client.connect(mqtt_host, mqtt_port)

def process():
    ups = subprocess.run(["upsc", ups_name + "@" + ups_host], stdout=subprocess.PIPE)
    lines = ups.stdout.decode('utf-8').split('\n')

    msgs = []

    for line in lines:
        fields = line.split(':')
        if len(fields) < 2:
            continue

        key = fields[0].strip()
        value = fields[1].strip()

        if cached_values.get(key, None) != value:
            cached_values[key] = value
            topic = base_topic + key.replace('.', '/').replace(' ', '_')
            msgs.append((topic, value, 0, True))

        timestamp = time.time()
        msgs.append((base_topic + 'timestamp', timestamp, 0, True))
        msgs.append((base_topic + 'lastUpdate',
                     datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S %Z'), 0, True))
        for msg in msgs:
            print(f'Sending to topic {msg[0]}: {msg[1]}')
            mqtt_client.publish(msg[0], msg[1], msg[2], msg[3])


if __name__ == '__main__':
    while True:
        process()
        if interval > 0:
            sleep(interval)
        else:
            break
