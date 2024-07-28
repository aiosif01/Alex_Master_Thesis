def calculate_reynolds_number(d_h_mm, velocity_cm_s, rho=1055, kv=0.0037):
    d_h_m = d_h_mm * 0.001
    velocity_m_s = velocity_cm_s / 100
    re = (rho * velocity_m_s * d_h_m) / kv
    flow_type = "Laminar" if re < 2300 else "Turbulent"
    return re, flow_type
