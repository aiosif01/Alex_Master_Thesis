import pandas as pd
import os
import numpy as np

# Define the directory path
directory_path = 'C:/Users/alexi/Desktop/GitHub/Alex_Master_Thesis/Fluent_Results/hypox01_pre'  # Replace with your correct path

# Dictionary mapping CSV files to their corresponding multipliers
csv_files = {
    'ventricle-average-kinetic-energy_TESToutput.csv': 1,   # No unit conversion
    # 'another-file.csv': 1000,   # Convert from Joules to milliJoules
    # Add more files and their multipliers as needed
}

# Initialize lists to store results
results = []

# Process each CSV file
for csv_file_name, multiplier in csv_files.items():
    csv_file = os.path.join(directory_path, csv_file_name)

    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Perform calculations for diastolic phase
    diastolic_mean = np.round(df['Diastolic Data'].mean() * multiplier, 3)
    diastolic_std = np.round(df['Diastolic Data'].std() * multiplier, 3)

    # Perform calculations for systolic phase
    systolic_mean = np.round(df['Systolic Data'].mean() * multiplier, 3)
    systolic_std = np.round(df['Systolic Data'].std() * multiplier, 3)

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
