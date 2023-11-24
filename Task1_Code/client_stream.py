# General libraries
import numpy as np
import time

# Libraries for socket
import socket

# Libraries for vizualization
import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkCommonCore import vtkDoubleArray
from vtkmodules.vtkCommonDataModel import vtkRectilinearGrid
from vtkmodules.vtkCommonDataModel import vtkImageData
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)



###################  Initial variables  #####################



# Definition for simulation
NX = 0
NY = 0
MAX_TIMESTEPS = 0

# Definitions for socket
PORT = 5050
SERVER = "172.23.39.107"
ADDR = (SERVER, PORT)
BUFFER_SIZE = 2048
FORMAT = 'utf-8'

SEPARATOR = ' '

INDEX = 3
INDEX_MSG = INDEX.to_bytes(4, byteorder='big')



###################  Client receive code  #####################


# Function to receive data
def receiveData():
    # receiving array size
    array_size_bytes = client.recv(4)
    array_size = int.from_bytes(array_size_bytes, byteorder="big")

    # Receiving array data in a loop until the entire array is received
    received_data = bytearray()
    while len(received_data) < array_size:
        remaining_size = array_size - len(received_data)
        remaining_data = client.recv(remaining_size)
        received_data.extend(remaining_data)

    # Convert the received data to a NumPy array
    array_data = np.frombuffer(received_data, dtype=np.int32)
    array_data = array_data.reshape((NX, NY))

    return array_data

# Establishing a connection
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
client.send(INDEX_MSG)

# Receiving constants NX, NY and MAX_TIMESTEPS
constants_size = client.recv(4)
constants_size = int.from_bytes(constants_size, byteorder="big")

# Receiving array data in a loop until the entire array is received
constants_data = bytearray()
while len(constants_data) < constants_size:
    remaining_size = constants_size - len(constants_data)
    remaining_data = client.recv(remaining_size)
    constants_data.extend(remaining_data)
# Convert the received data to a NumPy array
constants = np.frombuffer(constants_data, dtype=np.int32)

NX = constants[0] // 2
NY = constants[1] // 2
MAX_TIMESTEPS = constants[2]



###################  vtk visualization code  #####################



# Creating the initial window
# Numpy zeroes
data = np.zeros((NX, NY), np.int32)
colors = vtkNamedColors()

# Create a grid
grid = vtkImageData()
grid.SetDimensions(NX, NY, 1)

array = vtkDoubleArray()
array.SetNumberOfComponents(1) # this is 3 for a vector
array.SetNumberOfTuples(grid.GetNumberOfPoints())
# Update the loop to assign proper random scalar values
for i in range(grid.GetNumberOfPoints()):
    array.SetValue(i, data[i // NY][i % NY])  # Adjusting range to 0-255

grid.GetPointData().SetScalars(array)

# Create a mapper and actor
lut = vtkLookupTable()

mapper = vtkDataSetMapper()
mapper.SetLookupTable(lut)
mapper.SetInputData(grid)
mapper.SetScalarRange(0, 128)
mapper.SetColorModeToMapScalars()

actor = vtkActor()
actor.SetMapper(mapper)
actor.SetPosition(-NX // 2, -NY // 2, 0)

lut.SetNumberOfColors(256)
lut.SetHueRange(0.0, 1)
lut.Build()

# Visualize
renderer = vtkRenderer()
renderWindow = vtkRenderWindow()
renderWindow.SetSize(1600, 900)
renderWindow.AddRenderer(renderer)
renderWindow.SetWindowName('RectilinearGrid')

renderer.AddActor(actor)
renderer.SetBackground(colors.GetColor3d('SlateGray'))
renderer.GetActiveCamera().SetPosition(0, 0, 1.8 * NY)
renderWindow.Render()



###################  Loop for receving and updating the render  #####################



# Receiving the data and updating the window
time_steps = MAX_TIMESTEPS
connected = True

while connected:
    data = receiveData()
    if data.any() == None:
        break

    for i in range(grid.GetNumberOfPoints()):
        array.SetValue(i, data[i // NY][i % NY])
    grid.GetPointData().SetScalars(array)
    grid.Modified()

    renderWindow.Render()
    # time.sleep(0.5)

    time_steps -= 1
    if time_steps == 0:
        break

client.close()