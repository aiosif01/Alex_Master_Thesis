import os
import matplotlib.pyplot as plt
import pandas as pd

# Import the necessary functions
from functions.header_processing import parse_timestamps_from_header, parse_rr_duration_from_header
from functions.volume_analysis import calculate_average_volume_difference, plot_volumes_and_differences
from functions.volume_derivative import calculate_dv_dt, min_max_dv_dt, plot_dv_dt, process_volume_derivative  # Ensure process_volume_derivative is imported
from functions.doppler_areas import read_doppler_data, calculate_valve_areas, plot_mitral_valve_shape
from functions.output import print_time_information, print_volume_information, print_average_volume_difference, print_velocity, print_valve_results, print_reynolds_number
from functions.reynolds import calculate_reynolds_number

# Average short diameter of MV for each patient (in mm)
short_valve_diameters = {
    'hypox01': 24.35,
    'hypox08': 28.0,
    'hypox20': 30.0,
    'hypox09': 24.5,
    'hypox03': 27.5,
    'hypox28': 28.5
}

def read_volumes_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    volume_list = eval(lines[3].split(': ')[1])  # Extract the volumelist from the 4th line
    return [v / 1000 for v in volume_list]  # Convert from microliters to milliliters

def process_single_case(case):
    patient_type, patient, condition = case['patient_type'], case['patient'], case['condition']
    case_path = case['case_path']
    raw_volume_path = case['raw_volume_path']
    reconstructed_volume_path = case['reconstructed_volume_path']
    aortic_csv = case['aortic_csv']
    mitral_csv = case['mitral_csv']
    short_valve_diameter = case['short_valve_diameter']

    # Read header and volume data
    header_file = os.path.join(case_path, 'header.txt')
    rr_duration_timestamps = parse_timestamps_from_header(header_file)
    avg_rr_duration, endsystole_time, enddiastole_time = parse_rr_duration_from_header(header_file)
    old_volumes = read_volumes_from_file(raw_volume_path)

    edv = max(old_volumes)
    edv_position = old_volumes.index(edv)
    esv = min(old_volumes)
    esv_position = old_volumes.index(esv)
    stroke_volume = edv - esv

    # Print time information
    print_time_information(avg_rr_duration, endsystole_time, enddiastole_time)

    # Print raw volume information
    print_volume_information("Raw", edv, edv_position, esv, esv_position, stroke_volume)

    average_difference = None
    if os.path.isfile(reconstructed_volume_path):
        new_volumes = read_volumes_from_file(reconstructed_volume_path)
        edv_reconstructed = max(new_volumes)
        edv_position_reconstructed = new_volumes.index(edv_reconstructed)
        esv_reconstructed = min(new_volumes)
        esv_position_reconstructed = new_volumes.index(esv_reconstructed)
        stroke_volume_reconstructed = edv_reconstructed - esv_reconstructed
        
        # Print reconstructed volume information
        print_volume_information("Reconstructed", edv_reconstructed, edv_position_reconstructed, esv_reconstructed, esv_position_reconstructed, stroke_volume_reconstructed)
        
        # Calculate and print average volume difference
        average_difference = calculate_average_volume_difference(old_volumes, new_volumes)
        print_average_volume_difference(average_difference)

    # Calculate volume derivative
    dv_dt = calculate_dv_dt(old_volumes, rr_duration_timestamps)
    min_dv_dt, max_dv_dt = min_max_dv_dt(dv_dt)

    # Read Doppler data
    max_velocity_aortic, max_velocity_mitral = read_doppler_data(aortic_csv, mitral_csv)
    print_velocity(max_velocity_aortic, max_velocity_mitral)

    # Calculate valve areas
    valve_areas = calculate_valve_areas(min_dv_dt, max_dv_dt, max_velocity_aortic, max_velocity_mitral, short_valve_diameter)
    print_valve_results(*valve_areas[:9])

    # Calculate and print Reynolds number
    re_mitral, flow_type_mitral = calculate_reynolds_number(valve_areas[7], max_velocity_mitral)
    print_reynolds_number(re_mitral, flow_type_mitral)

    # Save results to a DataFrame
    results = {
        'Patient': patient,
        'Condition': condition,
        'Average RR Duration (ms)': avg_rr_duration,
        'Enddiastole Time (ms)': enddiastole_time,
        'Endsystole Time (ms)': endsystole_time,
        'Average Volume Difference (ml)': average_difference if average_difference is not None else 'N/A',
        'Min dV/dt (ml/ms)': min_dv_dt,
        'Max dV/dt (ml/ms)': max_dv_dt,
        'Max Velocity Aortic (cm/s)': max_velocity_aortic,
        'Max Velocity Mitral (cm/s)': max_velocity_mitral,
        'Aortic Valve Area (mm^2)': valve_areas[0],
        'Mitral Valve Area (mm^2)': valve_areas[2],
        'Mitral Valve Long Axis (mm)': valve_areas[4],
        'Mitral Valve Upper Short Axis (mm)': valve_areas[5],
        'Mitral Valve Lower Short Axis (mm)': valve_areas[6],
        'Mitral Valve Hydraulic Diameter (mm)': valve_areas[7],
        'Mitral Valve Circumference (mm)': valve_areas[8],
        'Reynolds Number Mitral': re_mitral,
        'Flow Type Mitral': flow_type_mitral,
        'EDV (ml)': edv,
        'EDV Position': edv_position,
        'ESV (ml)': esv,
        'ESV Position': esv_position,
        'Stroke Volume (ml)': stroke_volume
    }
    if average_difference is not None:
        results.update({
            'EDV Reconstructed (ml)': edv_reconstructed,
            'EDV Position Reconstructed': edv_position_reconstructed,
            'ESV Reconstructed (ml)': esv_reconstructed,
            'ESV Position Reconstructed': esv_position_reconstructed,
            'Stroke Volume Reconstructed (ml)': stroke_volume_reconstructed
        })

    # Save results to a CSV file
    output_file = f'output/{patient}_{condition}_results.csv'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as file:
        file.write(f"Average RR Duration: {avg_rr_duration:.2f} ms\n")
        file.write(f"Enddiastole Time: {enddiastole_time:.2f} ms\n")
        file.write(f"Endsystole Time: {endsystole_time:.2f} ms\n\n")
        file.write(f"Raw\n")
        file.write(f"Max volume (EDV): {edv:.4f} ml at position: {edv_position}\n")
        file.write(f"Min volume (ESV): {esv:.4f} ml at position: {esv_position}\n")
        file.write(f"Stroke volume: {stroke_volume:.4f} ml\n\n")
        if average_difference is not None:
            file.write(f"Reconstructed\n")
            file.write(f"Max volume (EDV): {edv_reconstructed:.4f} ml at position: {edv_position_reconstructed}\n")
            file.write(f"Min volume (ESV): {esv_reconstructed:.4f} ml at position: {esv_position_reconstructed}\n")
            file.write(f"Stroke volume: {stroke_volume_reconstructed:.4f} ml\n\n")
            file.write(f"Average Volume Difference: {average_difference:.4f} ml\n\n")
        file.write(f"Max Velocity (Aortic): {max_velocity_aortic:.2f} cm/s\n")
        file.write(f"Max Velocity (Mitral): {max_velocity_mitral:.2f} cm/s\n\n")
        file.write(f"Min dV/dt (Aortic): {min_dv_dt:.4f} ml/ms\n")
        file.write(f"Max dV/dt (Mitral): {max_dv_dt:.4f} ml/ms\n\n")
        file.write(f"--- AORTIC VALVE RESULTS ---\n")
        file.write(f"Aortic Valve Area: {valve_areas[0]:.4f} mm^2\n")
        file.write(f"Aortic Valve Radius: {valve_areas[0] ** 0.5 / 3.14159 * 2:.4f} mm\n\n")
        file.write(f"--- MITRAL VALVE RESULTS ---\n")
        file.write(f"Mitral Valve Area: {valve_areas[2]:.4f} mm^2\n")
        file.write(f"Updated Mitral Valve Area (after iterations): {valve_areas[2]:.4f} mm^2\n")
        file.write(f"Mitral Valve Long Axis Radius (after iterations): {valve_areas[4]:.4f} mm\n")
        file.write(f"Mitral Valve Upper Short Axis Radius: {valve_areas[5]:.4f} mm\n")
        file.write(f"Mitral Valve Lower Short Axis Radius: {valve_areas[6]:.4f} mm\n")
        file.write(f"Mitral Valve Hydraulic Diameter: {valve_areas[7]:.4f} mm\n")
        file.write(f"Mitral Valve Circumference: {valve_areas[8]:.4f} mm\n\n")
        file.write(f"Reynolds Number (Mitral Valve): {re_mitral:.2f} ({flow_type_mitral} flow)\n")

    print(f"Results saved to {output_file}")

    # Plot results
    figs = []
    figs.append(plot_volumes_and_differences(rr_duration_timestamps, old_volumes, new_volumes))
    min_dv_dt, max_dv_dt, dv_dt_fig = process_volume_derivative(old_volumes, rr_duration_timestamps)
    figs.append(dv_dt_fig)
    figs.append(plot_mitral_valve_shape(valve_areas[4], valve_areas[5], valve_areas[6]))

    for fig in figs:
        plt.show()  # Display each figure

