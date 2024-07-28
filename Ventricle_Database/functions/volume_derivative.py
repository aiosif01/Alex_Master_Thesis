import numpy as np
import matplotlib.pyplot as plt
from .volume_analysis import parse_volumes_from_text

def calculate_dv_dt(volumes, time_intervals):
    dv_dt = np.diff(volumes) / np.diff(time_intervals)
    return dv_dt

def min_max_dv_dt(dv_dt):
    min_dv_dt = np.min(dv_dt)
    max_dv_dt = np.max(dv_dt)
    return min_dv_dt, max_dv_dt

def process_volume_derivative(volumes, time_intervals):
    dv_dt = calculate_dv_dt(volumes, time_intervals)
    min_dv_dt, max_dv_dt = min_max_dv_dt(dv_dt)
    fig = plot_dv_dt(time_intervals, dv_dt)
    return min_dv_dt, max_dv_dt, fig

def plot_dv_dt(time_intervals, dv_dt):
    time_intervals_midpoints = (np.array(time_intervals[:-1]) + np.array(time_intervals[1:])) / 2
    fig = plt.figure()
    plt.plot(time_intervals_midpoints, dv_dt, marker='o')
    plt.xlabel('Time (ms)')
    plt.ylabel('dv/dt (cm³/s)')
    plt.title('Change in Volume over Time')
    plt.grid(True)
    return fig
