import subprocess

years = [2024] 
months = [1,2,3] 

for y in years:
    for m in months:
        subprocess.run(["python3", "run_connectivity_simulation_subprocess.py", "--year", str(y), "--month", str(m)],
    	stdout=open(f"out_{y}_{m:02d}.log", "w"),
    	stderr=open(f"err_{y}_{m:02d}.log", "w")
)


