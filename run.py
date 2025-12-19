#!/usr/bin/env python3
"""
Run script for TUK-ConvoSearch
"""
import subprocess
import sys
import os

def run_application():
    """Run the FastAPI application"""
    print("Starting TUK-ConvoSearch...")
    print("Web interface: http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop\n")
    
    # Run the application
    subprocess.run([
        "uvicorn", 
        "app.web.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ])

if __name__ == "__main__":
    # Check if requirements are installed
    try:
        import fastapi
        import langchain
    except ImportError:
        print("Error: Requirements not installed.")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    run_application()