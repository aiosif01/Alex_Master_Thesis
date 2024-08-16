import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# Load time information from the CSV file
time_info_df = pd.read_csv('C:/Users/alexi/Desktop/GitHub/Alex_Master_Thesis/Fluent_Results/time_information.csv')

def get_time_info(case_name):
    case_row = time_info_df[time_info_df['case'] == case_name]
    if not case_row.empty:
        return case_row.iloc[0]['RR_DURATION'], case_row.iloc[0]['END_DIASTOLE_TIME'], case_row.iloc[0]['END_SYSTOLE_TIME'], case_row.iloc[0]['TIMESTEPS']
    else:
        raise ValueError(f"Timing information for case '{case_name}' not found.")

# Manually select the case name and directory path
case_name = 'hypox01_pre'  # Replace with the desired case name
directory_path = 'C:/Users/alexi/Desktop/GitHub/Alex_Master_Thesis/Fluent_Results/hypox01_pre'  # Replace with the correct path

# Get the time information for the selected case
try:
    RR_DURATION, END_DIASTOLE_TIME, END_SYSTOLE_TIME, total_timesteps = get_time_info(case_name)
    print(f"Case: {case_name}")
    print(f"End Diastolic Time: {END_DIASTOLE_TIME}")
    print(f"End Systolic Time: {END_SYSTOLE_TIME}")
    print(f"Total Timesteps: {total_timesteps}")
except ValueError as e:
    print(e)
    exit()

# Manually select which .out files to work on
selected_files = [
    'ventricle-energy-loss.out'
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

        # The diastolic_flow_time and systolic_flow_time are defined here
        diastolic_flow_time = third_cycle_flow_time.iloc[:diastolic_end_idx].reset_index(drop=True)
        systolic_flow_time = third_cycle_flow_time.iloc[diastolic_end_idx:systolic_end_idx + 1].reset_index(drop=True)
        diastolic_data = third_cycle_data.iloc[:diastolic_end_idx].reset_index(drop=True)
        systolic_data = third_cycle_data.iloc[diastolic_end_idx:systolic_end_idx + 1].reset_index(drop=True)

        # Ensure the 0.0 time point is included in the diastolic flow time
        diastolic_flow_time.iloc[0] = 0.0

        # Combine into a DataFrame with four columns (raw data)
        output_df_raw = pd.DataFrame({
            'Diastolic Flow Time': diastolic_flow_time,
            'Diastolic Data': diastolic_data,
            'Systolic Flow Time': systolic_flow_time,
            'Systolic Data': systolic_data
        })

        # Prepare the output file path for the raw data
        output_file_path_raw = os.path.join(directory_path, f'{os.path.splitext(file_name)[0]}_raw.csv')

        # Write the DataFrame with raw data to the output file
        output_df_raw.to_csv(output_file_path_raw, index=False)

        # Combine the flow times and data for interpolation
        combined_flow_time = pd.concat([diastolic_flow_time, systolic_flow_time]).reset_index(drop=True)
        combined_data = pd.concat([diastolic_data, systolic_data]).reset_index(drop=True)

        # Ensure combined_flow_time and combined_data are of equal length
        min_length = min(len(combined_flow_time), len(combined_data))
        combined_flow_time = combined_flow_time.iloc[:min_length]
        combined_data = combined_data.iloc[:min_length]

        # Convert combined_data and interpolated_data to numeric to ensure correct plotting
        combined_data = pd.to_numeric(combined_data, errors='coerce')
        # Perform interpolation (you can choose the method: linear, quadratic, cubic, etc.)
        interp_func = interp1d(combined_flow_time, combined_data, kind='quadratic', fill_value="extrapolate")

        # Generate new time steps for interpolation, ensuring the number of steps is total_timesteps + 1
        new_time_steps = np.linspace(0, RR_DURATION, total_timesteps + 1)

        # Interpolate data for new time steps
        interpolated_data = interp_func(new_time_steps)

        # Combine into a DataFrame with two columns (interpolated data)
        output_df_interpolated = pd.DataFrame({
            'Flow Time': new_time_steps,
            'Interpolated Data': interpolated_data
        })

        # Prepare the output file path for the interpolated data
        output_file_path_interpolated = os.path.join(directory_path, f'{os.path.splitext(file_name)[0]}_interpolated.csv')

        # Write the DataFrame with interpolated data to the output file
        output_df_interpolated.to_csv(output_file_path_interpolated, index=False)

        # Plot raw and interpolated data
        plt.figure(figsize=(10, 6))
        plt.plot(combined_flow_time, combined_data, 'o', label='Raw Data', markersize=5)
        plt.plot(new_time_steps, interpolated_data, '-', label='Interpolated Data')

        # Labels and title
        plt.xlabel('Flow Time')
        plt.ylabel('Variable of Interest')
        plt.title('Comparison of Raw Data and Interpolated Data')

        # Ensure the y-axis scale is correct to see both raw and interpolated data
        plt.ylim([min(combined_data.min(), interpolated_data.min()), max(combined_data.max(), interpolated_data.max())])

        # Add grid and legend
        plt.grid(True)
        plt.legend()

        # Show plot
        plt.show()

        print(f"Processed and saved raw data for {file_name} into {output_file_path_raw}")
        print(f"Processed and saved interpolated data for {file_name} into {output_file_path_interpolated}")
    else:
        print(f"File {file_name} not found in the directory {directory_path}.")