if __name__ == "__main__":
    # Prompt user for patient selection
    patient_types = ['healthy', 'fontan']
    patients = {
        'healthy': ['hypox01', 'hypox08', 'hypox20'],
        'fontan': ['hypox03', 'hypox09', 'hypox28']
    }
    conditions = ['pre', 'post']

    print("Select patient type:")
    for i, patient_type in enumerate(patient_types):
        print(f"{i+1}: {patient_type}")
    selected_patient_type = patient_types[int(input("Enter patient type number: ")) - 1]

    print("Select patient:")
    for i, patient in enumerate(patients[selected_patient_type]):
        print(f"{i+1}: {patient}")
    selected_patient = patients[selected_patient_type][int(input("Enter patient number: ")) - 1]

    print("Select condition (1: pre, 2: post):")
    selected_condition = conditions[int(input("Enter condition number: ")) - 1]

    # Convert patient to lowercase to match file naming convention
    selected_patient = selected_patient.lower()

    case = {
        'patient_type': selected_patient_type,
        'patient': selected_patient,
        'condition': selected_condition,
        'case_path': f'data/{selected_patient_type}/{selected_condition}/{selected_patient}',
        'raw_volume_path': f'data/volumes/raw/{selected_patient}_{selected_condition}.txt',
        'reconstructed_volume_path': f'data/volumes/reconstructed/{selected_patient}_{selected_condition}.txt',
        'aortic_csv': None,
        'mitral_csv': None,
        'short_valve_diameter': short_valve_diameters[selected_patient]
    }

    # Check for different CSV file naming conventions
    for filename in ['aortic.csv', 'mitral.csv', 'av.csv', 'avv.csv']:
        filepath = os.path.join(case['case_path'], filename)
        if os.path.isfile(filepath):
            if 'aortic' in filename or 'av.csv' in filename:
                case['aortic_csv'] = filepath
            if 'mitral' in filename or 'avv.csv' in filename:
                case['mitral_csv'] = filepath

    # Special handling for Hypox28 which has only avv.csv
    if selected_patient == 'hypox28' and case['mitral_csv']:
        case['aortic_csv'] = case['mitral_csv']

    process_single_case(case)
    plt.show()  # Ensure that all figures remain displayed
