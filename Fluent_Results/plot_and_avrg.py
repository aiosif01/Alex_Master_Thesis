import pandas as pd
import matplotlib.pyplot as plt
import re
import os

# Timing Information (converted to seconds)
RR_DURATION = 0.923077  # in seconds
END_DIASTOLE_TIME = 0.597829  # in seconds
END_SYSTOLE_TIME = 0.325248  # in seconds

# SI units for the results
Y_AXIS_UNITS = {
    'avrg-wss.out': 'Wall Shear Stress (Pa)',
    'energy-loss.out': 'Energy Loss (J)',
    'flow-valves-av.out': 'Flow (m³/s)',
    'flow-valves-mv.out': 'Flow (m³/s)',
    'report-flow-av': 'Flow (m³/s)',
    'report-flow-mv': 'Flow (m³/s)',
    'report-ven-ave-vel-inlet-rfile.out': 'Velocity (m/s)',
    'report-ven-ave-vel-outlet-rfile.out': 'Velocity (m/s)',
    'report-ven-kin-energy-rfile.out': 'Kinetic Energy (J)',
    'tvpg.out': 'Pressure Gradient (Pa)',
    'ven-vol.out': 'Volume (m³)',
}

def read_out_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    data_lines = []
    for line in lines:
        if re.match(r'^\s*[\d\.\-eE\s]+$', line):
            data_lines.append(line.strip().split())
    
    df = pd.DataFrame(data_lines).apply(pd.to_numeric)
    return df

def process_file(file_path, column_index, label, use_absolute_value=False):
    data = read_out_file(file_path)
    
    total_timesteps = len(data)
    iterations_per_cycle = total_timesteps // 3

    last_cycle_data = data.tail(iterations_per_cycle).copy()

    last_cycle_timesteps = len(last_cycle_data)
    time_step_size = RR_DURATION / last_cycle_timesteps
    last_cycle_data['Actual_Time'] = (last_cycle_data.index - last_cycle_data.index.min()) * time_step_size

    y_values = last_cycle_data.iloc[:, column_index]
    if use_absolute_value:
        y_values = y_values.abs()

    diastolic_data = last_cycle_data[last_cycle_data['Actual_Time'] <= END_DIASTOLE_TIME].iloc[:, column_index]
    systolic_data = last_cycle_data[last_cycle_data['Actual_Time'] > END_DIASTOLE_TIME].iloc[:, column_index]

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

directory = os.path.join(os.path.dirname(__file__), 'hypox01_pre_turb')

file_column_mapping = {
    'avrg-wss.out': [2],
    'energy-loss.out': [2],
    'flow-valves-av.out': [2],
    'flow-valves-mv.out': [3],
    'report-ven-ave-vel-inlet-rfile.out': [1],
    'report-ven-ave-vel-outlet-rfile.out': [1],
    'report-ven-kin-energy-rfile.out': [1],
    'tvpg.out': [2],
    'ven-vol.out': [2],
}

file_column_labels = {
    'flow-valves-av.out': ['report-flow-av'],
    'flow-valves-mv.out': ['report-flow-mv'],
}

absolute_value_columns = ['flow-valves-av.out']

results = []

fig, axs = plt.subplots(3, 3, figsize=(12, 12))

i = 0
for file_name, column_indices in file_column_mapping.items():
    if file_name in ['flow-valves-av.out', 'flow-valves-mv.out']:
        original_file_name = 'flow-valves.out'
    else:
        original_file_name = file_name
    file_path = os.path.join(directory, original_file_name)
    if os.path.exists(file_path):
        labels = file_column_labels.get(file_name, [os.path.basename(file_name)] * len(column_indices))
        
        # Set use_absolute_value to True for 'report-flow-av.out'
        use_absolute = file_name in absolute_value_columns or file_name == 'report-flow-av.out'
        
        for col_idx, label in zip(column_indices, labels):
            ax = axs[i // 3, i % 3]
            result = process_file(file_path, col_idx, label, use_absolute_value=use_absolute)
            results.append(result)
            # Plotting
            data = read_out_file(file_path)
            total_timesteps = len(data)
            iterations_per_cycle = total_timesteps // 3

            last_cycle_data = data.tail(iterations_per_cycle).copy()
            last_cycle_timesteps = len(last_cycle_data)
            time_step_size = RR_DURATION / last_cycle_timesteps
            last_cycle_data['Actual_Time'] = (last_cycle_data.index - last_cycle_data.index.min()) * time_step_size

            y_values = last_cycle_data.iloc[:, col_idx]
            if use_absolute:
                y_values = y_values.abs()

            y_label = Y_AXIS_UNITS.get(file_name, 'Value')
            ax.plot(last_cycle_data['Actual_Time'], y_values, label=label)
            ax.set_xlabel('Time (s)')
            ax.set_ylabel(y_label)
            ax.set_title(f"{os.path.basename(file_path)} - {label}")
            ax.axvline(x=END_DIASTOLE_TIME, color='r', linestyle='--', label='End-Diastole')
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