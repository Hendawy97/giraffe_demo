#!/usr/bin/env python3
"""
Development server runner script.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run the development server with hot reload."""
    
    # Ensure we're in the right directory
    backend_dir = Path(__file__).parent.parent
    src_dir = backend_dir / "src"
    
    # Add src directory to Python path
    sys.path.insert(0, str(src_dir))
    
    # Run uvicorn with hot reload
    cmd = [
        "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
        "--reload-dir", str(src_dir),
        "--log-level", "info",
    ]
    
    print(f"Starting development server...")
    print(f"Command: {' '.join(cmd)}")
    print(f"Working directory: {backend_dir}")
    print(f"API docs will be available at: http://localhost:8000/docs")
    print(f"Health check: http://localhost:8000/health")
    
    try:
        subprocess.run(cmd, cwd=backend_dir, check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Server failed with exit code {e.returncode}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()