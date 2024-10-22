import subprocess
from datetime import datetime

# Function to execute a script with given parameters and a timeout
def execute_script(script_name, params, timeout=1200):  # Increased timeout to 1200 seconds (20 minutes)
    command = ['python3', script_name] + params
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            print(f"{script_name} executed successfully.")
            print(result.stdout)
        else:
            print(f"Error executing {script_name}: {result.stderr}")
    except subprocess.TimeoutExpired:
        print(f"Error: {script_name} timed out after {timeout} seconds.")

# Parameters for INDEC_employment.py
employment_params = ['Argentina']

# Parameters for INDEC_inflation.py
current_year = datetime.now().year
current_month = datetime.now().month
last_year = current_year - 1
periodo_desde = f"{last_year}01"
periodo_hasta = f"{current_year}{current_month:02d}"
num_periodos_proyeccion = '12'  # Example value, adjust as needed
inflation_params = [periodo_desde, periodo_hasta, num_periodos_proyeccion]

# Calculate date_from and date_until for BCRA_exchangerate.py
date_from = f"{last_year}-01-01"
date_until = datetime.now().strftime("%Y-%m-%d")
bcra_params = [date_from, date_until]

# Execute INDEC_employment.py with an increased timeout
execute_script('INDEC_employment.py', employment_params, timeout=1200)
# Execute INDEC_inflation.py with an increased timeout
execute_script('INDEC_inflation.py', inflation_params, timeout=1200)
# Execute BCRA_exchangerate.py with an increased timeout
execute_script('BCRA_exchangerate.py', bcra_params, timeout=1200)