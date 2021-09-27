import io
import socket
import struct
from PIL import Image
import time

cs = socket.socket()
cs.connect(('192.168.10.1', 5001))
print('Connected to RPi!')
connection = cs.makefile('rb')

count = 0
try:
    img = None
    while True:
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            continue
        print("write scan" + "\n")
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        image_stream.seek(0)
            
        image = Image.open(image_stream)
        image.save('../fromrpi.jpg')
        print('Image resolution is %d x %d' % image.size)
        image.verify()
        print('Verified!')
        cs.sendall('Picture'.encode())
finally:
    connection.close()
    cs.close()