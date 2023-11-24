# General libraries
import numpy as np
import os
import time

# Libraries for socket
import socket

# Definitions for socket
PORT = 5050
SERVER = "172.23.39.107"
ADDR = (SERVER, PORT)
BUFFER_SIZE = 2048
FORMAT = 'utf-8'

HEADER = 64
SEPARATOR = ' '

INDEX = 1
INDEX_MSG = INDEX.to_bytes(4, byteorder='big')

MAX_TIMESTEPS = 100

# Establishing a connection
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
client.send(INDEX_MSG)

def receive_file(output_directory, time_index):
    # receiving file name and file size
    file_size = client.recv(8)
    file_size = int.from_bytes(file_size)

    file_name = f"./{output_directory}/{time_index}.png"
    # convert to integer
    file_size = int(file_size)
    print(file_size)

    with open(file_name, "wb") as f:
        while file_size > 0:
            bytes_read = client.recv(min(BUFFER_SIZE, file_size))

            f.write(bytes_read)
            file_size -= len(bytes_read)


# Receiving the file and saving it
time_steps = MAX_TIMESTEPS
connected = True
output_directory = "output_frames_client"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

time_index = 1
while connected:
    receive_file(output_directory, time_index)
    time_index += 1
    if time_index == MAX_TIMESTEPS+1:
        break

client.close()
