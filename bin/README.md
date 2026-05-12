# Globus Manual Deployment Pipeline
This guide outlines the step-by-step process to deploy a Globus Compute function, wrap it in a Globus Flow, and schedule it using a Globus Timer.

## Prerequisites
1. **Environment:** You must run these commands from within your configured Apptainer container that has `globus-cli`, `globus-sdk`, and `globus-compute-sdk` installed.

```bash
apptainer run venv_globus_deploy.sif /bin/bash
```

2. **Compute Endpoint:** You need your target Compute Endpoint UUID ready.

---

## Step 1: Register the Compute Function

Globus Compute functions must be registered via Python. Create a small file named `register_function.py` with the following code:

```python
# register_function.py
from globus_compute_sdk import Client
from compute_functions import submit_monthly_update

gcc = Client()
func_uuid = gcc.register_function(submit_monthly_update)
print(f"Function ID: {func_uuid}")
```

Run the script to generate your Function ID:
```bash
python3 register_function.py
```


