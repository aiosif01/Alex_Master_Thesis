import os
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# Set font style and size globally
plt.rcParams['font.family'] = 'serif'  # Set the font family (e.g., 'serif', 'sans-serif', 'monospace')
plt.rcParams['font.size'] = 14  # Set the font size
plt.rcParams['font.serif'] = ['Times New Roman']  # Specify the serif font style (e.g., 'Times New Roman')
plt.style.use('bmh')  # Use 'bmh' style for the plots

def parse_volumes_from_text(text):
    volumelist_pattern = r'Volumelist: \[(.*?)\]'
    volumelist_match = re.search(volumelist_pattern, text)
    volumes = list(map(float, volumelist_match.group(1).split(', ')))
    
    # Convert volumes from mm³ to ml (1 ml = 1000 mm³)
    volumes = [v / 1000 for v in volumes]
    return volumes

def read_volumes(file_path):
    """Reads volume data from a file and converts from microliters to milliliters."""
    with open(file_path, 'r') as file:
        text = file.read()
    volumes = parse_volumes_from_text(text)
    return volumes

def normalize_time_series(volumes, num_points=100):
    """Normalize time series data to a common number of points."""
    original_time = np.linspace(0, 1, len(volumes))
    interpolated_func = interp1d(original_time, volumes, kind='linear')
    normalized_time = np.linspace(0, 1, num_points)
    normalized_volumes = interpolated_func(normalized_time)
    return normalized_time, normalized_volumes

def process_group_volumes(patient_group, condition, volume_type='raw'):
    """Processes volume data for a group of patients and normalizes the volumes."""
    all_normalized_volumes = []
    
    for patient in patient_group:
        volume_path = f'data/volumes/{volume_type}/{patient}_{condition}.txt'
        if os.path.isfile(volume_path):
            volumes = read_volumes(volume_path)
            _, normalized_volumes = normalize_time_series(volumes)
            all_normalized_volumes.append(normalized_volumes)
    
    return np.array(all_normalized_volumes)

def calculate_mean_and_std(volumes_array):
    """Calculate mean and standard deviation across multiple normalized volume series."""
    mean_volumes = np.mean(volumes_array, axis=0)
    std_volumes = np.std(volumes_array, axis=0)
    return mean_volumes, std_volumes

