import os
import numpy as np
import matplotlib.pyplot as plt

def read_vector_field(filepath):
    """
    Reads OpenFOAM volVectorField data from the given file.
    """
    with open(filepath, 'r') as file:
        data = []
        is_data_section = False
        for line in file:
            line = line.strip()
            if line.startswith("internalField"):
                if "nonuniform" in line:
                    is_data_section = True
            elif is_data_section:
                if line.startswith("("):  # Start of data values
                    continue
                if line.startswith(")"):  # End of data section
                    break
                try:
                    # Read vector data (x, y, z)
                    values = line.strip("()").split()
                    if len(values) == 3:  # Ensure valid vector
                        vector = [float(values[0]), float(values[1]), float(values[2])]
                        data.append(vector)
                except (ValueError, IndexError):
                    continue
    return np.array(data)  # Ensure output is a 2D array

# Path to your OpenFOAM folder
folder_path = "soap/7.9/"  # Change this to the correct folder
u_file_path = os.path.join(folder_path, "U")

if os.path.exists(u_file_path):
    velocity_data = read_vector_field(u_file_path)  # Shape: (num_points, 3)

    # Choose a component for frequency analysis (e.g., x-component)
    u_x = velocity_data[:, 0]  # Extract x-component of the velocity

    # Perform Fourier Transform on the x-component
    fft_result = np.fft.fft(u_x)
    frequencies = np.fft.fftfreq(len(fft_result))

    # Plot the magnitude of the FFT
    plt.figure(figsize=(10, 6))
    plt.plot(frequencies[:len(frequencies)//2], np.abs(fft_result[:len(fft_result)//2]))
    plt.title("Frequency Spectrum of Velocity (U_x)")
    plt.xlabel("Frequency")
    plt.ylabel("Magnitude")
    plt.grid()
    plt.show()
else:
    print(f"File {u_file_path} not found.")
