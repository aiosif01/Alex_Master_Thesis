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
case_name = 'hypox01_pre'  # Replace with the desired case name
directory_path = 'C:/Users/alexi/Desktop/GitHub/Alex_Master_Thesis/Fluent_Results/hypox01_pre'  # Replace with the correct path

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
    'ventricle-average-kinetic-energy.out'
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
        variable_data = df.iloc[:, 1]
        flow_time = pd.to_numeric(df.iloc[:, 2], errors='coerce')  # Convert to numeric

        # Determine the number of steps in one cardiac cycle
        num_timesteps_per_cycle = len(time_steps) // 3

        # Extract the flow time of the first cardiac cycle
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
        third_cycle_data = variable_data[start_third_cycle:start_third_cycle + num_timesteps_per_cycle + 1].reset_index(drop=True)
        third_cycle_flow_time = pd.concat([first_cycle_flow_time, pd.Series([RR_DURATION])]).reset_index(drop=True)

        # Separate diastolic and systolic data based on indices
        diastolic_data = third_cycle_data.iloc[:diastolic_end_idx].reset_index(drop=True)
        diastolic_flow_time = third_cycle_flow_time.iloc[:diastolic_end_idx].reset_index(drop=True)

        # Insert zero as the first diastolic flow time
        diastolic_flow_time.iloc[0] = 0

        systolic_data = third_cycle_data.iloc[diastolic_end_idx:systolic_end_idx + 1].reset_index(drop=True)
        systolic_flow_time = third_cycle_flow_time.iloc[diastolic_end_idx:systolic_end_idx + 1].reset_index(drop=True)

        # Combine into a DataFrame with four columns
        output_df = pd.DataFrame({
            'Diastolic Flow Time': diastolic_flow_time,
            'Diastolic Data': diastolic_data,
            'Systolic Flow Time': systolic_flow_time,
            'Systolic Data': systolic_data
        })

        # Prepare the output file path
        output_file_path = os.path.join(directory_path, f'{os.path.splitext(file_name)[0]}_TESToutput.csv')

        # Write the DataFrame to the output file
        output_df.to_csv(output_file_path, index=False)

        print(f"Processed and saved diastolic and systolic data for {file_name} into {output_file_path}")
    else:
        print(f"File {file_name} not found in the directory {directory_path}.")