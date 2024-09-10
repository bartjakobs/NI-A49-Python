import hid
import struct


class Device: 

	"""
	Device class for the Native Instruments Komplete Kontrol A49 Keyboard.
	Parameters:
		vendor_id: int
			The vendor ID of the device. Default is 6092.
		product_id: int
			The product ID of the device. Default is 5952.
	
	Attributes:
		rotary_value: int
			The last read value of the rotary encoder.
		transpose_value: int
			The last read value of the transpose buttons.
	
	Methods:
		poll_keys()
			Polls the device for key presses and updates the key states.
		send(data)
			Sends data to the device.
		set_key_light(key, state, send = True)
			Sets the state of a key light, by key name.
			Set send to False to prevent sending the key light state to the device.
		set_key_by_index(index, state, send = True)
			Sets the state of a key light by index.
			Set send to False to prevent sending the key light state to the device.
		set_all_keys(state, send = True)
			Sets the state of all key lights.
			Set send to False to prevent sending the key light states to the device.
		send_key_lights()
			Sends the key light states to the device.
		send_image(im)
			Sends an image to the device.
			im: PIL.Image, 1 bits, 128x32 pixels
	"""
	
	Keys = ["SHIFT", "SCALE", "ARP", "UNDO", "QUANTIZE", "IDEAS", "LOOP", "METRO", "TEMPO", "PLAY", "REC", "STOP", "PRESET_UP", "PRESET_DOWN", "M", "S", "BROWSER", "PLUGIN_MIDI", "TRACK", "OCTAVE_DOWN", "OCTAVE_UP", "JOYSTICK_UP", "JOYSTICK_LEFT", "JOYSTICK_RIGHT", "JOYSTICK_DOWN", "JOYSTICK_PRESS"]

	rotary_value = 0
	transpose_value = 0
	

	def __init__(self, vendor_id = 6092, product_id = 5952):
		self.key_light_states = {}
		self.key_states = {}
		for key in self.Keys:
			self.key_light_states[key] = 0
			self.key_states[key] = 0

		self.device = hid.Device(vendor_id, product_id)
		self.commands = {
			"image_first_row":  "e00000000080000200",
			"image_second_row": "e00000020080000200",
			"lights": "80"
		}

		self.on_key_press = None
		self.on_key_release = None
		self.on_rotary = None
		self.on_octave = None


	def poll_keys(self):
		data = self.device.read(30, 10)
		while len(data) != 0: 
			self._parse_incoming_data(data)
			data = self.device.read(30, 10)

	
	def _parse_incoming_data(self, data):
		u = struct.unpack("x" + ("B" * 29), data)
		for i in range(0, 64): 
			if i < 8:
				self._key_status_update(i, u[0] & (1 << i) != 0)
			elif i < 16:
				self._key_status_update(i, u[1] & (1 << (i - 8)) != 0)
			elif i < 24:
				self._key_status_update(i, u[2] & (1 << (i - 16)) != 0)
			elif i < 32:
				self._key_status_update(i, u[3] & (1 << (i - 24)) != 0)
			elif i < 40:
				self._key_status_update(i, u[4] & (1 << (i - 32)) != 0)

		transpose = u[-1]
		rotate_button = u[-2]
		self._transpose_rotate_update(transpose, rotate_button)

		
	def _transpose_rotate_update(self, transpose, rotate_button):
		if(self.rotary_value != rotate_button):
			self.rotary_value = rotate_button
			if self.on_rotary:
				self.on_rotary(rotate_button)
		if(self.transpose_value != transpose):
			self.transpose_value = transpose
			if self.on_octave:
				self.on_octave(transpose)

	def _key_status_update(self, key, state):
		if key >= len(self.Keys):
			if key == 33: 
				key = len(self.Keys) - 1
			else:
				return
		if state != self.key_states[self.Keys[key]]:
			self.key_states[self.Keys[key]] = state
			if state:
				if self.on_key_press:
					self.on_key_press(self.Keys[key])
			else:
				if self.on_key_release:
					self.on_key_release(self.Keys[key])

	
	def send(self, data): 
		data = bytearray.fromhex(data)
		data = bytes(data)
		self.device.write(data)
		
	def _send_image(self, row1, row2): 
		data = self.commands["image_first_row"] + row1
		self.send(data)
		
		data = self.commands["image_second_row"] + row2
		self.send(data)
		

	def set_key_light(self, key, state, send = True):
		self.key_light_states[key] = state
		if send:
			self.send_key_lights()


	def set_key_by_index(self, index, state, send = True):
		keys = list(self.key_light_states.keys())
		key = keys[index]
		self.set_key_light(key, state, send)

	def set_all_keys(self, state, send = True):
		keys = list(self.key_light_states.keys())
		for key in keys:
			self.key_light_states[key] = state
		if send:
			self.send_key_lights()

		
	def send_key_lights(self): 
		data = ""
		for key in self.key_light_states: 
			data_int = self.key_light_states[key]
			data_hex_str = format(data_int, 'x')
			if len(data_hex_str) == 1: 
				data_hex_str = "0" + data_hex_str
			data += data_hex_str
		self.send(self.commands["lights"] + data)


	def send_image(self, im): 
		bytes1 = []
		for x in range(128):
			i = 0
			for y in range(8):
				pixel = 0 if im.getpixel((x, y)) == 0 else 1
				i |= pixel << y
			bytes1.append(i)
		for x in range(128):
			i = 0
		
			for y in range(8):
				pixel = 0 if im.getpixel((x, y + 8)) == 0 else 1
				i |= pixel << y
			bytes1.append(i)
	
		bytes2 = []
		for x in range(128):
			i = 0
			for y in range(8):
				pixel = 0 if im.getpixel((x, y + 16)) == 0 else 1
				i |= pixel << y
			bytes2.append(i)

		for x in range(128):
			i = 0
			for y in range(8):
				pixel = 0 if im.getpixel((x, y+ 24)) == 0 else 1
				i |= pixel << y
			bytes2.append(i)

		part1 = ""
		part2 = ""

		for byte in bytes1:
			part1 += format(byte, '02x')
		for byte in bytes2:
			part2 += format(byte, '02x')

		
		
		self._send_image(part1, part2)

