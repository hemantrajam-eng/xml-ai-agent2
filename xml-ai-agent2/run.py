
import runpy
import sys
from pathlib import Path

# Add the project root to the system path
sys.path.append(str(Path(__file__).resolve().parent))

# Run the streamlit app as a module, or just point to the file
# Option A: using run_module (slightly more complex)
# runpy.run_module("ui.app", run_name="__main__", alter_sys=True) 

# Option B: Run the app using a subprocess call (simpler)
import subprocess
subprocess.run(["streamlit", "run", "ui/app.py"])