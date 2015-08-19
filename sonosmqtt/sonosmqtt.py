import yaml
import soco
import json
import paho.mqtt.client as mqtt

import os

class MQTT_Client(object):
    def __init__(self, mqtt_settings, callbacks=None):
        self.server = mqtt_settings.get('host')
        self.port = mqtt_settings.get('port')
        self.user = mqtt_settings.get('username', None)
        self.password = mqtt_settings.get('password', None)
        self.sub_topic = mqtt_settings.get('topic') + "/#"
        self.pub_topic = mqtt_settings.get('topic')

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.callbacks = callbacks

        if self.user:
            self.client.username_pw_set(self.user, self.password)

        self.client.connect(self.server, self.port, 60)

    def on_connect(self, client, userdata, flags, rc):
        print ("Connected to mqtt server")

        client.subscribe(self.sub_topic)

    def on_message(self, client, userdata, msg):
        print (msg.topic+" | "+str(msg.payload))
        if self.callbacks:
            for keyword, callback_func in self.callbacks.items():
                if keyword in msg.topic:
                    callback_func(msg.topic, msg.payload)

    def publish(self, topic, message):
        topic = "/".join((self.pub_topic, topic))
        self.client.publish(topic, payload=message, qos=0, retain=True)

    def loop(self):
        self.client.loop(timeout=0.5)


class SonosManager(object):
    def __init__(self, devices):
        self.devices = devices
        self.device_lookup = dict()
        for dev in devices:
            self.device_lookup[dev.player_name.lower()] = dev

    def control_callback(self, topic, payload):
        playername = topic.rstrip('/control').split('/')[-1]
        device = self.device_lookup.get(playername, None)
        if device:
            if 'pause' in payload:
                device.pause()
            elif 'stop' in payload:
                device.stop()
            elif 'play' in payload:
                device.play()
            elif 'next' in payload or 'skip' in payload:
                device.next()
            elif 'previous' in payload:
                device.previous()


if __name__ == '__main__':
    settings = yaml.load(file(os.path.join('sonosmqtt', 'config_default.yaml'), 'r'))
    settings.update(yaml.load(file(os.path.join('sonosmqtt', 'config_user.yaml'), 'r')))

    devices = soco.discover()

    sonos_devs = dict()
    for dev in devices:
        ct = dev.get_current_track_info()
        state = dev.get_current_transport_info().get('current_transport_state')
        sonos_devs[dev] = (ct.get('uri', None), "UNDEFINED")

    Sonos = SonosManager(devices)
    callbacks = {'control':Sonos.control_callback}
    MQ = MQTT_Client(settings.get('mqtt'), callbacks)


    while True:
        # get current playing tracks from sonos
        for dev, (last_track_uri, last_state) in sonos_devs.items():
            ct = dev.get_current_track_info()
            tp = dev.get_current_transport_info()
            curr_state = tp.get('current_transport_state')
            curr_uri = ct.get('uri', None)

            if curr_uri != last_track_uri or curr_state != last_state:
                #print("{} : {} - {} ({})".format(dev.player_name, ct.get('artist'), 
                    #ct.get('title'), ct.get('duration')))
                sonos_devs[dev] = (curr_uri, curr_state)
                play_info = {
                    'artist':ct.get('artist'),
                    'title':ct.get('title'),
                    'duration':ct.get('duration'),
                    'status':curr_state,
                    }
                MQ.publish(dev.player_name.lower() + "/now_playing",
                        json.dumps(play_info))

        # push to mqtt
        MQ.loop()
