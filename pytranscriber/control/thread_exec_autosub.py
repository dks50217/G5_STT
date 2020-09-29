from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from pathlib import Path
from pytranscriber.util.srtparser import SRTParser
from pytranscriber.util.util import MyUtil
from pytranscriber.control.ctr_autosub import Ctr_Autosub
from pytranscriber.control.ctr_logger import Ctr_Logger
from pytranscriber.control.ctr_mssql import Ctr_MSSQL
import os
import configparser
import sys
import root_path
import datetime

ROOT_DIR = os.path.abspath(os.curdir)
Initfile = os.path.join(root_path.path, 'Config.ini')
config = configparser.ConfigParser()
config.read(Initfile,encoding="utf-8")
jsonList = []

class Thread_Exec_Autosub(QThread):
    signalLockGUI = pyqtSignal()
    signalResetGUIAfterCancel = pyqtSignal()
    signalResetGUIAfterSuccess = pyqtSignal()
    signalProgress = pyqtSignal(str, int)
    signalProgressFileYofN = pyqtSignal(str)
    signalErrorMsg = pyqtSignal(str)
    #20200916
    signalFinished = pyqtSignal(str)

    def __init__(self, objParamAutosub,audioList):
        self.objParamAutosub = objParamAutosub
        self._audioList = audioList
        self.running = True
        self.logger = Ctr_Logger()
        self._logAudioList = []
        self._logRCList = []
        self._removeSRTList = []
        QThread.__init__(self)

    def __updateProgressFileYofN(self, currentIndex, countFiles ):
        self.signalProgressFileYofN.emit("File " + str(currentIndex+1) + " of " +str(countFiles))

    def listenerProgress(self, string, percent):
        self.signalProgress.emit(string, percent)

    def __generatePathOutputFile(self, sourceFile):
        self.logger.logInfo("__generatePathOutputFile Start")
        
        try:
            #extract the filename without extension from the path
            base = os.path.basename(sourceFile)
            #[0] is filename, [1] is file extension
            fileName = os.path.splitext(base)[0]

            #the output file has same name as input file, located on output Folder
            #with extension .srt
            self.logger.logInfo("__generatePathOutputFile pathOutputFolder: " + str(self.objParamAutosub.outputFolder))
            pathOutputFolder = Path(self.objParamAutosub.outputFolder)
            outputFileSRT = pathOutputFolder / (fileName + ".srt")
            outputFileTXT = pathOutputFolder / (fileName + ".txt")
        except expression as e:
            self.logger.logError("__generatePathOutputFile Error: " + str(e))
            self.stop_thread()

        self.logger.logInfo("__generatePathOutputFile End outputFileSRT: " + str(outputFileSRT))
        return [outputFileSRT, outputFileTXT]

    def __runAutosubForMedia(self, index, langCode):
        self.logger.logInfo("__runAutosubForMedia")
        
        ctrSQL = Ctr_MSSQL()
        today = datetime.date.today()

        sourceFile = self.objParamAutosub.listFiles[index]

        #20200720 Michael 取代預設語言
        langCode = self.objParamAutosub.langCodeList[index]

        self.logger.logInfo("sourceFile:{0},langCode:{1},Index:{2}".format(str(sourceFile),str(langCode),str(index)))
        
        outputFiles = self.__generatePathOutputFile(sourceFile)
        outputFileSRT = outputFiles[0]
        outputFileTXT = outputFiles[1]

        #有VoiceMail代表有客戶專員通話 反之則是RC
        isRecord = 'VoiceMail' not in sourceFile

        self.logger.logInfo("Ctr_Autosub.generate_subtitles Start: OutPutFile: " + str(outputFileSRT))
        
        #20200926 加入付費Cloud API判斷
        stt_api_version = config['api']['GoogleAPI']
        fOutput = Ctr_Autosub.generate_subtitles(source_path = sourceFile,
                                output = outputFileSRT,
                                src_language = langCode,
                                listener_progress = self.listenerProgress,
                                stt_api_version = stt_api_version
                                )

        self.logger.logInfo("Ctr_Autosub.generate_subtitles End")

        #if nothing was returned
        if not fOutput:
            self.signalErrorMsg.emit("Error! Unable to generate subtitles for file " + sourceFile + ".")
        elif fOutput != -1:

            #一個音檔轉換為一個TXT檔案
            if config['owner']['allowTxt'] == '1':
                self.logger.logInfo('SRTParser.extractTextFromSRT: ' + str(outputFileSRT))
                SRTParser.extractTextFromSRT(str(outputFileSRT))                

            #不結合專員與客戶/RC SRT檔案，個別轉換為Json檔案
            if config['owner']['allowJson'] == '1':
                self.logger.logInfo('SRTParser.extractTextFromSRT: ' + str(outputFileSRT))
                SRTParser.parseSRTToJson(str(outputFileSRT),self._audioList[index])

            #結合員與客戶SRT檔案，合併成一個Json檔案
            if config['owner']['allowMerge'] == '1' and isRecord:
                if self.isEven(index) == True:
                    #用Srt檔名比對輸出資料夾SRT檔
                    jsonList.append(str(outputFileSRT))

                    head, tail = os.path.split(str(outputFileSRT))

                    _srtFileName = tail.replace('-out','')

                    _audioItem = next(item for item in self._audioList if item["SRTFileName"] == _srtFileName)
                   
                    self.logger.logInfo('MergeSRT: ' + _srtFileName)
 
                    SRTParser.parsePairSRTToJson(jsonList,_audioItem)

                    self._logAudioList.append(_audioItem)

                    #20200922 處理完insertCount筆就塞入DB
                    if len(self._logAudioList) >= int(config['owner']['insertCount']) and config['method']['IsDBLog'] == '1':
                        self.logger.logInfo('_logAudioList: ' + str(len(self._logAudioList)))
                        ctrSQL.BulkCopy(self._logAudioList,str(today))
                        self._logAudioList = []
                                               
                    jsonList.clear()
                else:
                    jsonList.append(str(outputFileSRT))
            
            #轉換一個留言成JSON檔案
            if config['owner']['allowRCJson'] == '1' and not isRecord:
                
                _srtFileName = self.getFileName(str(outputFileSRT))
                
                _audioItem = next(item for item in self._audioList if self.getFileName(item["SRTFileName"]) == _srtFileName)

                self.logger.logInfo('OneRCSRT: ' + _srtFileName)

                SRTParser.parseSRTToJson(str(outputFileSRT),_audioItem)

                self._logRCList.append(_audioItem)

            if self.objParamAutosub.boolOpenOutputFilesAuto:
                #open both SRT and TXT output files
                MyUtil.open_file(outputFileTXT)
                MyUtil.open_file(outputFileSRT)


            #addToRemoveSRTList
            self._removeSRTList.append(str(outputFileSRT))

            #updated the progress message
            self.listenerProgress("Finished", 100)


    def __loopSelectedFiles(self):
        
        #轉檔時間
        today = datetime.date.today()

        ctrSQL = Ctr_MSSQL()
        
        self.logger.logInfo("__loopSelectedFiles")
        
        self.signalLockGUI.emit()

        langCode = self.objParamAutosub.langCode

        #if output directory does not exist, creates it
        pathOutputFolder = Path(self.objParamAutosub.outputFolder)

    
        if not os.path.exists(pathOutputFolder):
            os.mkdir(pathOutputFolder)
        #if there the output file is not a directory
        if not os.path.isdir(pathOutputFolder):
            #force the user to select a different output directory
            self.signalErrorMsg.emit("路徑有誤")
        else:
            #go ahead with autosub process
            nFiles = len(self.objParamAutosub.listFiles)
            for i in range(nFiles):
                #does not continue the loop if user clicked cancel button
                if not Ctr_Autosub.is_operation_canceled():
                    self.__updateProgressFileYofN(i, nFiles)
                    self.__runAutosubForMedia(i, langCode)
            #if operation is canceled does not clear the file list
            if Ctr_Autosub.is_operation_canceled():
                self.signalResetGUIAfterCancel.emit()
            else:
                self.signalResetGUIAfterSuccess.emit()


        #寫入已完成Record(若還有剩下沒塞入DB者)
        if config['method']['IsDBLog'] == '1' and len(self._logAudioList) > 0:
            ctrSQL.BulkCopy(self._logAudioList,str(today))

        #寫入已完成RC
        if config['method']['IsRCLog'] == '1' and len(self._logRCList) > 0:
            ctrSQL.BulkCopy_RC(self._logRCList,str(today))
 
        #移除SRT
        if config['owner']['allowSRT'] == '0':
            self.removeSRTFile()

    def run(self):
        Ctr_Autosub.init()
        self.__loopSelectedFiles()
        self.running = False
        self.signalFinished.emit('Finished!! closeThread..')

    def cancel(self):
        Ctr_Autosub.cancel_operation()
    
    def isEven(self,num) -> bool:
        if (num % 2) != 0:
            return True
        else:
            return False
    def removeSRTFile(self):
        self.logger.logInfo('SRTParser.removeSRTFile: ' + str(len(self._removeSRTList)))  
        try:
            for srtPath in self._removeSRTList:
                os.remove(srtPath)
            self.logger.logInfo('SRTParser.removeSRTFile Success')
        except Exception as e:
            self.logger.logError('SRTParser.removeSRTFile Error: ' + str(e))
    def getFileName(self,path):
        head, filename = os.path.split(path)
        return filename



    
