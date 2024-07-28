def print_time_information(avg_rr_duration, endsystole_time, enddiastole_time):
    print(f"\nAverage RR Duration: {avg_rr_duration:.2f} ms")
    print(f"Enddiastole Time: {enddiastole_time:.2f} ms")
    print(f"Endsystole Time: {endsystole_time:.2f} ms")

def print_volume_information(title, edv, edv_position, esv, esv_position, stroke_volume):
    print(f"\n{title}")
    print(f"Max volume (EDV): {edv:.4f} ml at position: {edv_position}")
    print(f"Min volume (ESV): {esv:.4f} ml at position: {esv_position}")
    print(f"Stroke volume: {stroke_volume:.4f} ml")

def print_average_volume_difference(average_difference):
    print(f"Average Volume Difference: {average_difference:.4f} ml")

def print_velocity(max_velocity_aortic, max_velocity_mitral):
    print(f"Max Velocity (Aortic): {max_velocity_aortic} cm/s")
    print(f"Max Velocity (Mitral): {max_velocity_mitral} cm/s")

def print_valve_results(area_aortic, diameter_aortic, area_mitral, new_area_mitral, a, upper_short_axis_mitral, lower_short_axis_mitral, hydraulic_diameter_mitral, perimeter_mitral):
    print("\n--- AORTIC VALVE RESULTS ---")
    print(f"Aortic Valve Area: {area_aortic:.4f} mm^2")
    print(f"Aortic Valve Radius: {diameter_aortic / 2:.4f} mm")

    print("\n--- MITRAL VALVE RESULTS ---")
    print(f"Mitral Valve Area: {area_mitral:.4f} mm^2")
    print(f"Updated Mitral Valve Area (after iterations): {new_area_mitral:.4f} mm^2")
    print(f"Mitral Valve Long Axis Radius (after iterations): {a:.4f} mm")
    print(f"Mitral Valve Upper Short Axis Radius: {upper_short_axis_mitral:.4f} mm")
    print(f"Mitral Valve Lower Short Axis Radius: {lower_short_axis_mitral:.4f} mm")
    print(f"Mitral Valve Hydraulic Diameter: {hydraulic_diameter_mitral:.4f} mm")
    print(f"Mitral Valve Circumference: {perimeter_mitral:.4f} mm")

def print_reynolds_number(re_mitral, flow_type_mitral):
    print(f"\nReynolds Number (Mitral Valve): {re_mitral:.2f} ({flow_type_mitral} flow)")
