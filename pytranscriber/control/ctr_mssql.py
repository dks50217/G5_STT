from pytranscriber.control.ctr_logger import Ctr_Logger
import configparser
import pyodbc
import os
import sys
import root_path
ROOT_DIR = os.path.abspath(os.curdir)
Initfile = os.path.join(root_path.path, 'Config.ini')
config = configparser.ConfigParser()
config.read(Initfile,encoding="utf-8")

class Ctr_MSSQL():
    def __init__(self):
        self.conn_str  = (config['path']['ConnStr'].replace('\'','',2))
        self.logger = Ctr_Logger()
        self.logger.logInfo('__INIT__ Ctr_MSSQL')
    def GetG5AudioList(self):
        resultList = []
        if config['method']['IsDBList'] == '1':
            self.logger.logInfo('GetG5AudioList')
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            cmd_prod_executesp = 'EXEC ' + config['path']['QuerySPName']
            conn.autocommit = True
            try:
                cursor.execute(cmd_prod_executesp)
                column_names_list = [x[0] for x in cursor.description]
                resultList = [dict(zip(column_names_list, row)) for row in cursor.fetchall()]
                return resultList
            except Exception as ex:
                self.logger.logError('錯誤 !!!!! %s' % ex)
            cursor.close()
            del cursor
        else:
            return resultList
    def InsertLog(self,errorList):
        self.logger.logInfo('InsertTransLog')
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cmd_prod_executesp = config['path']['InsertSPName']
        conn.autocommit = True
        try:
            sql = """\
            EXEC cmd_prod_executesp @JsonCount=?, @CallDetailID=?
            """
            params = ('1234','123')
            cursor.execute(sql)
            del cursor
            return resultList
        except Exception as ex:
            self.logger.logError('錯誤 !!!!! %s' % ex)
    def BulkCopy(self,transcribedList,folderDate):
        self.logger.logInfo('BulkCopy Start')
        bulkList = []
        for row in transcribedList:
            _recordFileName = row.get('RecordFileName',0).replace('.wav','.json')
            _path = config['path']['OutputFolder'] + folderDate + "\\"          
                       
            bulkList.append((
                row.get('RecordId'),
                row.get('CallLogId'),
                row.get('CallDetailId'),
                _recordFileName,
                _path
            ))

       
        self.logger.logInfo('BulkCopy Cnt:' + str(len(bulkList)))
        
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.executemany('INSERT INTO [Transcribed] (RecordID,CalllogID,CallDetailID,FileName,Path) VALUES (?,?,?,?,?)', bulkList)
        cursor.commit()
        cursor.close()
        del cursor

        self.logger.logInfo('BulkCopy Success: ' + str(len(bulkList)))
    def BulkUpdate(self,unTranscribedList):
        self.logger.logInfo('BulkUpdate Start')
        unbulkList = []
    def BulkCopy_RC(self,transcribedList,folderDate):
        self.logger.logInfo('BulkCopy_RC Start')
        bulkList = []
        for row in transcribedList:
            _path = config['path']['OutputFolder'] + folderDate + "\\"          
            bulkList.append((
                row.get('MessageID'),
                row.get('MessageID') + '.json',
                _path
            ))

        self.logger.logInfo('BulkCopy_RC Cnt:' + str(len(bulkList)))
        
        conn = pyodbc.connect(self.conn_str)
        cursor = conn.cursor()
        cursor.executemany('INSERT INTO [Transcribed_RC] (MessageID,FileName,Path) VALUES (?,?,?)', bulkList)
        cursor.commit()
        cursor.close()
        del cursor

        self.logger.logInfo('BulkCopy_RC Success: ' + str(len(bulkList)))

    
        
    