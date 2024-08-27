import pandas as pd
import os
import numpy as np

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

# Load paths from config file
paths = read_paths_from_config()
time_info_path = paths['time_info_path']
directory_path = os.path.join(paths['directory_base_path'], paths['selected_case'])
volume_path = os.path.join(paths['volume_base_path'], f"{paths['selected_case']}_interpolated.csv")

# Print the path for debugging
print(f"Looking for volume file at: {volume_path}")

# Dictionary mapping CSV files to their corresponding multipliers
csv_files = {
    'ventricle-average-velocity-inlet_interpolated.csv': 100,  # Convert m/s to cm/s
    'ventricle-average-velocity-outlet_interpolated.csv': 100,  # Convert m/s to cm/s
    'ventricle-average-kinetic-energy_interpolated.csv': 1000,  # Convert J to mJ
    'ventricle-average-turbulent-kinetic-energy_interpolated.csv': 1000,  #  Convert J/kg to mJ/kg
    'ventricle-average-wss_interpolated.csv': 1,  # Pascal
    'ventricle-energy-loss_interpolated.csv': 1,  # Convert later to mWatt
}

# Load time information data
time_info_df = pd.read_csv(time_info_path)

# Initialize lists to store results
results = []

# Process each CSV file
for csv_file_name, multiplier in csv_files.items():
    csv_file = os.path.join(directory_path, csv_file_name)

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

    if 'energy-loss' in csv_file_name:
        # Adjust the multiplier for the energy loss calculation
        multiplier = 1000 / timestep_size  # Convert energy loss to power (mW)

    if 'kinetic-energy' in csv_file_name and 'turbulent' not in csv_file_name:
        # Load the corresponding interpolated volume data for the case
        volume_df = pd.read_csv(volume_path)

        # Ensure the expected columns are present in the volume data
        if 'Interpolated Volumes' not in volume_df.columns:
            raise ValueError(f"Expected column 'Interpolated Volumes' not found in {volume_path}")

        # Convert volumes from mL (cm³) to m³ by dividing by 1,000,000 (1e6)
        volumes_in_m3 = volume_df['Interpolated Volumes'] / 1e6

        # Calculate kinetic energy as dynamic pressure * volume
        df['Kinetic Energy'] = df['Interpolated Data'] * volumes_in_m3

        # Use 'Kinetic Energy' for further calculations
        data_column = 'Kinetic Energy'
    else:
        # For turbulent kinetic energy and other metrics, use 'Interpolated Data' directly
        data_column = 'Interpolated Data'

    # Separate the data into diastolic and systolic based on timing information
    diastolic_data = df[(df['Flow Time'] >= 0) & (df['Flow Time'] <= END_DIASTOLE_TIME)][data_column]
    systolic_data = df[(df['Flow Time'] > END_DIASTOLE_TIME) & (df['Flow Time'] <= END_DIASTOLE_TIME + END_SYSTOLE_TIME)][data_column]

    # Perform calculations for diastolic phase
    diastolic_mean = np.round(diastolic_data.mean() * multiplier, 2)
    diastolic_std = np.round(diastolic_data.std() * multiplier, 2)

    # Perform calculations for systolic phase
    systolic_mean = np.round(systolic_data.mean() * multiplier, 2)
    systolic_std = np.round(systolic_data.std() * multiplier, 2)

    # Append the results for the current file to the list
    results.append({
        'File': csv_file_name,
        'Phase': 'Diastolic',
        'Mean ± Std': f"{diastolic_mean} ± {diastolic_std}"
    })
    results.append({
        'File': csv_file_name,
        'Phase': 'Systolic',
        'Mean ± Std': f"{systolic_mean} ± {systolic_std}"
    })

# Create a pandas DataFrame to display the results
results_df = pd.DataFrame(results)

# Output the pandas table
print(results_df.to_string(index=False))