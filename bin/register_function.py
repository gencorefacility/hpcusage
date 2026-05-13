# register_function.py
from globus_compute_sdk import Client

def submit_monthly_update():
    import subprocess
    import os
    import datetime

    # Check if today is the 1st of the month
    if datetime.datetime.today().day != 1:
        return {"status": "skipped", "message": "Not the 1st of the month."}
    
    netid = "gencore"
    script_dir = f"/home/{netid}/_admin/hpcusage/bin"
    update_script = os.path.join(script_dir, "update_csv.py")

    cmd = [
        "/opt/slurm/bin/sbatch",
        "-N1",
        "--output=/dev/null",
        "--error=/dev/null",
        "--job-name=MONTHLY_UPDATE",
        "--time=02:00:00", 
        f"--wrap=python3 {update_script}"
    ]

    try:
        result = subprocess.run(cmd, cwd=script_dir, capture_output=True, text=True, check=True)
        return {"status": "success", "job_id": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "stderr": e.stderr}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ---------------------------------------------------------
# REGISTRATION LOGIC
# ---------------------------------------------------------
if __name__ == "__main__":
    print("Connecting to Globus Compute...")
    gcc = Client()

    print("Registering function...")
    # This packages the function and its internal imports as a single payload
    func_uuid = gcc.register_function(submit_monthly_update)

    print("\n✅ Registration Successful!")
    print(f"Function ID: {func_uuid}")
    print("\nCopy this Function ID and paste it into your flow_def.json file.")
