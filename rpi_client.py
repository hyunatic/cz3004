import io
import socket
import struct
import time
import picamera

client_socket = socket.socket()
client_socket.connect(('192.168.10.14', 8000))
print('Connected...')
connection = client_socket.makefile('wb')

try:
    camera = picamera.PiCamera()
    #camera.vflip = True
    camera.rotation = 180
    camera.resolution = (640, 480)
    camera.start_preview()
    time.sleep(2)
    stream = io.BytesIO()
    
    count = 0
    for foo in camera.capture_continuous(stream, 'jpeg'):
        connection.write(struct.pack('<L', stream.tell()))
        connection.flush()
        stream.seek(0)
        connection.write(stream.read())
        if count == 0:
            count+=1
        else:
            print(client_socket.recv(1024).decode())
        if input("Press Enter to Send...") == '':
            stream.seek(0)
            stream.truncate()
        else:
            break
    connection.write(struct.pack('<L', 0))
    
finally:
    connection.close()
    client_socket.close()
