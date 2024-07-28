import os
import pandas as pd

# Function to calculate VTI from a given CSV file
def calculate_vti(file_path):
    df = pd.read_csv(file_path, names=['Time', 'Velocity'])
    df['Time_diff'] = df['Time'].diff()
    df = df.dropna(subset=['Time_diff'])
    df['VTI_segment'] = df['Velocity'] * df['Time_diff']
    VTI = df['VTI_segment'].sum()
    return VTI

# Directory containing the CSV files
base_directory = 'vti'

# Dictionaries to store the results
healthy_vti_results = {}
univentricle_vti_results = {}

# Iterate over all files in the directory and subdirectories
for subdir in ['healthy', 'univentricle']:
    directory = os.path.join(base_directory, subdir)
    
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            case_name = filename.split('.')[0]  # Extract case name without extension
            file_path = os.path.join(directory, filename)
            
            # Calculate VTI for the current file
            vti_value = calculate_vti(file_path)
            
            # Store the result in the appropriate dictionary
            if subdir == 'healthy':
                healthy_vti_results[case_name] = vti_value
            elif subdir == 'univentricle':
                univentricle_vti_results[case_name] = vti_value

# Print the results for healthy cases
print("Healthy Cases:")
for case, vti in healthy_vti_results.items():
    print(f"The Velocity Time Integral (VTI) for {case} is: {vti}")

# Print the results for univentricle cases
print("\nUniventricle Cases:")
for case, vti in univentricle_vti_results.items():
    print(f"The Velocity Time Integral (VTI) for {case} is: {vti}")