#部屬前測試

import unittest
import os
import configparser
import root_path
import datetime
from pytranscriber.util.srtparser import SRTParser
from pytranscriber.util.util import MyUtil

Initfile = os.path.join(root_path.path, 'Config.ini')
config = configparser.ConfigParser()
config.read(Initfile,encoding="utf-8")


class Tester(unittest.TestCase):
    def test_basePath(self):    
        # user = userhome = os.path.expanduser('~')
        # print(user)
        base_path_key = 'adm'
        self.assertTrue(base_path_key in root_path.path,"基底路徑有誤")
    def test_OutputFolder(self):
        path = config['path']['OutputFolder']   
        self.assertTrue(os.access(path,os.F_OK),"Json輸出不存在")
        self.assertTrue(os.access(path,os.R_OK),"Json輸出不可讀")
        self.assertTrue(os.access(path,os.W_OK),"Json輸出不可寫")
    def test_LogFolder(self):
        path = config['path']['LogFolder']
        self.assertTrue(os.access(path,os.F_OK),"log資料夾不存在")
        self.assertTrue(os.access(path,os.R_OK),"log資料夾不可讀")
        self.assertTrue(os.access(path,os.W_OK),"log資料夾不可寫")
    def test_TempFolder(self):
        path = config['path']['TempFolder']
        self.assertTrue(os.access(path,os.F_OK),"temp資料夾不存在")
        self.assertTrue(os.access(path,os.R_OK),"temp資料夾不可讀")
        self.assertTrue(os.access(path,os.W_OK),"temp資料夾不可寫")
    def test_DependenFolder(self):
        path = config['path']['DependenFolder']
        self.assertTrue(os.access(path,os.F_OK),"必存在套件不存在")
        self.assertTrue(os.access(path,os.R_OK),"必存在套件不可讀")
    def test_DBConnect(self):
        connStr = config['path']['ConnStr']
        self.assertTrue("tecs" in connStr,"必須是tecs權限")
        self.assertTrue("G5_STT" in connStr,"必須是G5_STT資料庫")
    def test_SP(self):
        sp_name = config['path']['QuerySPName']
        self.assertTrue("s_QueryG5Record" in sp_name,"檢查SP名稱")
    def test_SRTParser(self):
        test_insert = SRTParser.dotInsert('123',1)
        self.assertEqual(test_insert,'0.123',"dotInsert Fail")
        test_unsort = [{'sortkey':2,'name':'test2'},{'sortkey':1,'name':'test1'},{'sortkey':3,'name':'test3'}]
        test_sorted = [{'sortkey':1,'name':'test1'},{'sortkey':2,'name':'test2'},{'sortkey':3,'name':'test3'}]
    def test_ffmpeg(self):
        test_command = ['\\192.168.0.11\\adm\\pyTranscriberSTT\\ffmpeg.exe', 
                        '-y', '-i', 
                        '//192.168.1.35/g5/Recording/wav/pbx-g5-dradvice.telexpress.com/20200709/30003/g51011a5731257.20200709114040595-out.wav', 
                        '-ac', '1', '-ar', '16000', '-loglevel', 'error',
                         'C:\\Users\\SQLADM~1\\AppData\\Local\\Temp\\tmpdtkapa_y.wav']
    def test_spec(self):
        test_meta = "extra_files = copy_metadata('google-api-python-client')" 
    def test_API(self):
        self.assertTrue(MyUtil.is_internet_connected(),"Google API連接失敗")
        
    
if __name__ == '__main__':
    unittest.main()