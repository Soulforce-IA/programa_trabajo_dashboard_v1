import subprocess
import sys
import os

def main():
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    dashboard_path = os.path.join(base_dir, "app.py")

    # Lanza Streamlit en un proceso separado (no bloquea)
    subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            dashboard_path,
            "--server.port=8501",
            "--browser.gatherUsageStats=false",
            "--server.headless=true"
        ],
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    )

if __name__ == "__main__":
    main()