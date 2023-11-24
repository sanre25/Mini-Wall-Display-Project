
# General libraries
import numpy as np
import os
import time

# Libraries for vizualization
import vtk 
import cv2
from vtkmodules.vtkCommonCore import vtkLookupTable, vtkDoubleArray
from vtkmodules.vtkCommonDataModel import vtkImageData
from vtkmodules.vtkRenderingCore import vtkActor, vtkDataSetMapper, vtkRenderWindow, vtkRenderer
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOImage import vtkPNGWriter  


# Variables 
MAX_TIMESTAMP = 100
NX = 64
NY = 64
DT = 60.0  
DX = 1000.0  
U0 = 10.0  
V0 = 5.0  
KX = 0.00001  
KY = 0.00001  

# Randomly Initialise field 
def initialize_field():
    np.random.seed(42)
    field = np.random.randint(0, 100, (NX, NY))
    return field

def updateField(field):
    temp_field = np.copy(field)

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

    field = temp_field
    return field

## Function for save rendered VTK window as image
def save_rendered_window(render_window, file_name):
    window_to_image_filter = vtk.vtkWindowToImageFilter()
    window_to_image_filter.SetInput(render_window)
    window_to_image_filter.Update()

    writer = vtkPNGWriter()
    writer.SetFileName(file_name)
    writer.SetInputConnection(window_to_image_filter.GetOutputPort())
    writer.Write()

## Function for split saved images in output_folder
def split_image(image_path, output_folder):
    image = cv2.imread(image_path)
    height, width, _ = image.shape
    center_x, center_y = width // 2, height // 2
    top_left = image[0:center_y, 0:center_x]
    top_right = image[0:center_y, center_x:]
    bottom_left = image[center_y:, 0:center_x]
    bottom_right = image[center_y:, center_x:]

    top_left_folder = os.path.join(output_folder, 'top_left')
    top_right_folder = os.path.join(output_folder, 'top_right')
    bottom_left_folder = os.path.join(output_folder, 'bottom_left')
    bottom_right_folder = os.path.join(output_folder, 'bottom_right')

    os.makedirs(top_left_folder, exist_ok=True)
    os.makedirs(top_right_folder, exist_ok=True)
    os.makedirs(bottom_left_folder, exist_ok=True)
    os.makedirs(bottom_right_folder, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(image_path))[0]
    cv2.imwrite(os.path.join(top_left_folder, f'{base_name}.png'), top_left)
    cv2.imwrite(os.path.join(top_right_folder, f'{base_name}.png'), top_right)
    cv2.imwrite(os.path.join(bottom_left_folder, f'{base_name}.png'), bottom_left)
    cv2.imwrite(os.path.join(bottom_right_folder, f'{base_name}.png'), bottom_right)

    print(f"Image split and saved successfully: {base_name}")

def main():
    data = initialize_field()
    side = data.shape[0]
    
    ## Setting VTK window 
    colors = vtkNamedColors()
    grid = vtkImageData()
    grid.SetDimensions(side, side, 1)

    array = vtkDoubleArray()
    array.SetNumberOfComponents(1)
    array.SetNumberOfTuples(grid.GetNumberOfPoints())

    for i in range(grid.GetNumberOfPoints()):
        array.SetValue(i, data[i//side][i%side])

    grid.GetPointData().SetScalars(array)

    lut = vtkLookupTable()
    mapper = vtkDataSetMapper()
    mapper.SetLookupTable(lut)
    mapper.SetInputData(grid)
    mapper.SetScalarRange(0, 128)
    mapper.SetColorModeToMapScalars()

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.SetPosition(-side//2, -side//2, 0)

    lut.SetNumberOfColors(256)
    lut.SetHueRange(0.0, 1)
    lut.Build()

    renderer = vtkRenderer()
    render_window = vtkRenderWindow()
    render_window.SetSize(1600, 900)
    render_window.AddRenderer(renderer)
    render_window.SetWindowName('RectilinearGrid')

    renderer.AddActor(actor)
    renderer.SetBackground(colors.GetColor3d('SlateGray'))
    renderer.GetActiveCamera().SetPosition(0, 0, 1.8*side)


    ## Each frame corresponding to the each 
    ## timestamp will be saved in "output_frames" folder
    output_directory = "output_frames"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    st_1 = time.time()
    for i in range(1, MAX_TIMESTAMP+1):  
        data = updateField(data)
        for j in range(grid.GetNumberOfPoints()):
            array.SetValue(j, data[j//side][j%side])
        grid.GetPointData().SetScalars(array)

        grid.Modified()

        render_window.Render()

        file_name = os.path.join(output_directory, f"{i}.png")
        save_rendered_window(render_window, file_name)
    et_1 = time.time()
        #time.sleep(0.05)

    # Split the saved images
    input_folder = 'output_frames'
    image_files = [f for f in os.listdir(input_folder) if f.endswith('.png')]

    st_2 = time.time()
    for image_file in image_files:
        image_path = os.path.join(input_folder, image_file)
        split_image(image_path, 'output_parts')
    et_2 = time.time()
    print(f'Time taken for split: {"{:.5f}".format(et_2 - st_2)}seconds')
    print(f'Time taken for update: {"{:.5f}".format(et_1 - st_1)}seconds')
	
if __name__ == '__main__':
    main()
