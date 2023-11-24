import time
import socket
import threading
import os
import numpy as np
import sys

################### Command line arguments ###################

# python  ./server_file_name.py   NX  NY  MAX_TIMESTEPS

# NX = Number of rows
# NY = Number of columns
# MAX_TIMESTEPS = The total timesteps for which simulation runs

###################  Initial variables  #####################


# Simulation variables
NX = 64
NY = 64
MAX_TIMESTEPS = 200
TIME_SLEEP = 0.2

DT = MAX_TIMESTEPS  # Time step in seconds
DX = 1000.0  # Spatial step in meters
U0 = 10.0  # Initial horizontal wind velocity (m/s)
V0 = 5.0  # Initial vertical wind velocity (m/s)
KX = 0.00001  # Diffusion coefficient for X-direction
KY = 0.00001  # Diffusion coefficient for Y-direction

# Server variables
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
BUFFER_SIZE = 2048
FORMAT = 'utf-8'

CLIENTS = 1

SEPARATOR = ' '



###################  Simulation code  #####################



def initialize_field():
    np.random.seed(42)  # Set a seed for reproducibility
    field = np.random.randint(0, 100, (NX, NY))
    return field

def updateField(field):
    temp_field = np.copy(field)  # Create a temporary field for the updated values

    for i in range(NX):
        for j in range(NY):
            i_prev = int((i - U0 * DT / DX + NX) % NX)
            j_prev = int((j - V0 * DT / DX + NY) % NY)
            temp_field[i, j] = field[i_prev, j_prev]

    for i in range(NX):
        for j in range(NY):
            laplacian = (field[(i + 1) % NX, j] + field[(i - 1 + NX) % NX, j]
                        + field[i, (j + 1) % NY] + field[i, (j - 1 + NY) % NY]
                        - 4 * field[i, j]) / (DX * DX)
            temp_field[i, j] += (KX * laplacian + KY * laplacian) * DT

    field = temp_field # Update the field with the new values for the next time step
    return field



###################  Server send code  #####################



# Fucntion for sending numpy data array to the client
def sendData(conn, addr, client_index, time_index, data_array):

    # reshaping the data_array to a 1D array
    data_array = data_array.reshape((1, (NX//2)*(NY//2)))

    # calculating and sending size of the data_array
    array_size = (data_array.itemsize * data_array.size)
    size = array_size.to_bytes(4, byteorder = "big")
    conn.send(size)

    # sending the array
    data = data_array.tobytes()
    conn.send(data)

    print(f"{time_index+1} data sent to {client_index} client")

# Function to handle the clients
def start(server):
    print("[SERVER] is starting...")
    server.listen()

    # storing the simulation constants in constants array
    constants = np.array((NX, NY, MAX_TIMESTEPS), dtype = np.int32)
    constants_size = constants.itemsize * constants.size
    constants_size = constants_size.to_bytes(4, byteorder = "big")
    constants_data = constants.tobytes()

    # since we need to send the data to client based on
    # the position in the display, we store the connections
    # to clients in a dictionary using index as a key
    clients = dict()
    threads = list()
    client_index = 0
    time_index = 0
    while client_index != CLIENTS:
        conn, addr = server.accept()

        # receiving the index from all the clients
        index = conn.recv(4)
        index = int.from_bytes(index, byteorder='big')
        print(f'Client {index} connected')
        clients[index] = (conn, addr)
        client_index += 1

        # sending NX, NY and time steps to clients
        conn.send(constants_size)
        conn.send(constants_data)

    input('Press any key to continue...')
    
    # Initializing the data
    data = initialize_field()
    update_time = 0

    st = time.time()
    
    # Setting up different threads for the clients
    while time_index != MAX_TIMESTEPS:

        # we loop through all the clients
        for i in range(1, CLIENTS+1):
            conn = clients[i][0]
            addr = clients[i][1]

            # dividing the data according to the index
            client_data = np.zeros((NX // 2, NY // 2))
            if i == 1:
                client_data = data[0:NX//2, 0:NY//2]
            elif i == 2:
                client_data = data[0:NX//2, NY//2:NY]
            elif i == 3:
                client_data = data[NX//2:NX, 0:NY//2]
            else:
                client_data = data[NX//2:NX, NY//2:NY]

            # we create a new thread to send data for one timestep to a single client
            thread = threading.Thread(target=sendData, args=(conn, addr, i, time_index, client_data))
            thread.start()
            threads.append(thread)

        # this ensures we proceed after all threads are terminated
        for thread in threads:
            thread.join()

        update_time_s = time.time()
        data = updateField(data)
        update_time_e = time.time()

        # calculating time taken to update the array
        update_time += (update_time_e - update_time_s)

        # the simulation waits before sending the next data array
        time.sleep(TIME_SLEEP)
        time_index += 1
    
    et = time.time()
    print(f'Time taken: {"{:.5f}".format(et - st)} seconds')
    print(f'Time taken for updates: {"{:.5f}".format(update_time)} seconds')
    print(f'Time taken for sending: {"{:.5f}".format(et - st - update_time)} seconds')

# Taking initial arguments from terminal
args = sys.argv
NX = int(args[1])
NY = int(args[2])
MAX_TIMESTEPS = int(args[3])

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
print(ADDR)
start(server)
server.close()