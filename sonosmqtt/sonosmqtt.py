import yaml
import soco
import paho.mqtt.client as mqtt

import os

settings = yaml.load(file(os.path.join('sonosmqtt', 'config_default.yaml'), 'r'))
settings.update(yaml.load(file(os.path.join('sonosmqtt', 'config_user.yaml'), 'r')))

class MQTT_Client(object):
    def __init__(self, mqtt_settings):
        self.server = mqtt_settings.get('host')
        self.port = mqtt_settings.get('port')
        self.user = mqtt_settings.get('username', None)
        self.password = mqtt_settings.get('password', None)
        self.sub_topic = mqtt_settings.get('topic') + "/#"

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        if self.user:
            self.client.username_pw_set(self.user, self.password)

        self.client.connect(self.server, self.port, 60)

        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print ("Connected to mqtt server")

        client.subscribe(self.sub_topic)

    def on_message(self, client, userdata, msg):
        print (msg.topic+" | "+str(msg.payload))

print settings
devices = soco.discover()

if __name__ == '__main__':
    for dev in devices:
        ct = dev.get_current_track_info()
        print("{} : {} - {} ({})".format(dev.player_name, ct.get('artist'), 
            ct.get('title'), ct.get('duration')))

    MQ = MQTT_Client(settings.get('mqtt'))
