import sys
import subprocess

def start_server():
    try:
        theproc = subprocess.Popen([sys.executable, "manage.py", "runserver"])
        theproc.communicate()
    except :
        return "please call download_model()"


def download_model():
    return "Downloading ..."