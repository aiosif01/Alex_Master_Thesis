import pandas as pd
import matplotlib.pyplot as plt
import os
from sklearn.preprocessing import MinMaxScaler
from scipy.interpolate import PchipInterpolator
import numpy as np

# Initialize the scaler for normalization
scaler = MinMaxScaler(feature_range=(0, 1))  # Ensure normalization is from 0 to 1

# Define the base directory for Fluent results and Doppler velocities
fluent_base_dir = 'C:/Users/alexi/Desktop/GitHub/Alex_Master_Thesis/Fluent_Results'  # Fluent results directory
doppler_base_dir = 'C:/Users/alexi/Desktop/GitHub/Alex_Master_Thesis/doppler'  # Doppler velocities directory

# Specify the case you want to plot
case_name = 'hypox03'

# Define paths for the mitral valve (mv) and aortic valve (av) Doppler files
pre_mv_doppler_path = os.path.join(doppler_base_dir, f'{case_name}_pre', f'{case_name}_pre_mv.csv')
post_mv_doppler_path = os.path.join(doppler_base_dir, f'{case_name}_post', f'{case_name}_post_mv.csv')
pre_av_doppler_path = os.path.join(doppler_base_dir, f'{case_name}_pre', f'{case_name}_pre_av.csv')
post_av_doppler_path = os.path.join(doppler_base_dir, f'{case_name}_post', f'{case_name}_post_av.csv')

# Define paths for the Fluent results
pre_fluent_dir = os.path.join(fluent_base_dir, f'{case_name}_pre')
post_fluent_dir = os.path.join(fluent_base_dir, f'{case_name}_post')
pre_mv_fluent_path = os.path.join(pre_fluent_dir, 'ventricle-average-velocity-inlet_interpolated.csv')
post_mv_fluent_path = os.path.join(post_fluent_dir, 'ventricle-average-velocity-inlet_interpolated.csv')
pre_av_fluent_path = os.path.join(pre_fluent_dir, 'ventricle-average-velocity-outlet_interpolated.csv')
post_av_fluent_path = os.path.join(post_fluent_dir, 'ventricle-average-velocity-outlet_interpolated.csv')

# Function to interpolate Doppler data using PCHIP (Piecewise Cubic Hermite Interpolating Polynomial)
def interpolate_doppler_data(df):
    if df is not None and not df.empty:
        interp_func = PchipInterpolator(df['Time'], df['Velocity'], extrapolate=True)  # PCHIP is good for monotonic data
        return interp_func
    return None

# Ensure that the interpolation does not dip below zero
def enforce_non_negative(interp_data):
    return np.maximum(interp_data, 0)

# Function to load and normalize Fluent data
def load_fluent_data(file_path):
    if os.path.exists(file_path):
        fluent_df = pd.read_csv(file_path)
        # Extract the flow time and interpolated data
        time_data = fluent_df['Flow Time'].values
        velocity_data = fluent_df['Interpolated Data'].values * 100  # Multiply by 100 to convert to cm/s
        
        # Normalize time data
        normalized_time = scaler.fit_transform(time_data.reshape(-1, 1)).flatten()
        
        return normalized_time, velocity_data
    else:
        return None, None

# Function to load Doppler data and create interpolation functions
def load_doppler_data(file_path):
    if os.path.exists(file_path):
        doppler_df = pd.read_csv(file_path, header=None)
        doppler_df.columns = ['Time', 'Velocity']
        doppler_df['Time'] = scaler.fit_transform(doppler_df['Time'].values.reshape(-1, 1))
        return interpolate_doppler_data(doppler_df)
    return None

# Load all data
pre_mv_fluent_time, pre_mv_fluent_data = load_fluent_data(pre_mv_fluent_path)
post_mv_fluent_time, post_mv_fluent_data = load_fluent_data(post_mv_fluent_path)
pre_av_fluent_time, pre_av_fluent_data = load_fluent_data(pre_av_fluent_path)
post_av_fluent_time, post_av_fluent_data = load_fluent_data(post_av_fluent_path)

pre_mv_doppler_interp_func = load_doppler_data(pre_mv_doppler_path)
post_mv_doppler_interp_func = load_doppler_data(post_mv_doppler_path)
pre_av_doppler_interp_func = load_doppler_data(pre_av_doppler_path)
post_av_doppler_interp_func = load_doppler_data(post_av_doppler_path)

# Initialize the plot with 2x2 subplots
fig, axs = plt.subplots(2, 2, figsize=(15, 10))

# Define font properties for the legend
legend_font = {'size': 14, 'weight': 'bold'}  # Increase font size and make bold

# Determine common y-axis range for all subplots with a margin
all_velocities = []
datasets = [
    (pre_mv_fluent_data, pre_mv_fluent_time, pre_mv_doppler_interp_func),
    (post_mv_fluent_data, post_mv_fluent_time, post_mv_doppler_interp_func),
    (pre_av_fluent_data, pre_av_fluent_time, pre_av_doppler_interp_func),
    (post_av_fluent_data, post_av_fluent_time, post_av_doppler_interp_func),
]

for fluent_data, fluent_time, doppler_func in datasets:
    if fluent_data is not None:
        all_velocities.extend(fluent_data)
    if doppler_func is not None:
        all_velocities.extend(enforce_non_negative(doppler_func(fluent_time)))

# Manually set y-axis range
y_min, y_max = -2, 130  # Example range from -10 to 100

# Plot data for each subplot
data_pairs = [
    (pre_mv_fluent_time, pre_mv_fluent_data, pre_mv_doppler_interp_func, 0, 0),
    (post_mv_fluent_time, post_mv_fluent_data, post_mv_doppler_interp_func, 0, 1),
    (pre_av_fluent_time, pre_av_fluent_data, pre_av_doppler_interp_func, 1, 0),
    (post_av_fluent_time, post_av_fluent_data, post_av_doppler_interp_func, 1, 1),
]

for fluent_time, fluent_data, doppler_func, row, col in data_pairs:
    ax = axs[row, col]
    if fluent_time is not None:
        ax.plot(fluent_time, fluent_data, label='Fluent - MV' if row == 0 else 'Fluent - AV', color='red')
    if doppler_func is not None:
        doppler_interp_data = enforce_non_negative(doppler_func(fluent_time))
        ax.plot(fluent_time, doppler_interp_data, label='Doppler - MV' if row == 0 else 'Doppler - AV', color='blue')
    ax.legend(loc='upper left', prop=legend_font)
    ax.set_ylim(y_min, y_max)  # Set common y-axis range with margin
    ax.grid(True)
    ax.tick_params(axis='x', labelsize=14, width=2)
    ax.tick_params(axis='y', labelsize=14, width=2)

# Set titles for the columns
axs[0, 0].set_title(f'Healthy {case_name}_pre', fontsize=18, fontweight='bold')
axs[0, 1].set_title(f'Healthy {case_name}_post', fontsize=18, fontweight='bold')

# Set the common y-axis label and x-axis label for the entire figure
fig.text(0.025, 0.5, 'Velocity (cm/s)', va='center', rotation='vertical', fontsize=18, fontweight='bold')
fig.text(0.5, 0.025, 'Normalized Time', ha='center', fontsize=18, fontweight='bold')

# Adjust layout to keep the figure size and spacing consistent
plt.tight_layout(rect=[0.05, 0.05, 1, 0.95])

plt.show()