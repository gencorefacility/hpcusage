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

**Copy the Function ID output. You will need it for the next step.**

---

## Step 2: Create the Flow Definition
Create a file named `flow_def.json`. Replace `YOUR_ENDPOINT_ID` and `YOUR_FUNCTION_ID` with your actual UUIDs.
```json
{
  "StartAt": "RunPythonScript",
  "States": {
    "RunPythonScript": {
      "End": true,
      "Type": "Action",
      "ActionUrl": "https://compute.actions.globus.org",
      "Parameters": {
        "endpoint": "YOUR_ENDPOINT_ID",
        "function": "YOUR_FUNCTION_ID"
      },
      "ResultPath": "$.Result"
    }
  }
}
```
---

## Step 3: Deploy the Flow
Use the Globus CLI to create the flow based on your JSON definition.

```bash
globus flows create "Monthly Update Flow" flow_def.json
```

**Look at the JSON output and copy the `id` (this is your Flow ID).**

---

## Step 4: Grant Timer Consent

Before you can schedule a timer, you must explicitly grant the Globus Timer service permission to execute your specific Flow.

Run this command, replacing `YOUR_FLOW_ID` with the ID from Step 3:
```bash
globus login --no-local-server --timer flow:YOUR_FLOW_ID
```
1. Open the generated URL in your web browser.
2. Log in and check the consent boxes.
3. Copy the authorization code, paste it back into your terminal, and hit Enter.

---

## Step 5: Schedule the Timer

Now that the Timer service has permission, you can schedule the automation. Run the following command (replace YOUR_FLOW_ID with your actual ID):

```bash
globus timer create flow YOUR_FLOW_ID --name "Daily Check for Monthly Update" --interval 1d --start "2026-05-12T06:00:00Z"
```

If successful, the CLI will output a Timer ID. Your pipeline is now live and will execute on the defined schedule.

**Updating the Pipeline Later**

If you update your Python code in the future, you do not need to recreate the Timer or the Flow. Just do the following:

1. Re-run `register_function.py` to get a new Function ID.
2. Update `flow_def.json` with the new Function ID.
3. Run `globus flows update YOUR_FLOW_ID flow_def.json`.












