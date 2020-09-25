import logging
import datetime
import configparser
import os
import sys
import root_path
ROOT_DIR = os.path.abspath(os.curdir)
Initfile = os.path.join(root_path.path, 'Config.ini')
config = configparser.ConfigParser()
config.read(Initfile,encoding="utf-8")

class Ctr_Logger():
    def __init__(self):  
        today = datetime.date.today()
        formatStr = '%(asctime)s %(levelname)s: %(message)s'
        logFileName = config['path']['LogFolder'] + str(today) + '.log'
        logging.basicConfig(level=logging.DEBUG, filename= logFileName, filemode='a', format=formatStr)
        #logging.info('Ctr_Logger __INIT__ | loggerFile: ' + logFileName)
               
    def logInfo(self,str):
        logging.info(str)
    def logError(self,str):
        logging.error(str)