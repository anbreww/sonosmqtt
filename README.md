# Sonos to MQTT bridge

Reads currently playing track on Sonos system and posts to relevant 
topic on MQTT

Will allow monitoring of specific topics for play/pause/skip actions

The aim is to provide a super simple bridge to allow ESP8266 based modules
to control the music in the house and display some "now playing" information
on little LCD screens

## WARNING : VERY MUCH INCOMPLETE

This is still mostly a proof of concept, some of the settings don't work,
a lot of things haven't been tested yet, and I haven't taken any time to
write tests or even comment the code (yargh).


## Getting started

    cp sonosmqtt/config_{default,user}.yaml

then edit the `config_user` file with your own settings.
For now, the program expects a username and password to connect to mqtt and
will probably fail without it. The sonos "hosts" list is not used, instead
it gets populated when the program launches.

Make sure all the speakers are powered up and connected to the network before
starting this program, since it only checks once for the players. In the future,
we will probably auto-detect when a player gets added or removed from the
network or renamed.

Volume control is also missing, it'll probably be added in the next commit.
