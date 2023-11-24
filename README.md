# Mini Wall Display Project

Our main objective in this proeject is to create display wall. For that we have two aprroachs.

1. We would be simulating the data using parallel processing using multiple processes on our server node and then the data would be divided into certain parts (4 to be specific) and each part would be transmitted to different client nodes for visualisation. Since the data would be processed with different time steps, the visualisation would be real-time in this method.
 
2. Construct images in the server node itself after data generation and instead of dividing and sending the data, we partition the image and send the images to different client nodes for visualisation.



The code and readme file for appraoch 1 can be found in `Task1_code` folder. For approach 2 relevent code can be found in `Task2_code` with readme file.
