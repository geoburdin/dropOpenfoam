from paraview.simple import OpenFOAMReader, ProbeLocation, Show, Render, UpdatePipeline
from vtk.util.numpy_support import vtk_to_numpy
import numpy as np
import matplotlib.pyplot as plt
from paraview import servermanager

# 1. Load the OpenFOAM case
# Make sure the file 'waterDrop.foam' (or your case file) exists in the current directory.
reader = OpenFOAMReader(FileName="water/waterDrop.foam")
reader.MeshRegions = ['internalMesh']
reader.CellArrays = ['alpha.water', 'p', 'U']

Show(reader)
Render()
UpdatePipeline()

# 2. Create a ProbeLocation filter to sample the field at a specific point
probe = ProbeLocation(Input=reader)
# Note: ProbePoints must be a list of points (each point is a list of coordinates).
# Adjust these coordinates to a location on (or near) the free surface.
probe.ProbePoints = [[50, 5, 0.05]]
UpdatePipeline()

# 3. Fetch the data from the probe (should be returned as a vtkTable)
tableData = servermanager.Fetch(probe)

# 4. Attempt to extract the time series data from the vtkTable
try:
    colNames = tableData.GetColumnNames()
    print("Available columns:", colNames)
    # Expect columns like "Time" and "alpha.water"
    timeArr = vtk_to_numpy(tableData.GetColumnByName("Time"))
    alphaArr = vtk_to_numpy(tableData.GetColumnByName("alpha.water"))
except Exception as e:
    print("Error retrieving columns:", e)
    timeArr = None
    alphaArr = None

if timeArr is not None and alphaArr is not None:
    # 5. Plot the time series (oscillation at the probe point)
    plt.figure()
    plt.plot(timeArr, alphaArr, label="alpha.water")
    plt.xlabel("Time [s]")
    plt.ylabel("alpha.water")
    plt.title("Time Series at Probe Point")
    plt.legend()
    plt.show()

    # 6. Compute the FFT of the time series
    fftResult = np.fft.fft(alphaArr)
    # Calculate frequency bins; time resolution from difference between consecutive time values
    freq = np.fft.fftfreq(len(alphaArr), d=(timeArr[1]-timeArr[0]))
    pos_mask = freq >= 0  # Consider only positive frequencies

    plt.figure()
    plt.plot(freq[pos_mask], np.abs(fftResult[pos_mask]))
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Amplitude")
    plt.title("FFT of Probe Signal")
    plt.show()
else:
    print("Time series data not available from ProbeLocation.")
