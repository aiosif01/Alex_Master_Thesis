import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from .volume_analysis import parse_volumes_from_text

def normalize_time(time_intervals):
    """
    Normalize the time intervals to the range [0, 1].
    
    Parameters:
    - time_intervals: Original time intervals.
    
    Returns:
    - normalized_time: Normalized time intervals.
    """
    min_time = min(time_intervals)
    max_time = max(time_intervals)
    normalized_time = [(t - min_time) / (max_time - min_time) for t in time_intervals]
    return normalized_time

def quadratic_interpolation(volumes, time_intervals):
    """
    Perform quadratic interpolation on the given volume data.
    
    Parameters:
    - volumes: List of volume data points.
    - time_intervals: Corresponding time intervals for the volume data.
    
    Returns:
    - interpolated_volumes: Interpolated volume data.
    - fine_time_intervals: Time intervals with finer granularity for interpolation.
    """
    # Normalize time intervals
    time_intervals = normalize_time(time_intervals)
    
    # Define a finer time interval for interpolation
    fine_time_intervals = np.linspace(time_intervals[0], time_intervals[-1], num=100)
    
    # Perform quadratic interpolation
    interp_func = interp1d(time_intervals, volumes, kind='quadratic')
    interpolated_volumes = interp_func(fine_time_intervals)
    
    return interpolated_volumes, fine_time_intervals

def calculate_dv_dt(volumes, time_intervals):
    dv_dt = np.diff(volumes) / np.diff(time_intervals)
    return dv_dt

def min_max_dv_dt(dv_dt):
    min_dv_dt = np.min(dv_dt)
    max_dv_dt = np.max(dv_dt)
    return min_dv_dt, max_dv_dt

def process_volume_derivative(volumes, time_intervals):
    # Perform quadratic interpolation on the volumes
    interpolated_volumes, fine_time_intervals = quadratic_interpolation(volumes, time_intervals)
    
    # Calculate dv/dt on the interpolated data
    interpolated_dv_dt = calculate_dv_dt(interpolated_volumes, fine_time_intervals)
    
    # Find min and max dv/dt from the interpolated data
    min_dv_dt, max_dv_dt = min_max_dv_dt(interpolated_dv_dt)
    
    # Plot dv/dt with only interpolated data
    fig = plot_dv_dt(fine_time_intervals, interpolated_dv_dt)
    
    return min_dv_dt, max_dv_dt, fig

def plot_dv_dt(fine_time_intervals, interpolated_dv_dt):
    """
    Plot the interpolated dv/dt against the normalized time intervals.
    
    Parameters:
    - fine_time_intervals: Finer time intervals for interpolated data.
    - interpolated_dv_dt: Interpolated dv/dt values.
    
    Returns:
    - fig: The matplotlib figure object containing the plot.
    """
    fine_midpoints = (fine_time_intervals[:-1] + fine_time_intervals[1:]) / 2
    
    fig = plt.figure()
    
    # Plot interpolated dv/dt
    plt.plot(fine_midpoints, interpolated_dv_dt, marker='o', linestyle='-', label='Volumetric Derivation')
    
    plt.xlabel('Normalized Cardiac Cycle')
    plt.ylabel('dv/dt (cm³/s)')
    plt.title('Change in Volume over Time')
    plt.grid(True)
    plt.legend()
    
    return fig
