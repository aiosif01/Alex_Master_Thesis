import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

# Function to read paths from config.txt
def read_paths_from_config():
    config_file = os.path.join(os.path.dirname(__file__), 'config.txt')
    paths = {}
    with open(config_file, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or '=' not in line or line.startswith('#'):
                continue  # Skip empty lines, lines without '=', or comment lines
            key, value = line.split('=', 1)
            paths[key.strip()] = value.strip()
    return paths

# Function to normalize data based on the specified method
def normalize_data(data, method='max', ed_volume=None, es_volume=None, stroke_volume=None):
    """
    Normalizes data based on the specified method.
    
    Parameters:
    - data: The data to normalize.
    - method: The normalization method ('max', 'EDVolume', 'ESVolume', 'StrokeVolume', 'None').
    - ed_volume: End-Diastolic Volume in cubic meters (m³).
    - es_volume: End-Systolic Volume in cubic meters (m³).
    - stroke_volume: Stroke Volume in milliliters (mL).

    Returns:
    - Normalized data.
    """
    if method == 'max':
        return data / data.max()
    elif method == 'EDVolume' and ed_volume is not None:
        return data / ed_volume
    elif method == 'ESVolume' and es_volume is not None:
        return data / es_volume
    elif method == 'StrokeVolume' and stroke_volume is not None:
        return data / stroke_volume
    elif method == 'None':
        return data  # No normalization applied
    else:
        raise ValueError("Invalid normalization method or missing volume data.")

# Load paths from config file
paths = read_paths_from_config()
time_info_path = paths['time_info_path']
directory_path = os.path.join(paths['directory_base_path'], paths['selected_case'])
volume_path = os.path.join(paths['volume_base_path'], f"{paths['selected_case']}_interpolated.csv")

# Print the path for debugging
print(f"Looking for volume file at: {volume_path}")

# Dictionary mapping CSV files to their corresponding multipliers and normalization method
csv_files = {
    'ventricle-average-kinetic-energy_interpolated.csv': {'multiplier': 1, 'normalize': 'StrokeVolume'},  # Convert J to mJ later
    'ventricle-energy-loss_interpolated.csv': {'multiplier': 1, 'normalize': 'StrokeVolume'},  # Convert J to mW later
}

# Load time information data
time_info_df = pd.read_csv(time_info_path)

# Initialize lists to store results
results = []
plot_data = {}  # Dictionary to store plot data for EL and KE

# Load the corresponding interpolated volume data for the case
volume_df = pd.read_csv(volume_path)

# Ensure the expected columns are present in the volume data
if 'Interpolated Volumes' not in volume_df.columns:
    raise ValueError(f"Expected column 'Interpolated Volumes' not found in {volume_path}")

# Calculate EDV and ESV from interpolated volumes
EDVolume_ml = volume_df['Interpolated Volumes'].max()  # EDV as the maximum volume in mL
ESVolume_ml = volume_df['Interpolated Volumes'].min()  # ESV as the minimum volume in mL

# Calculate Stroke Volume (SV) in mL
StrokeVolume_ml = EDVolume_ml - ESVolume_ml

# Process each CSV file
for csv_file_name, options in csv_files.items():
    csv_file = os.path.join(directory_path, csv_file_name)
    multiplier = options['multiplier']
    normalization_method = options['normalize']

    # Check if the file exists
    if not os.path.exists(csv_file):
        raise ValueError(f"File {csv_file_name} not found in directory {directory_path}")

    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Get corresponding timestep size and other timing information from time_information.csv
    case_name = os.path.basename(directory_path)
    time_info_row = time_info_df[time_info_df['case'] == case_name]

    if time_info_row.empty:
        raise ValueError(f"Case {case_name} not found in time_information.csv")

    # Extract relevant timing information
    RR_DURATION = time_info_row['RR_DURATION'].values[0]
    END_DIASTOLE_TIME = time_info_row['END_DIASTOLE_TIME'].values[0]
    END_SYSTOLE_TIME = time_info_row['END_SYSTOLE_TIME'].values[0]
    total_timesteps = time_info_row['TIMESTEPS'].values[0]
    timestep_size = RR_DURATION / total_timesteps

    # Normalize time data for plotting
    df['Normalized Time'] = df['Flow Time'] / RR_DURATION

    # Conversion for energy loss data
    if 'energy-loss' in csv_file_name:
        # Convert energy loss from J to W
        power_W = df['Interpolated Data'] / timestep_size

        # Convert power to mW
        power_mW = power_W * 1000

        # Normalize by Stroke Volume in mL to get mW/mL
        power_mW_per_ml = power_mW / StrokeVolume_ml

        # Convert to W/m³
        power_W_per_m3 = power_mW_per_ml * 1000

        df['Converted Data'] = power_W_per_m3
        plot_data['EL'] = (df['Normalized Time'], power_mW)

    # Conversion for kinetic energy data
    elif 'kinetic-energy' in csv_file_name:
        # Convert interpolated volumes to m³ before using them for conversion
        volumes_in_m3 = volume_df['Interpolated Volumes'] / 1e6
        # Calculate kinetic energy as dynamic pressure * volume [Joules]
        KE_J = df['Interpolated Data'] * volumes_in_m3

        # Convert KE to mJ
        KE_mJ = KE_J * 1000

        # Normalize by Stroke Volume in mL to get mJ/mL
        KE_mJ_per_ml = KE_mJ / StrokeVolume_ml

        # Convert to J/m³
        KE_J_per_m3 = KE_mJ_per_ml * 1000

        df['Converted Data'] = KE_J_per_m3
        # plot_data['KE'] = (df['Normalized Time'], KE_mJ)

    else:
        # For other data types, use 'Interpolated Data' directly
        df['Converted Data'] = df['Interpolated Data']

    # Separate the converted data into diastolic and systolic based on timing information
    diastolic_data = df[(df['Flow Time'] >= 0) & (df['Flow Time'] <= END_DIASTOLE_TIME)]['Converted Data']
    systolic_data = df[(df['Flow Time'] > END_DIASTOLE_TIME) & (df['Flow Time'] <= END_DIASTOLE_TIME + END_SYSTOLE_TIME)]['Converted Data']

    # Normalize diastolic and systolic data if normalization is enabled
    if normalization_method != 'None':
        diastolic_data = normalize_data(diastolic_data, method=normalization_method, stroke_volume=StrokeVolume_ml)
        systolic_data = normalize_data(systolic_data, method=normalization_method, stroke_volume=StrokeVolume_ml)

    # Compute mean and standard deviation for normalized or non-normalized data
    diastolic_mean = np.round(diastolic_data.mean(), 2)
    diastolic_std = np.round(diastolic_data.std(), 2)
    systolic_mean = np.round(systolic_data.mean(), 2)
    systolic_std = np.round(systolic_data.std(), 2)

    # Append the results for the current file to the list
    results.append({
        'File': csv_file_name,
        'Phase': 'Diastolic',
        'Mean ± Std (W/m³ or J/m³)': f"{diastolic_mean} ± {diastolic_std}"
    })
    results.append({
        'File': csv_file_name,
        'Phase': 'Systolic',
        'Mean ± Std (W/m³ or J/m³)': f"{systolic_mean} ± {systolic_std}"
    })

# Create a pandas DataFrame to display the results
results_df = pd.DataFrame(results)

# Output the pandas table
print(results_df.to_string(index=False))

# # Plotting KE and EL over Normalized Time
# fig, ax1 = plt.subplots()

# # Plot EL on the left y-axis
# ax1.set_xlabel('Normalized Time', fontsize=14, fontweight='bold')
# ax1.set_ylabel('EL (mW)', color='tab:blue', fontsize=14, fontweight='bold')
# ax1.plot(plot_data['EL'][0], plot_data['EL'][1], color='tab:blue', label='Energy Loss (EL)')
# ax1.tick_params(axis='y', labelcolor='tab:blue', labelsize=12)
# ax1.tick_params(axis='x', labelsize=12)

# # Create a second y-axis for KE
# ax2 = ax1.twinx()
# ax2.set_ylabel('KE (mJ)', color='tab:red', fontsize=14, fontweight='bold')
# ax2.plot(plot_data['KE'][0], plot_data['KE'][1], color='tab:red', label='Kinetic Energy (KE)')
# ax2.tick_params(axis='y', labelcolor='tab:red', labelsize=12)

# # Add a title and grid
# plt.title('KE and EL over Normalized Time', fontsize=16, fontweight='bold')
# fig.tight_layout()  # Adjust layout

# # Show the plot
# plt.show()
