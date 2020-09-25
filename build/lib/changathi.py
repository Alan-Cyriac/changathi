import sys
import subprocess
import os

def start_server():
    try:
        # theproc = subprocess.Popen([sys.executable, "manage.py", "runserver"])
        # theproc.communicate()

        os.system('cmd /k "python manage.py runserver"')
    except :
        return "please call download_model()"


def download_model():
    return "Downloading ..."