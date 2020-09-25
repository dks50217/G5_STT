import platform
import os
import subprocess
import socket
import requests

class MyUtil(object):
    @staticmethod
    def open_file(path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    @staticmethod
    def is_internet_connected():
        try:
            s = socket.create_connection(("www.google.com", 80), 2)
            s.close()
            return True
        except OSError:
            pass
        return False

    @staticmethod
    def percentage(currentval, maxval):
        return 100 * currentval / float(maxval)
    
    @staticmethod
    def getfileInfo(source_path):
        file_head,file_name = os.path.split(source_path)
        return file_head,file_name
    
