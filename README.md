# OCT-data
Simple processing of OCT images (a cross-section of the sample) to retrieve the attenuation coefficients from the corresponding A-scans.
This Python script is an open source alternative of MATLAB or OriginPro functions used in OCT analysis.

This Python script is a graphical user interface (GUI) application used for viewing and analyzing Optical Coherence Tomography (OCT) images. It provides functionality to load OCT data, display the average image and its corresponding A-scan, define Regions of Interest (ROIs), calculate the linear fit within each ROI, and remove the ROIs.

# Features
- Load OCT data from a file
- Display OCT images
- Visualize the average image and its corresponding A-scan
- Define Regions of Interest (ROI) on the A-scan
- Calculate the linear fit within each ROI
- Remove the defined ROIs
- Display a table of calculated measurements

# Required Libraries
- Python (version 3.x recommended)
- NumPy
- Matplotlib
- Tkinter
- re

# Usage
To run the script, use the following command:
`python oct_analysis.py`

When the GUI starts, you can interact with it as follows:

1. Click the Open button to load an OCT data .dat file (example is in OCT data folder).
2. The program will display the OCT image and its corresponding A-scan (depth profile).
3. Click the Choose ROI button and then click on two points on the A-scan plot to define the ROI.
4. The program will calculate a linear fit within the defined ROI, display it on the A-scan plot, and add the slope to a table of measurements.
5. Click the Remove ROI button to remove the last defined ROI and update the table of measurements.
6. The slope value of the liner fit of the A-scan gives a physical value of the attenuation coefficient of the sample.

# Notes
This script expects the OCT data to be stored in a binary file of 64-bit floating point numbers.
The script assumes that the dimensions of the data (X, Y, Z) are included in the file name in the format 'X# Y# Z#', where # is the dimension size.
The size of the ROI is determined by the two points that you click on the A-scan plot after clicking the Choose ROI button.
The program uses a simple linear fit (y = mx + b) to calculate the slope within each ROI.
The table of measurements shows the slope for each defined ROI, and the average slope ± standard deviation for all defined ROIs.

# Disclaimer
This script is provided as-is, and the accuracy and completeness of the calculations are not guaranteed. Always verify the results independently.
