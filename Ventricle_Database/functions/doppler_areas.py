import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def read_doppler_data(aortic_csv=None, mitral_csv=None):
    max_velocity_aortic = None
    max_velocity_mitral = None
    
    if aortic_csv:
        aortic_data = pd.read_csv(aortic_csv, header=None)
        max_velocity_aortic = aortic_data.iloc[:, -1].max()
    
    if mitral_csv:
        mitral_data = pd.read_csv(mitral_csv, header=None)
        max_velocity_mitral = mitral_data.iloc[:, -1].max()
    
    return max_velocity_aortic, max_velocity_mitral

def calculate_valve_areas(min_dv_dt, max_dv_dt, max_velocity_aortic, max_velocity_mitral, short_diameter_mitral, tolerance=1e-8, max_iterations=1000):
    # Convert velocities from cm/s to cm/ms
    max_velocity_aortic /= 1000
    max_velocity_mitral /= 1000

    # Calculate aortic valve area
    area_aortic = (-min_dv_dt) / max_velocity_aortic * 100
    diameter_aortic = 2 * np.sqrt(area_aortic / np.pi)

    # Calculate initial mitral valve area
    area_mitral = (max_dv_dt) / max_velocity_mitral * 100

    # Define constants for mitral valve short axes
    upper_short_axis_mitral = short_diameter_mitral / 2 * 0.65
    lower_short_axis_mitral = short_diameter_mitral / 2 * 1.1

    # Initialize variables
    long_axis_mitral = np.sqrt(area_mitral / np.pi)
    upper_area = np.pi * long_axis_mitral * upper_short_axis_mitral
    lower_area = np.pi * long_axis_mitral * lower_short_axis_mitral
    calculated_area = (upper_area + lower_area) / 2

    # Iterate to refine the long axis
    for _ in range(max_iterations):
                
        error = area_mitral - calculated_area
        if abs(error) < tolerance:
            break

        # Derivative of the area with respect to long axis (a)
        derivative = np.pi * (upper_short_axis_mitral + lower_short_axis_mitral) / 2

        # Update long axis using Newton-Raphson method
        long_axis_mitral += error / derivative

        # Update Values
        upper_area = np.pi * long_axis_mitral * upper_short_axis_mitral
        lower_area = np.pi * long_axis_mitral * lower_short_axis_mitral
        calculated_area = (upper_area + lower_area) / 2

    # Calculate the updated mitral valve area
    updated_new_area_mitral = (np.pi * long_axis_mitral * (upper_short_axis_mitral + lower_short_axis_mitral)) / 2

    # Calculate the hydraulic diameter and perimeter
    perimeter_upper = np.pi * (3*(long_axis_mitral + upper_short_axis_mitral) - np.sqrt((3*long_axis_mitral + upper_short_axis_mitral)*(long_axis_mitral + 3*upper_short_axis_mitral)))
    perimeter_lower = np.pi * (3*(long_axis_mitral + lower_short_axis_mitral) - np.sqrt((3*long_axis_mitral + lower_short_axis_mitral)*(long_axis_mitral + 3*lower_short_axis_mitral)))
    perimeter_mitral = (perimeter_upper + perimeter_lower) / 2
    hydraulic_diameter_mitral = 4 * updated_new_area_mitral / perimeter_mitral

    return (area_aortic, diameter_aortic, area_mitral, updated_new_area_mitral, long_axis_mitral, 
            upper_short_axis_mitral, lower_short_axis_mitral, hydraulic_diameter_mitral, perimeter_mitral)

def plot_mitral_valve_shape(a, b_upper, b_lower):
    t = np.linspace(0, np.pi, 100)
    x = a * np.cos(t)
    y_upper = b_upper * np.sin(t)
    y_lower = b_lower * np.sin(t)

    plt.style.use('ggplot')
    fig = plt.figure(figsize=(6, 6))
    plt.plot(x, y_upper, label='Anterior Leaflet')
    plt.plot(x, -y_lower, label='Posterior Leaflet')
    plt.axhline(0, color='grey', linewidth=0.5)
    plt.axvline(0, color='grey', linewidth=0.5)
    plt.xlabel('Anterolateral-Posteromedial Diameter (mm)')
    plt.ylabel('Anterior-Posterior Diameter (mm)')
    plt.title('Approximal Mitral Valve Shape')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    return fig  # Return the figure object instead of showing it directly
