import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import numpy as np

# Path to the time information CSV file
time_info_path = 'C:/Users/alexi/Desktop/GitHub/Alex_Master_Thesis/Fluent_Results/time_information.csv'

# Load time information
time_info_df = pd.read_csv(time_info_path)

# Function to calculate VTI from a given CSV file with interpolation
def calculate_vti(file_path, start_time, end_time, threshold, phase_name="Custom", plot=False, ax=None):
    # Read CSV without headers (time and velocity columns)
    df = pd.read_csv(file_path, header=None, names=['Time', 'Velocity'])
    
    # Convert 'Time' to seconds for consistency
    df['Time'] = pd.to_timedelta(df['Time'], unit='s').dt.total_seconds()
    
    # Interpolate Time and Velocity on a Fine Grid
    interpolation_function = interp1d(df['Time'], df['Velocity'], kind='linear', fill_value="extrapolate")
    
    # Create a finer time grid for interpolation
    fine_time_grid = np.arange(df['Time'].min(), df['Time'].max(), 0.000001)
    fine_velocities = interpolation_function(fine_time_grid)
    
    # Determine the range of velocities above the threshold
    above_threshold_indices = np.where(fine_velocities > threshold)[0]
    
    if len(above_threshold_indices) == 0:
        # If no velocities are above the threshold, return VTI as 0
        VTI = 0.0
    else:
        # Extract the time and velocity values corresponding to the indices above the threshold
        fine_time_above_threshold = fine_time_grid[above_threshold_indices]
        fine_velocities_above_threshold = fine_velocities[above_threshold_indices]
        
        # Calculate time differences for VTI computation
        time_diffs = np.diff(fine_time_above_threshold)
        
        # Compute VTI for velocities above the threshold
        vti_segments = fine_velocities_above_threshold[:-1] * time_diffs  # VTI = velocity * time
        VTI = np.sum(vti_segments)  # Total VTI

    if plot:
        plot_vti_region(df, fine_time_grid, fine_velocities, fine_time_above_threshold, fine_velocities_above_threshold, threshold, phase_name, ax)
    
    return VTI

# Function to plot the VTI region
def plot_vti_region(original_df, fine_time_grid, fine_velocities, fine_time_above_threshold, fine_velocities_above_threshold, threshold, phase_name, ax):
    ax.plot(original_df['Time'], original_df['Velocity'], label=f'{phase_name} Doppler', linewidth=1)
    
    # Highlight the region where velocity is above the threshold
    ax.fill_between(
        fine_time_above_threshold, 
        0, 
        fine_velocities_above_threshold, 
        color='lightblue', 
        alpha=0.5
    )
    
    ax.set_title(f'VTI Calculation - {phase_name}')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Velocity (m/s)')
    ax.grid(True)
    ax.legend()

# Directory containing the CSV files (relative to where the script is located)
base_directory = os.path.join(os.getcwd(), 'vti')

# Function to get the time information for a specific case
def get_time_information(case_name):
    row = time_info_df[time_info_df['case'] == case_name]
    if not row.empty:
        end_diastole_time = row['END_DIASTOLE_TIME'].values[0]
        rr_duration = row['RR_DURATION'].values[0]
        end_systole_time = rr_duration  # Systole ends at the RR duration
        return end_diastole_time, end_systole_time
    else:
        raise ValueError(f"No time information found for case {case_name}")

# Function to calculate VTI for a specific case, condition, and valve type with subplots
def calculate_case_vti_with_subplots(case_name, case_type, mv_threshold, av_threshold, custom_range=None, plot=False):
    subdir = case_type  # 'healthy' or 'univentricle'
    
    # Get time information for the case
    end_diastole_time, end_systole_time = get_time_information(case_name)
    
    results = {}
    fig, axs = plt.subplots(2, 1, figsize=(10, 12))  # Create subplots for mv and av

    for i, valve_type in enumerate(['mv', 'av']):  # 'mv' for mitral valve, 'av' for aortic valve
        file_name = f"{case_name}_{valve_type}.csv"
        file_path = os.path.join(base_directory, subdir, file_name)
        
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist. Skipping.")
            continue

        # Set the appropriate threshold for the valve type
        threshold = mv_threshold if valve_type == 'mv' else av_threshold
        phase_name = "Mitral Valve" if valve_type == 'mv' else "Aortic Valve"

        if custom_range:
            # Calculate VTI for a custom range
            custom_vti = round(calculate_vti(file_path, start_time=custom_range[0], end_time=custom_range[1], threshold=threshold, plot=plot, ax=axs[i]), 2)
            results[file_name] = {
                'Custom VTI': custom_vti
            }
        else:
            # Calculate VTI for diastole (start of time to end of diastole)
            diastole_vti = round(calculate_vti(file_path, start_time=0, end_time=end_diastole_time, threshold=threshold, phase_name="Diastole", plot=plot, ax=axs[i]), 2)
            
            # Calculate VTI for systole (end of diastole to end of systole)
            systole_vti = round(calculate_vti(file_path, start_time=end_diastole_time, end_time=end_systole_time, threshold=threshold, phase_name="Systole", plot=plot, ax=axs[i]), 2)
            
            results[file_name] = {
                'Diastole VTI': diastole_vti,
                'Systole VTI': systole_vti
            }
    
    plt.tight_layout()
    plt.show()
    
    return results

# Example usage: choose a specific case
case_to_calculate = 'hypox01_pre'  # Specify the exact case and condition here
case_type = 'healthy'  # Specify the type here ('healthy' or 'univentricle')

# Example of custom VTI calculation
custom_time_range = (0.5, 1.0)  # Define your custom start and end time here
mv_threshold = 0.6018  # Set the threshold for mitral valve
av_threshold = 0.5729  # Set the threshold for aortic valve

try:
    # Ask the user if they want to calculate a custom VTI
    calculate_custom = input("Do you want to calculate a custom VTI? (y/n): ").strip().lower()

    if calculate_custom == 'y':
        vti_results = calculate_case_vti_with_subplots(case_to_calculate, case_type, mv_threshold=mv_threshold, av_threshold=av_threshold, custom_range=custom_time_range, plot=True)
    else:
        vti_results = calculate_case_vti_with_subplots(case_to_calculate, case_type, mv_threshold=mv_threshold, av_threshold=av_threshold, plot=True)
    
    for file_name, vti_values in vti_results.items():
        print(f"Results for {file_name}:")
        for phase, vti in vti_values.items():
            print(f"  {phase}: {vti}")
except Exception as e:
    print(str(e))
