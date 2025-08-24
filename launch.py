# launch.py - Updated version with path handling
import os
import sys
import subprocess

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Add numpy compatibility before importing anything else
class NumpyCoreCompat:
    def __getattr__(self, name):
        try:
            import numpy as np
            if hasattr(np, 'core'):
                return getattr(np.core, name)
            return None
        except:
            return None

# Patch sys.modules for compatibility
sys.modules['numpy._core'] = NumpyCoreCompat()
sys.modules['numpy._core.multiarray'] = NumpyCoreCompat()
sys.modules['numpy._core.umath'] = NumpyCoreCompat()

# Now launch your actual application
if __name__ == "__main__":
    # Pass through all command line arguments
    subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--reload"] + sys.argv[1:])