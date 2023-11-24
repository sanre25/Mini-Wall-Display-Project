import time
import socket
import threading
import os
import numpy as np

MAX_TIMESTEPS = 100

# code for sending the data
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
BUFFER_SIZE = 2048
FORMAT = 'utf-8'

CLIENTS = 4

SEPARATOR = ' '

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# This function sends the files
def send_file(conn, addr, client_index, time_index, file_name):
    # Generate name of file based on time index
    file_size = os.path.getsize(file_name)
    file_size = file_size.to_bytes(8, byteorder = "big")
    conn.send(file_size)
    with open(file_name, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in 
            # busy networks
            conn.sendall(bytes_read)   

    print(f"{time_index} file sent to {client_index} client") 

def start():
    print("[SERVER] is starting...")
    server.listen()

    clients = dict()
    threads = list()
    client_index = 0
    time_index = 1
    while client_index != CLIENTS:
        conn, addr = server.accept()
        index = conn.recv(4)  # Use 4 bytes for index
        index = int.from_bytes(index, byteorder='big')
        print(index)

        clients[index] = (conn, addr)
        client_index += 1
    input('Press any key to continue...')
    
    st = time.time()
    # Setting up different threads for the clients
    while time_index != MAX_TIMESTEPS+1:
        for i in range(1, CLIENTS+1):
            conn = clients[i][0]
            addr = clients[i][1]
            file_name = "./output_parts/"
            if i == 1:
                file_name += f'top_left/{time_index}.png'
            elif i == 2:
                file_name += f'top_right/{time_index}.png'
            elif i == 3:
                file_name += f'bottom_left/{time_index}.png'
            else:
                file_name += f'bottom_right/{time_index}.png'
            thread = threading.Thread(target=send_file, args=(conn, addr, client_index, time_index, file_name))
            thread.start()
            threads.append(thread)
        time.sleep(0.5)
        for thread in threads:
            thread.join()
        time_index += 1
    et = time.time()
    print(f'Time taken for split: {"{:.5f}".format(et - st)}seconds')
print(ADDR)
start()
server.close()