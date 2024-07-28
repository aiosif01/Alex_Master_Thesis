def parse_timestamps_from_header(header_file):
    timestamps = []
    with open(header_file, 'r') as file:
        lines = file.readlines()
        start_reading = False
        for line in lines:
            if line.strip() == '#Timestamps':
                start_reading = True
                continue
            if start_reading:
                if line.strip() and '#' not in line.strip():
                    timestamps.append(float(line.split()[0]))
    return timestamps

def parse_rr_duration_from_header(header_file):
    with open(header_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('Average RR Duration'):
                avg_rr_duration = float(line.split()[3])
            elif line.startswith('Endsystole time'):
                endsystole_time = float(line.split()[2])
        enddiastole_time = avg_rr_duration - endsystole_time
        return avg_rr_duration, endsystole_time, enddiastole_time
