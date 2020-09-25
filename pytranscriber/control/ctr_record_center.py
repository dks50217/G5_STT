from pytranscriber.control.ctr_logger import Ctr_Logger
from pytranscriber.util.util import MyUtil
import configparser
import requests
import os
import sys
import root_path
ROOT_DIR = os.path.abspath(os.curdir)
Initfile = os.path.join(root_path.path, 'Config.ini')
config = configparser.ConfigParser()
config.read(Initfile,encoding="utf-8")

class Ctr_Record_Center():
    """
    Class for download G5RecordCenter audio(WAV) into STT temp Folder
    """
    def __init__(self,sourcePath):
        self.api_path = config['api']['G5RecordCenter']
        self.temp_path = config['path']['TempFolder']
        self.allow_temp_file = config['owner']['allowTempFile']
        self.source_path = sourcePath
        self.logger = Ctr_Logger()

    def downloadAudio(self):
        try:
            file_head,file_name = MyUtil.getfileInfo(self.source_path)

            api_url = "{0}?FileName={1}&FilePath={2}".format(
                self.api_path,
                file_name,
                self.source_path
            )
            
            self.logger.logInfo("downloading {0} from G5RecordCenter".format(file_name))

            self.final_path = self.temp_path + file_name

            doc = requests.get(api_url)

            if(doc.status_code == 200):
                 with open(self.final_path, 'wb') as f:
                    f.write(doc.content)
            else:
                self.logger.logError("G5RecordCenter downloadAudio Error status_code:{0}".format(str(doc.status_code)))

            return self.final_path

        except Exception as e:
            self.logger.logError("G5RecordCenter downloadAudio Error:{0}".format(str(e)))
            return self.final_path

    def removeTempFile(self,source_path):
        try:
            if os.path.exists(source_path) and self.allow_temp_file == '0':
                os.remove(source_path)
        except Exception as e:
            self.logger.logError("G5RecordCenter __removeTempFile Error:{0}".format(str(e)))
            return None

   