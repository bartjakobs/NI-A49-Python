import NIA49Keyboard
from PIL import Image, ImageDraw
import time

running = True

def key_press(key):
	global running
	if key == "STOP":
		running = False

device = NIA49Keyboard.Device()
device.on_key_press = key_press
device.set_all_keys(0, False)
device.set_key_light("STOP", 0xff)	

x = 0
y = 0
vx = 1
vy = 1
while running:
	x += vx
	y += vy
	if x < 0 or x > (128 - 24):
		vx *= -1
	if y < 0 or y > (32 - 16):
		vy *= -1
	im = Image.new('1', (128, 32), (1))
	draw = ImageDraw.Draw(im)
	draw.text((x, y), "DVD", fill=0)
	# draw.ellipse((0, 0, 20, 20), fill=0)
	device.send_image(im)
	time.sleep(0.05)
	device.poll_keys()

# Clear the display and turn off all lights
device.send_image(Image.new('1', (128, 32), (1)))
device.set_all_keys(0)

