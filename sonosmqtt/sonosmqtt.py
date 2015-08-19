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
        self.pub_topic = mqtt_settings.get('topic')

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        if self.user:
            self.client.username_pw_set(self.user, self.password)

        self.client.connect(self.server, self.port, 60)

    def on_connect(self, client, userdata, flags, rc):
        print ("Connected to mqtt server")

        client.subscribe(self.sub_topic)

    def on_message(self, client, userdata, msg):
        print (msg.topic+" | "+str(msg.payload))

    def publish(self, topic, message):
        topic = "/".join((self.pub_topic, topic))
        self.client.publish(topic, payload=message, qos=0, retain=True)

    def loop(self):
        self.client.loop(timeout=0.5)

print settings
devices = soco.discover()

if __name__ == '__main__':

    MQ = MQTT_Client(settings.get('mqtt'))
    sonos_devs = dict()
    for dev in devices:
        ct = dev.get_current_track_info()
        sonos_devs[dev] = ct.get('uri', None)

    print("initial dictionary: ", sonos_devs)


    while True:
        # get current playing tracks from sonos
        for dev, last_track_uri in sonos_devs.items():
            ct = dev.get_current_track_info()
            if ct.get('uri', None) != last_track_uri:
                #print("{} : {} - {} ({})".format(dev.player_name, ct.get('artist'), 
                    #ct.get('title'), ct.get('duration')))
                sonos_devs[dev] = ct.get('uri', None)
                MQ.publish(dev.player_name.lower() + "/now_playing",
                "{} - {} ({})".format(ct.get('artist'), ct.get('title'),
                    ct.get('duration')))

        # push to mqtt
        MQ.loop()
