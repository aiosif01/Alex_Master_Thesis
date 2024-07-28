# ventricle_database
This Python database analyzes cardiovascular data for left heart ventricle and univentricle patients. It examines mitral and aortic valve characteristics, volume differences, derivatives, and mitral valve shape using Ramanujan's ellipsoid equation. Users select healthy or univentricle cases and specify pre or post-exercise conditions.



## Overview
This repository contains a Python project for analyzing cardiac volumes using raw and reconstructed volume data. The project includes calculations for stroke volumes, volume derivatives, valve areas, and Reynolds numbers. The results are output to the console and saved in a structured CSV file.

## Features
- Parse header files to extract relevant timestamps and RR durations.
- Read and process raw and reconstructed volume data.
- Calculate stroke volumes and their differences.
- Compute volume derivatives (dV/dt) and identify minimum and maximum values.
- Analyze Doppler data to compute aortic and mitral valve areas and shapes.
- Calculate Reynolds numbers for flow characterization.
- Save detailed results in a structured CSV format.
- Plot results including volumes, volume derivatives, and mitral valve shapes.

## You can run the code as follows:
`cd ventricle_database`

`python -u main.py`
