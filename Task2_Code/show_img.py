import cv2
import os
import time

def show_image_with_opencv(file_path):
    try:
        img = cv2.imread(file_path)
        cv2.imshow("Image Viewer", img)
        cv2.waitKey(1000)  # Adjust the waitKey duration (in milliseconds) as needed
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error opening image with OpenCV: {e}")

if __name__ == '__main__':
   

    # Open each file with OpenCV and create an animation
    output_directory = "output_frames"
    for i in range(1, 51):  # Assuming you have 50 frames
        file_path = os.path.join(output_directory, f"{i}.png")
        show_image_with_opencv(file_path)
