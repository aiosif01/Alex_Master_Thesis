import re
import numpy as np
import matplotlib.pyplot as plt

def parse_volumes_from_text(text):
    volumelist_pattern = r'Volumelist: \[(.*?)\]'
    volumelist_match = re.search(volumelist_pattern, text)
    volumes = list(map(float, volumelist_match.group(1).split(', ')))
    
    # Convert volumes from mm³ to ml (1 ml = 1000 mm³)
    volumes = [v / 1000 for v in volumes]
    return volumes

def read_volumes(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
    volumes = parse_volumes_from_text(text)
    
    # Calculate additional volume metrics
    edv = max(volumes)
    edv_position = volumes.index(edv)
    esv = min(volumes)
    esv_position = volumes.index(esv)
    stroke_volume = edv - esv
    
    print(f"Max volume (EDV): {edv} ml at position: {edv_position}")
    print(f"Min volume (ESV): {esv} ml at position: {esv_position}")
    print(f"Stroke volume: {stroke_volume} ml")
    
    return volumes

def calculate_average_volume_difference(old_volumes, new_volumes):
    volume_differences = [new - old for old, new in zip(old_volumes, new_volumes)]
    average_difference = np.mean(volume_differences)
    return average_difference

def calculate_percentage_differences(old_volumes, new_volumes):
    percentage_differences = [(new - old) / old * 100 for old, new in zip(old_volumes, new_volumes)]
    return percentage_differences

def plot_volumes_and_differences(timestamps, old_volumes, new_volumes):
    percentage_differences = calculate_percentage_differences(old_volumes, new_volumes)
    ventricles = [f'ventricle_{i}' for i in range(len(percentage_differences))]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=False)

    # Line plot for volumes with ms timestamps
    ax1.plot(timestamps, old_volumes, label='Old Volumes', marker='o', linestyle='-')
    ax1.plot(timestamps, new_volumes, label='New Volumes', marker='o', linestyle='-')
    ax1.set_ylabel('Volume (ml)')
    ax1.set_title('Volumes Over Time')
    ax1.legend()
    ax1.grid(True)
    ax1.set_xlabel('Time (ms)')

    # Bar plot for percentage differences with ventricle labels
    ax2.bar(ventricles, percentage_differences, width=0.5, color='skyblue', alpha=0.7)
    ax2.set_ylabel('Percentage Difference (%)')
    ax2.set_title('Volume Percentage Differences Over Time')
    ax2.axhline(0, color='black', linewidth=0.5)
    ax2.grid(True)
    ax2.set_xlabel('Ventricles')
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right', fontsize=8)

    plt.tight_layout()
    return fig  # Return the figure object instead of showing it directly
