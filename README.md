# pyTranscriberSTT

>由pyTranscriber加入連接DB、單元測試、設定檔，藉由設定檔中的AutoRun可開啟排程處理

### 加入功能簡述

1.可自動執行

2.藉由預存程序撈取欲轉換音檔(僅限MS SQL)

3.將兩個對話SRT檔轉換為合併JSON

4.紀錄處理log


### 引用
- [原專案/pyTranscriber](https://github.com/raryelcostasouza/pyTranscriber/)
- [語音辨識使用/google-speech-v2](https://github.com/gillesdemey/google-speech-v2) 
- [音檔轉換與時間戳記處理/Autosub](https://github.com/agermanidis/autosub) 
- [音檔轉換切割FLAC/FFmpeg](https://github.com/FFmpeg/FFmpeg)


### 安裝依賴套件

```cmd
pip3 install --user pyQt5
pip3 install --user autosub
pip3 install --user pyinstaller
```

### 如何執行?
```cmd
python main.py
```

### 編譯步驟

1.如果main.spec不在專案目錄內,加入編譯spec
```cmd
python -m PyInstaller --onefile main.py
```

2.main.spec 加入以下程式碼
```python
from PyInstaller.utils.hooks import copy_metadata
extra_files = copy_metadata('google-api-python-client')
datas= extra_files
```

3.如果找不到Google api套件
```cmd
pip install google-api-python-client
```

4.藉由main.spec產生執行檔
```cmd
python -m PyInstaller main.spec
```

5.main.exe即會出現在dist資料夾內

6.將Config.ini放入對應資料夾內

### 設定檔注意事項
FFmpeg路徑請與exe相同
DependenFolder = '\\192.XXX.X.XX\pyTranscriberSTT\ffmpeg.exe'

### 其它
autoSub 是執行 __init__.py 非 __init__-0.4.0.py

### License
GPL v3







