import sys
import os

# Add the root directory to the python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Run the main Streamlit application
from frontend.streamlit_app import main

if __name__ == "__main__":
    main()
