from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from pathlib import Path
from pytranscriber.model.param_autosub import Param_Autosub
from pytranscriber.util.util import MyUtil
from pytranscriber.control.thread_exec_autosub import Thread_Exec_Autosub
from pytranscriber.control.thread_cancel_autosub import Thread_Cancel_Autosub
from pytranscriber.control.ctr_record_center import Ctr_Record_Center
from pytranscriber.gui.gui import Ui_window
#Add by Michael
from os import walk
from os.path import join
import os
import re
import sys
import datetime
import configparser
import root_path
from pytranscriber.control.ctr_logger import Ctr_Logger
ROOT_DIR = os.path.abspath(os.curdir)
Initfile = os.path.join(root_path.path, 'Config.ini')
config = configparser.ConfigParser()
config.read(Initfile,encoding="utf-8")

class Ctr_Main():
    def __init__(self,audioList):
        app = QtWidgets.QApplication(sys.argv)
        window = QtWidgets.QMainWindow()
        self.objGUI = Ui_window()
        self.objGUI.setupUi(window)
        self._audioList = audioList
        self.logger = Ctr_Logger()
        self.__initGUI()
        if config['owner']['autoRun'] == '1':
            self.__listenerBExec()
        window.setFixedSize(window.size())
        window.show()
        sys.exit(app.exec_())

    def __initGUI(self):
        #language selection list
        #list_languages =  [ "en-US - English (United States)", "en-AU - English (Australia)", "en-CA - English (Canada)", "en-GB - English (United Kingdom)", "en-IN - English (India)", "en-GB - English (Ireland)", "en-NZ - English (New Zealand)", "en-PH - English (Philippines)","en-SG - English (Singapore)", "af - Afrikaans", "ar - Arabic", "az - Azerbaijani", "be - Belarusian", "bg - Bulgarian", "bn - Bengali", "bs - Bosnian", "ca - Catalan", "ceb -Cebuano", "cs - Czech", "cy - Welsh", "da - Danish", "de - German", "el - Greek", "eo - Esperanto", "es-AR - Spanish (Argentina)", "es-CL - Spanish (Chile)", "es-ES - Spanish (Spain)", "es-US - Spanish (United States)", "es-MX - Spanish (Mexico)", "et - Estonian", "eu - Basque", "fa - Persian", "fi - Finnish", "fr - French", "ga - Irish", "gl - Galician", "gu -Gujarati", "ha - Hausa", "hi - Hindi", "hmn - Hmong", "hr - Croatian", "ht Haitian Creole", "hu - Hungarian", "hy - Armenian", "id - Indonesian", "ig - Igbo", "is - Icelandic", "it - Italian", "iw - Hebrew", "ja - Japanese", "jw - Javanese", "ka - Georgian", "kk - Kazakh", "km - Khmer", "kn - Kannada", "ko - Korean", "la - Latin", "lo - Lao", "lt - Lithuanian", "lv - Latvian", "mg - Malagasy", "mi - Maori", "mk - Macedonian", "ml - Malayalam", "mn - Mongolian", "mr - Marathi", "ms - Malay", "mt - Maltese", "my - Myanmar (Burmese)", "ne - Nepali", "nl - Dutch", "no - Norwegian", "ny - Chichewa", "pa - Punjabi", "pl - Polish", "pt-BR - Portuguese (Brazil)", "pt-PT - Portuguese (Portugal)", "ro - Romanian", "ru - Russian", "si - Sinhala", "sk - Slovak", "sl - Slovenian", "so - Somali", "sq - Albanian", "sr - Serbian", "st - Sesotho", "su - Sudanese", "sv - Swedish", "sw - Swahili", "ta - Tamil", "te - Telugu", "tg - Tajik", "th - Thai", "tl - Filipino", "tr - Turkish", "uk - Ukrainian", "ur - Urdu", "uz - Uzbek", "vi - Vietnamese", "yi - Yiddish", "yo - Yoruba", "yue-Hant-HK - Cantonese (Traditional, HK)", "zh - Chinese (Simplified, China)", "zh-HK - Chinese (Simplified, Hong Kong)", "zh-TW - Chinese (Traditional, Taiwan)", "zu - Zulu" ]
        languageOption = int(config['owner']['language'].replace('\'',''))
        list_languages = ["zh-TW - Chinese (Traditional, Taiwan)","en-US - English (United States)"] 
        _audioList =[]
        _unExistList = []
        self.objGUI.cbSelectLang.addItems(list_languages)
        try:
            self.objGUI.cbSelectLang.setCurrentIndex(languageOption)
        except expression as identifier:
            self.objGUI.cbSelectLang.setCurrentIndex(0)

        self.__listenerProgress("", 0)
        #若MapPath為1代表絕對路徑
        userHome = Path.home()

        today = datetime.date.today()

        if config['path']['MapPath'] == '1':
            pathOutputFolder = config['path']['OutputFolder']
        else:
            pathOutputFolder = userHome /  config['path']['OutputFolder']
       
        pathOutputFolder = pathOutputFolder / str(today)

        if not os.path.exists(pathOutputFolder):
            self.logger.logInfo(str(pathOutputFolder) + ' not exist,creating..')
            os.makedirs(pathOutputFolder)
            
        self.objGUI.qleOutputFolder.setText(str(pathOutputFolder))

        self.objGUI.bRemoveFile.setEnabled(False)
        
        self.objGUI.bCancel.hide()

        #button listeners
        self.objGUI.bConvert.clicked.connect(self.__listenerBExec)
        self.objGUI.bCancel.clicked.connect(self.__listenerBCancel)
        self.objGUI.bRemoveFile.clicked.connect(self.__listenerBRemove)
        self.objGUI.bSelectOutputFolder.clicked.connect(self.__listenerBSelectOuputFolder)
        self.objGUI.bOpenOutputFolder.clicked.connect(self.__listenerBOpenOutputFolder)
        self.objGUI.bSelectMedia.clicked.connect(self.__listenerBSelectMedia)

        self.objGUI.actionLicense.triggered.connect(self.__listenerBLicense)
        self.objGUI.actionAbout_pyTranscriber.triggered.connect(self.__listenerBAboutpyTranscriber)


        #是否來自DB的路徑  (self._audioList 有CallID等資訊,_audioList則沒有)
        if config['method']['IsDBList'] == '1':
            for row in self._audioList:
                #_path = row.get('Path').replace('\\','/').replace('mp3','wav').replace('MP3','WAV')
                _path = row.get('Path').replace('mp3','wav').replace('MP3','WAV')
                _recordId = row.get('RecordId',0)

                #有in/out(專員客戶對話)
                if _recordId:
                    audioList,unExistList = self.__checkInOutExist(_path,_recordId)
                    _audioList.extend(audioList)
                    _unExistList.extend(unExistList)
                #rc留言
                else:
                    audioList_rc = self.__checkAudioExist(_path)
                    _audioList.extend(audioList_rc)

 
            self.logger.logInfo('existCnt: ' + str(len(_audioList)))
            self.logger.logInfo('nonExistCnt: ' + str(len(_unExistList)))

            if len(_audioList) == 0:
                self.logger.logInfo('no record pytranscriberSTT closing: ' + str(len(_audioList)))
                sys.exit()
        else:
            mypath = userHome / config['path']['InputFolder']
            for root, dirs, files in walk(mypath):
                for f in files:
                    fullpath = join(root, f)
                    _audioList.append(fullpath)

        #移除不存在清單內的AudioList
        self.__removeNotExitList(_unExistList)

        self.objGUI.qlwListFilesSelected.addItems(_audioList)
        self.objGUI.bConvert.setEnabled(True)
        self.objGUI.bRemoveFile.setEnabled(True)

    def __resetGUIAfterSuccess(self):
        self.__resetGUIAfterCancel()

        self.objGUI.qlwListFilesSelected.clear()
        self.objGUI.bConvert.setEnabled(False)
        self.objGUI.bRemoveFile.setEnabled(False)

    def __resetGUIAfterCancel(self):

        self.__resetProgressBar()

        self.objGUI.bSelectMedia.setEnabled(True)
        self.objGUI.bSelectOutputFolder.setEnabled(True)
        self.objGUI.cbSelectLang.setEnabled(True)
        self.objGUI.chbxOpenOutputFilesAuto.setEnabled(True)

        self.objGUI.bCancel.hide()
        self.objGUI.bConvert.setEnabled(True)
        self.objGUI.bRemoveFile.setEnabled(True)

    def __lockButtonsDuringOperation(self):
        self.objGUI.bConvert.setEnabled(False)
        self.objGUI.bRemoveFile.setEnabled(False)
        self.objGUI.bSelectMedia.setEnabled(False)
        self.objGUI.bSelectOutputFolder.setEnabled(False)
        self.objGUI.cbSelectLang.setEnabled(False)
        self.objGUI.chbxOpenOutputFilesAuto.setEnabled(False)
        QtCore.QCoreApplication.processEvents()

    def __listenerProgress(self, str, percent):
        self.objGUI.labelCurrentOperation.setText(str)
        self.objGUI.progressBar.setProperty("value", percent)
        QtCore.QCoreApplication.processEvents()

    def __setProgressBarIndefinite(self):
        self.objGUI.progressBar.setMinimum(0)
        self.objGUI.progressBar.setMaximum(0)
        self.objGUI.progressBar.setValue(0)

    def __resetProgressBar(self):
        self.objGUI.progressBar.setMinimum(0)
        self.objGUI.progressBar.setMaximum(100)
        self.objGUI.progressBar.setValue(0)
        self.__listenerProgress("", 0)

    def __updateProgressFileYofN(self, str):
        self.objGUI.labelProgressFileIndex.setText(str)
        QtCore.QCoreApplication.processEvents()

    def __listenerBSelectOuputFolder(self):
        fSelectDir = QFileDialog.getExistingDirectory(self.objGUI.centralwidget)
        if fSelectDir:
            self.objGUI.qleOutputFolder.setText(fSelectDir)

    def __listenerBSelectMedia(self):
        #options = QFileDialog.Options()
        options = QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self.objGUI.centralwidget, "選擇音檔", "","All Media Files (*.mp3 *.mp4 *.wav *.m4a *.wma)")

        if files:
            self.objGUI.qlwListFilesSelected.addItems(files)
            
            #enable the convert button only if list of files is not empty
            self.objGUI.bConvert.setEnabled(True)
            self.objGUI.bRemoveFile.setEnabled(True)


    def __listenerBExec(self):
        if not MyUtil.is_internet_connected():
            self.__showErrorMessage("必須要有網路連線!")
        else:
            #extracts the two letter lang_code from the string on language selection
            self.logger.logInfo('start STT')
            
            selectedLanguage = self.objGUI.cbSelectLang.currentText()
            indexSpace = selectedLanguage.index(" ")
            langCode = selectedLanguage[:indexSpace]

            #20200720 Michael，根據self._audioList 判斷語系
            listFiles = []
            langCodeList = []
            for i in range(self.objGUI.qlwListFilesSelected.count()):
                filePath = str(self.objGUI.qlwListFilesSelected.item(i).text()) 
                listFiles.append(filePath)
            for i in self._audioList:
                _recordId = i.get('RecordId',0)
                _locale = i.get('Locale',langCode)
                if _recordId:#in/out
                    langCodeList.append(_locale)
                    langCodeList.append(_locale)
                else:
                    langCodeList.append(_locale)


            outputFolder = self.objGUI.qleOutputFolder.text()

            if self.objGUI.chbxOpenOutputFilesAuto.checkState() == Qt.Checked:
                boolOpenOutputFilesAuto = True
            else:
                boolOpenOutputFilesAuto = False

            #boolOpenOutputFilesAuto = False

            objParamAutosub = Param_Autosub(listFiles, outputFolder, langCode,
                                            boolOpenOutputFilesAuto,langCodeList)

            #execute the main process in separate thread to avoid gui lock
            self.thread_exec = Thread_Exec_Autosub(objParamAutosub,self._audioList)

            #connect signals from work thread to gui controls
            self.thread_exec.signalLockGUI.connect(self.__lockButtonsDuringOperation)
            self.thread_exec.signalResetGUIAfterSuccess.connect(self.__resetGUIAfterSuccess)
            self.thread_exec.signalResetGUIAfterCancel.connect(self.__resetGUIAfterCancel)
            self.thread_exec.signalProgress.connect(self.__listenerProgress)
            self.thread_exec.signalProgressFileYofN.connect(self.__updateProgressFileYofN)
            self.thread_exec.signalErrorMsg.connect(self.__showErrorMessage)
            #Michael 20200916
            self.thread_exec.signalFinished.connect(self.__finishProcess)

            self.thread_exec.start()

            #Show the cancel button
            self.objGUI.bCancel.show()
            self.objGUI.bCancel.setEnabled(True)

    def __listenerBCancel(self):
        self.objGUI.bCancel.setEnabled(False)
        self.thread_cancel = Thread_Cancel_Autosub(self.thread_exec)

        #Only if worker thread is running
        if self.thread_exec and self.thread_exec.isRunning():
            #reset progress indicator
            self.__listenerProgress("Cancelling", 0)
            self.__setProgressBarIndefinite()
            self.__updateProgressFileYofN("")

            #connect the terminate signal to resetGUI
            self.thread_cancel.signalTerminated.connect(self.__resetGUIAfterCancel)
            #run the cancel autosub operation in new thread
            #to avoid progressbar freezing
            self.thread_cancel.start()
            self.thread_exec = None

    def __listenerBRemove(self):
        indexSelected = self.objGUI.qlwListFilesSelected.currentRow()
        if indexSelected >= 0:
            self.objGUI.qlwListFilesSelected.takeItem(indexSelected)

        #if no items left disables the remove and convert button
        if self.objGUI.qlwListFilesSelected.count() == 0:
            self.objGUI.bRemoveFile.setEnabled(False)
            self.objGUI.bConvert.setEnabled(False)

    def __listenerBOpenOutputFolder(self):
        pathOutputFolder = Path(self.objGUI.qleOutputFolder.text())

        #if folder exists and is valid directory
        if os.path.exists(pathOutputFolder) and os.path.isdir(pathOutputFolder):
            MyUtil.open_file(pathOutputFolder)
        else:
            self.__showErrorMessage("Error! Invalid output folder.")

    def __listenerBLicense(self):
        self.__showInfoMessage("<html><body><a href=\"https://www.gnu.org/licenses/gpl-3.0.html\">GPL License</a><br><br>"
                + "Copyright (C) 2019 Raryel C. Souza <raryel.costa at gmail.com><br>"
                + "<br>This program is free software: you can redistribute it and/or modify<br>"
                + "it under the terms of the GNU General Public License as published by<br>"
                + "the Free Software Foundation, either version 3 of the License, or<br>"
                + " any later version<br>"
                + "<br>"
                + "This program is distributed in the hope that it will be useful,<br>"
                + "but WITHOUT ANY WARRANTY; without even the implied warranty of<br>"
                + "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the<br>"
                + "GNU General Public License for more details.<br>"
                + "<br>"
                + "You should have received a copy of the GNU General Public License<br>"
                + "along with this program.  If not, see <a href=\"https://www.gnu.org/licenses\">www.gnu.org/licenses</a>."
                + "</body></html>", "License")

    def __listenerBAboutpyTranscriber(self):
        self.__showInfoMessage("<html><body>"
                + "<a href=\"https://github.com/raryelcostasouza/pyTranscriber\">pyTranscriber</a> is an application that can be used "
                + "to generate <b>automatic transcription / automatic subtitles </b>"
                + "for audio/video files through a friendly graphical user interface. "
                +"<br><br>"
                + "The hard work of speech recognition is made by the <a href=\"https://cloud.google.com/speech/\">Google Speech Recognition API</a> "
                + "using <a href=\"https://github.com/agermanidis/autosub\">Autosub</a>"
                + "</body></html>", "About pyTranscriber")


    def __showInfoMessage(self, info_msg, title):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setWindowTitle(title)
        msg.setText(info_msg)
        msg.exec()

    def __showErrorMessage(self, errorMsg):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)

        msg.setWindowTitle("Error!")
        msg.setText(errorMsg)
        msg.exec()

    def __checkInOutExist(self,path,recordID):
        """
        檢查成對才會撈進 existFileList (必須同時有out & in)
        """
        ExtList = ['-in','-out']
        existFileList = []
        unExistFileList = []
        try:
            for extItem in ExtList:
                
                _oFile = self.__appendInOutBeforeExt(path,extItem)

                #如果來自雲端，必須先下載，下載後傳回下載路徑
                if 'g5-file' in _oFile:
                    exec_g5RecordCenter = Ctr_Record_Center(_oFile)
                    _oFile = exec_g5RecordCenter.downloadAudio()

                #是否有權限讀取資料夾
                _accessFlag = os.access(_oFile,os.F_OK)  
                self.logger.logInfo('File: ' + _oFile + ' Access: ' + str(_accessFlag))
                
                if os.path.exists(_oFile) == True:
                    existFileList.append(_oFile)
                else:
                    #傳回不存在的檔,並刪除存在list的(-in)，因為必須要成對才能轉換
                    if recordID not in unExistFileList:
                        unExistFileList.append(recordID)

                    _pairWavRemove = _oFile.replace(ExtList[1],ExtList[0])  
                     
                    if _pairWavRemove in existFileList:
                        existFileList.remove(_pairWavRemove)

        except Exception as e:
            self.logger.logError('__checkInOutExist error' + str(e))
        
        return existFileList,unExistFileList
    #RC
    def __checkAudioExist(self,path):  
        existFileList = []
        try:
            _accessFlag = os.access(path,os.F_OK)
            self.logger.logInfo('File: ' + path + ' Access: ' + str(_accessFlag))
            if os.path.exists(path) == True:
                existFileList.append(path)
        except Exception as e:
            self.logger.logError('__checkAudioExist error' + str(e))

        return existFileList
        
    def __appendInOutBeforeExt(self,filename,oStr) -> 'str':
        parts = filename.rfind(".")
        return filename[:parts] + oStr + "." + filename[parts+1:]
    
    def __removeNotExitList(self,notExitList):   
        for index, item in enumerate(self._audioList):
            RecordID = item.get('RecordId',0)
            if RecordID in notExitList:
               del self._audioList[index]
    #Michael 連接執行緒關閉 / 刪除暫存
    def __finishProcess(self,finishedMsg):
        temp_path = config['path']['TempFolder']
        
        try:
            if config['owner']['allowTempFile'] == '0':
                self.logger.logInfo("start to remove temp folder files")
                for root, dirs, files in os.walk(temp_path):
                    for file in files:
                        remove_file = os.path.join(root, file)
                        os.remove(remove_file)
                        self.logger.logInfo("file removed:" + str(remove_file))
        except Exception as e:
            self.logger.logError('remove file error' + str(e))

        self.logger.logInfo(finishedMsg)

        sys.exit()
        
        

        

