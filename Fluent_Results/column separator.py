import pandas as pd
import os
import numpy as np

# Load time information from the CSV file
time_info_df = pd.read_csv('C:/Users/alexi/Desktop/GitHub/Alex_Master_Thesis/Fluent_Results/time_information.csv')

def get_time_info(case_name):
    case_row = time_info_df[time_info_df['case'] == case_name]
    if not case_row.empty:
        return case_row.iloc[0]['RR_DURATION'], case_row.iloc[0]['END_DIASTOLE_TIME'], case_row.iloc[0]['END_SYSTOLE_TIME']
    else:
        raise ValueError(f"Timing information for case '{case_name}' not found.")

# Manually select the case name and directory path
case_name = 'hypox01_post'  # Replace with the desired case name
directory_path = 'C:/Users/alexi/Desktop/GitHub/Alex_Master_Thesis/Fluent_Results/hypox01_post'  # Replace with the correct path

# Get the time information for the selected case
try:
    RR_DURATION, END_DIASTOLE_TIME, END_SYSTOLE_TIME = get_time_info(case_name)
    print(f"Case: {case_name}")
    print(f"End Diastolic Time: {END_DIASTOLE_TIME}")
    print(f"End Systolic Time: {END_SYSTOLE_TIME}")
except ValueError as e:
    print(e)
    exit()

# Manually select which .out files to work on
selected_files = [
    # 'velocity-plane-over-valves.out',
    # 'ventricle-average-kinetic-energy.out',
    # 'ventricle-average-pressure.out',
    # 'ventricle-average-turbulent-kinetic-energy.out',
    # 'ventricle-average-velocity-inlet.out',
    # 'ventricle-average-velocity-outlet.out',
    'ventricle-average-wss.out',
    'ventricle-energy-loss.out',
    'ventricle-volume.out'
]

# Process each selected .out file
for file_name in selected_files:
    file_path = os.path.join(directory_path, file_name)

    if os.path.exists(file_path):
        # Read the .out file, skipping the first two lines
        try:
            df = pd.read_csv(file_path, sep='\s+', skiprows=2, header=None)
        except pd.errors.ParserError as e:
            print(f"Error parsing {file_name}: {e}")
            continue

        # Ensure the file has enough columns
        if df.shape[1] < 3:
            print(f"File {file_name} does not have enough columns.")
            continue

        # Assuming the first column is time steps, second is variable of interest, and third is flow time
        time_steps = df.iloc[:, 0]
        variable_data = df.iloc[:, 2]
        flow_time = pd.to_numeric(df.iloc[:, 1], errors='coerce')  # Convert to numeric

        # Determine the number of steps in one cardiac cycle
        num_timesteps_per_cycle = len(time_steps) // 3

        # Indices for the first cycle
        first_cycle_flow_time = flow_time[:num_timesteps_per_cycle].reset_index(drop=True)

        # Determine the indices that match the end of diastolic and systolic phases
        diastolic_end_idx = np.searchsorted(first_cycle_flow_time, END_DIASTOLE_TIME)
        systolic_end_idx = np.searchsorted(first_cycle_flow_time, END_DIASTOLE_TIME + END_SYSTOLE_TIME)

        # Ensure we cover the exact range by including all matching indices
        if diastolic_end_idx < num_timesteps_per_cycle and first_cycle_flow_time.iloc[diastolic_end_idx] < END_DIASTOLE_TIME:
            diastolic_end_idx += 1
        if systolic_end_idx < num_timesteps_per_cycle and first_cycle_flow_time.iloc[systolic_end_idx] < END_DIASTOLE_TIME + END_SYSTOLE_TIME:
            systolic_end_idx += 1

        # Use the same indices to extract data from the third cycle onwards
        start_third_cycle = 2 * num_timesteps_per_cycle
        third_cycle_data = variable_data[start_third_cycle:].reset_index(drop=True)

        # Shift selections:
        # Exclude the first point from diastolic
        diastolic_data = third_cycle_data.iloc[1:diastolic_end_idx]  # Exclude the first data point
        # Include all remaining points in the systolic phase
        systolic_data = third_cycle_data.iloc[diastolic_end_idx:]

        # Prepare the output file path
        output_file_path = os.path.join(directory_path, f'{os.path.splitext(file_name)[0]}_output.csv')

        # Write the data to the output file in the required format
        with open(output_file_path, 'w') as f:
            # Write the total number of diastolic data in the first line
            f.write(f"Total Diastolic Data: {len(diastolic_data)}\n")
            # Write the diastolic data in the second row
            f.write(','.join(map(str, diastolic_data.tolist())) + '\n')
            # Write a blank line
            f.write('\n')
            # Write the total number of systolic data
            f.write(f"Total Systolic Data: {len(systolic_data)}\n")
            # Write the systolic data
            f.write(','.join(map(str, systolic_data.tolist())) + '\n')

        print(f"Processed and saved diastolic and systolic data for {file_name} into {output_file_path}")
    else:
        print(f"File {file_name} not found in the directory {directory_path}.")