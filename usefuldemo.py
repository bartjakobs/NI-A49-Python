import hid
import NIA49Keyboard
import time 
import math
from PIL import Image, ImageDraw
import subprocess


device = NIA49Keyboard.Device()

def key_press(key):
	if key == "PLAY":
		cmd = 'osascript -e "tell application \\"Spotify\\" to playpause"'
		subprocess.call(cmd, shell=True)
	if key == "STOP":
		cmd = 'osascript -e "tell application \\"Spotify\\" to pause"'
		subprocess.call(cmd, shell=True)
	
device.on_key_press = key_press


im = Image.new('1', (128, 32), (1))
draw = ImageDraw.Draw(im)
draw.text((0, 0 ), "Press Play / Stop", fill=0)
draw.text((0, 16 ), "to control Spotify!", fill=0)
# draw.ellipse((0, 0, 20, 20), fill=0)
device.send_image(im)
time.sleep(0.05)
device.poll_keys()



device.set_all_keys(0, False)
device.set_key_light("PLAY", 0xff)
device.set_key_light("STOP", 0xff)
while True:
	device.poll_keys()



# Inverse:

