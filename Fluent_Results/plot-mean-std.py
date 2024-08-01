import pandas as pd
import matplotlib.pyplot as plt
import re
import os

# Load time information from the CSV file
time_info_df = pd.read_csv('time_information.csv')

def get_time_info(case_name):
    case_row = time_info_df[time_info_df['Case'] == case_name]
    if not case_row.empty:
        return case_row.iloc[0]['RR_DURATION'], case_row.iloc[0]['END_DIASTOLE_TIME'], case_row.iloc[0]['END_SYSTOLE_TIME']
    else:
        raise ValueError(f"Timing information for case '{case_name}' not found.")

def read_out_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    data_lines = []
    for line in lines:
        if re.match(r'^\s*[\d\.\-eE\s]+$', line):
            data_lines.append(line.strip().split())
    
    df = pd.DataFrame(data_lines).apply(pd.to_numeric)
    return df

def process_file(file_path, column_index, label, rr_duration, end_diastole_time, use_absolute_value=False):
    data = read_out_file(file_path)
    
    total_timesteps = len(data)
    iterations_per_cycle = total_timesteps // 3

    last_cycle_data = data.tail(iterations_per_cycle).copy()

    last_cycle_timesteps = len(last_cycle_data)
    time_step_size = rr_duration / last_cycle_timesteps
    last_cycle_data['Actual_Time'] = (last_cycle_data.index - last_cycle_data.index.min()) * time_step_size

    y_values = last_cycle_data.iloc[:, column_index]
    if use_absolute_value:
        y_values = y_values.abs()

    diastolic_data = last_cycle_data[last_cycle_data['Actual_Time'] <= end_diastole_time].iloc[:, column_index]
    systolic_data = last_cycle_data[last_cycle_data['Actual_Time'] > end_diastole_time].iloc[:, column_index]

    if use_absolute_value:
        diastolic_data = diastolic_data.abs()
        systolic_data = systolic_data.abs()

    diastolic_mean = diastolic_data.mean()
    diastolic_std = diastolic_data.std()
    systolic_mean = systolic_data.mean()
    systolic_std = systolic_data.std()

    base_filename = os.path.basename(file_path)
    unit = Y_AXIS_UNITS.get(base_filename, Y_AXIS_UNITS.get(label, 'Value'))

    return {
        'label': f"{label} ({unit})",
        'diastolic_mean': diastolic_mean,
        'diastolic_std': diastolic_std,
        'systolic_mean': systolic_mean,
        'systolic_std': systolic_std
    }

# Adjust the directory and file column mapping as necessary
directory = os.path.join(os.path.dirname(__file__), 'hypox01_pre')

file_column_mapping = {
    'ventricle-average-wss.out': [1],  # Example files
    'ventricle-energy-loss.out': [2],
    'ventricle-average-pressure.out': [1],
    # Add more mappings here
}

file_column_labels = {
    'ventricle-average-wss.out': ['Wall Shear Stress'],
    'ventricle-energy-loss.out': ['Energy Loss'],
    # Add more label mappings here
}

absolute_value_columns = ['ventricle-average-wss.out']

results = []

fig, axs = plt.subplots(3, 3, figsize=(12, 12))

i = 0
for file_name, column_indices in file_column_mapping.items():
    case_name = directory.split(os.sep)[-1]
    try:
        rr_duration, end_diastole_time, end_systole_time = get_time_info(case_name)
    except ValueError as e:
        print(e)
        continue

    file_path = os.path.join(directory, file_name)
    if os.path.exists(file_path):
        labels = file_column_labels.get(file_name, [os.path.basename(file_name)] * len(column_indices))
        
        use_absolute = file_name in absolute_value_columns
        
        for col_idx, label in zip(column_indices, labels):
            ax = axs[i // 3, i % 3]
            result = process_file(file_path, col_idx, label, rr_duration, end_diastole_time, use_absolute_value=use_absolute)
            results.append(result)

            data = read_out_file(file_path)
            total_timesteps = len(data)
            iterations_per_cycle = total_timesteps // 3

            last_cycle_data = data.tail(iterations_per_cycle).copy()
            last_cycle_timesteps = len(last_cycle_data)
            time_step_size = rr_duration / last_cycle_timesteps
            last_cycle_data['Actual_Time'] = (last_cycle_data.index - last_cycle_data.index.min()) * time_step_size

            y_values = last_cycle_data.iloc[:, col_idx]
            if use_absolute:
                y_values = y_values.abs()

            y_label = Y_AXIS_UNITS.get(file_name, 'Value')
            ax.plot(last_cycle_data['Actual_Time'], y_values, label=label)
            ax.set_xlabel('Time (s)')
            ax.set_ylabel(y_label)
            ax.set_title(f"{os.path.basename(file_path)} - {label}")
            ax.axvline(x=end_diastole_time, color='r', linestyle='--', label='End-Diastole')
            ax.legend()
            ax.grid(True)
            i += 1
    else:
        print(f"File not found: {file_path}")

plt.tight_layout()
plt.show()

# Convert results to DataFrame and split into diastolic and systolic phases
df = pd.DataFrame(results)
diastolic_table = df[['label', 'diastolic_mean', 'diastolic_std']]
systolic_table = df[['label', 'systolic_mean', 'systolic_std']]

# Display tables
print("Diastolic Phase Table:")
print(diastolic_table.to_string(index=False))
print("\nSystolic Phase Table:")
print(systolic_table.to_string(index=False))