def plot_group_statistics(normalized_time, stats_healthy_raw, stats_healthy_reconstructed, stats_univentricular_raw, stats_univentricular_reconstructed):
    """Plot the mean and standard deviation for healthy and univentricular patients for both raw and reconstructed volumes."""
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))

    # Top-Left: Healthy Pre and Post Raw Volumes
    mean_healthy_pre_raw, std_healthy_pre_raw = stats_healthy_raw[0]
    mean_healthy_post_raw, std_healthy_post_raw = stats_healthy_raw[1]
    axs[0, 0].plot(normalized_time, mean_healthy_pre_raw, color='blue', label='Pre Mean Volume')
    axs[0, 0].fill_between(normalized_time, mean_healthy_pre_raw - std_healthy_pre_raw, mean_healthy_pre_raw + std_healthy_pre_raw, color='blue', alpha=0.3)
    axs[0, 0].plot(normalized_time, mean_healthy_post_raw, color='cyan', label='Post Mean Volume')
    axs[0, 0].fill_between(normalized_time, mean_healthy_post_raw - std_healthy_post_raw, mean_healthy_post_raw + std_healthy_post_raw, color='cyan', alpha=0.3)
    axs[0, 0].set_title('Healthy Raw Volumes')
    # axs[0, 0].set_ylabel('Volume (ml)')
    axs[0, 0].legend()
    axs[0, 0].grid(True)

    # Top-Right: Univentricular Pre and Post Raw Volumes
    mean_univentricular_pre_raw, std_univentricular_pre_raw = stats_univentricular_raw[0]
    mean_univentricular_post_raw, std_univentricular_post_raw = stats_univentricular_raw[1]
    axs[0, 1].plot(normalized_time, mean_univentricular_pre_raw, color='red', label='Pre Mean Volume')
    axs[0, 1].fill_between(normalized_time, mean_univentricular_pre_raw - std_univentricular_pre_raw, mean_univentricular_pre_raw + std_univentricular_pre_raw, color='red', alpha=0.3)
    axs[0, 1].plot(normalized_time, mean_univentricular_post_raw, color='yellow', label='Post Mean Volume')
    axs[0, 1].fill_between(normalized_time, mean_univentricular_post_raw - std_univentricular_post_raw, mean_univentricular_post_raw + std_univentricular_post_raw, color='yellow', alpha=0.3)
    axs[0, 1].set_title('Univentricular Raw Volumes')
    axs[0, 1].legend()
    axs[0, 1].grid(True)

    # Bottom-Left: Healthy Pre and Post Reconstructed Volumes
    mean_healthy_pre_reconstructed, std_healthy_pre_reconstructed = stats_healthy_reconstructed[0]
    mean_healthy_post_reconstructed, std_healthy_post_reconstructed = stats_healthy_reconstructed[1]
    axs[1, 0].plot(normalized_time, mean_healthy_pre_reconstructed, color='blue', label='Pre Mean Volume')
    axs[1, 0].fill_between(normalized_time, mean_healthy_pre_reconstructed - std_healthy_pre_reconstructed, mean_healthy_pre_reconstructed + std_healthy_pre_reconstructed, color='blue', alpha=0.3)
    axs[1, 0].plot(normalized_time, mean_healthy_post_reconstructed, color='cyan', label='Post Mean Volume')
    axs[1, 0].fill_between(normalized_time, mean_healthy_post_reconstructed - std_healthy_post_reconstructed, mean_healthy_post_reconstructed + std_healthy_post_reconstructed, color='cyan', alpha=0.3)
    axs[1, 0].set_title('Healthy Reconstructed Volumes')
    # axs[1, 0].set_xlabel('Normalized Time')
    # axs[1, 0].set_ylabel('Volume (ml)')
    axs[1, 0].legend()
    axs[1, 0].grid(True)

    # Bottom-Right: Univentricular Pre and Post Reconstructed Volumes
    mean_univentricular_pre_reconstructed, std_univentricular_pre_reconstructed = stats_univentricular_reconstructed[0]
    mean_univentricular_post_reconstructed, std_univentricular_post_reconstructed = stats_univentricular_reconstructed[1]
    axs[1, 1].plot(normalized_time, mean_univentricular_pre_reconstructed, color='red', label='Pre Mean Volume')
    axs[1, 1].fill_between(normalized_time, mean_univentricular_pre_reconstructed - std_univentricular_pre_reconstructed, mean_univentricular_pre_reconstructed + std_univentricular_pre_reconstructed, color='red', alpha=0.3)
    axs[1, 1].plot(normalized_time, mean_univentricular_post_reconstructed, color='yellow', label='Post Mean Volume')
    axs[1, 1].fill_between(normalized_time, mean_univentricular_post_reconstructed - std_univentricular_post_reconstructed, mean_univentricular_post_reconstructed + std_univentricular_post_reconstructed, color='yellow', alpha=0.3)
    axs[1, 1].set_title('Univentricular Reconstructed Volumes')
    # axs[1, 1].set_xlabel('Normalized Time')
    axs[1, 1].legend()
    axs[1, 1].grid(True)

   # Common settings for all subplots
    for ax in axs.flat:
        ax.legend()
        ax.set_xlim(0, 1)

    # Add these lines to set a single x and y label for the entire figure
    fig.supxlabel('Normalized Time', fontsize=20)
    fig.supylabel('Volume (ml)', fontsize=20)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Define patient groups and conditions
    healthy_patients = ['hypox01', 'hypox08', 'hypox20']
    univentricular_patients = ['hypox03', 'hypox09', 'hypox28']
    conditions = ['pre', 'post']

    # Process raw volumes for both groups and conditions
    healthy_pre_volumes_raw = process_group_volumes(healthy_patients, 'pre', volume_type='raw')
    healthy_post_volumes_raw = process_group_volumes(healthy_patients, 'post', volume_type='raw')
    univentricular_pre_volumes_raw = process_group_volumes(univentricular_patients, 'pre', volume_type='raw')
    univentricular_post_volumes_raw = process_group_volumes(univentricular_patients, 'post', volume_type='raw')

    # Process reconstructed volumes for both groups and conditions
    healthy_pre_volumes_reconstructed = process_group_volumes(healthy_patients, 'pre', volume_type='reconstructed')
    healthy_post_volumes_reconstructed = process_group_volumes(healthy_patients, 'post', volume_type='reconstructed')
    univentricular_pre_volumes_reconstructed = process_group_volumes(univentricular_patients, 'pre', volume_type='reconstructed')
    univentricular_post_volumes_reconstructed = process_group_volumes(univentricular_patients, 'post', volume_type='reconstructed')

    # Calculate mean and std for each group and condition
    stats_healthy_raw = (
        calculate_mean_and_std(healthy_pre_volumes_raw),
        calculate_mean_and_std(healthy_post_volumes_raw)
    )
    stats_univentricular_raw = (
        calculate_mean_and_std(univentricular_pre_volumes_raw),
        calculate_mean_and_std(univentricular_post_volumes_raw)
    )
    stats_healthy_reconstructed = (
        calculate_mean_and_std(healthy_pre_volumes_reconstructed),
        calculate_mean_and_std(healthy_post_volumes_reconstructed)
    )
    stats_univentricular_reconstructed = (
        calculate_mean_and_std(univentricular_pre_volumes_reconstructed),
        calculate_mean_and_std(univentricular_post_volumes_reconstructed)
    )

    # Common normalized time vector
    normalized_time = np.linspace(0, 1, 100)

    # Plot the results
    plot_group_statistics(
        normalized_time,
        stats_healthy_raw,
        stats_healthy_reconstructed,
        stats_univentricular_raw,
        stats_univentricular_reconstructed
    )
