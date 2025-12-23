import subprocess
import os
import sys

def run_streamlit():
    #Obtiene la ruta del script de streamlit
    script_path = os.path.join(os.path.dirname(__file__), "app.py")

    #ejecuta la app de streamlit
    subprocess.run(["streamlit","run",script_path])


if __name__ == "__main__":
    run_streamlit()