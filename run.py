import os
import sys
import subprocess

def main():
    print("Starting AgriTech AI with TensorFlow Engine...")
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "Scripts", "python.exe")
    
    # Fallback to system python if venv doesn't exist (though it will)
    if not os.path.exists(venv_python):
        venv_python = "python"
        
    try:
        subprocess.run([venv_python, "-m", "streamlit", "run", app_path])
    except KeyboardInterrupt:
        print("\nAgriTech AI stopped.")

if __name__ == "__main__":
    main()
