# pyTranscriberSTT

>由pyTranscriber加入連接DB、單元測試、設定檔，藉由設定檔中的AutoRun可開啟排程處理

### 加入功能簡述

1.可自動執行

2.藉由預存程序撈取欲轉換音檔(僅限MS SQL)

3.將兩個對話SRT檔轉換為合併JSON

4.紀錄處理log

5.雲端STT API

6.下載音檔

7.拆解改用auditok


### 引用
- [原專案/pyTranscriber](https://github.com/raryelcostasouza/pyTranscriber/)
- [語音辨識使用/google-speech-v2](https://github.com/gillesdemey/google-speech-v2) 
- [語音辨識使用2/google_cloud](https://cloud.google.com/speech-to-text/docs)
- [音檔轉換與時間戳記處理/Autosub](https://github.com/agermanidis/autosub) 
- [音檔轉換切割FLAC/FFmpeg](https://github.com/FFmpeg/FFmpeg)
- [判斷音檔時間軸/auditok](https://github.com/amsehili/auditok)


### 安裝依賴套件 (只需做一次)

>先執行
```cmd
pip3 install --user pyQt5
pip3 install --user autosub
pip3 install --user pyinstaller
pip install configparser
pip install pyodbc
pip install forked-auditok-split-without-data
```

### 如何執行?
```cmd
python main.py
```

>若失敗
```cmd
pip3 install -r requirements.txt
```
>若失敗多次，根據error message去載套件

### 編譯步驟

1.將root_path.py的path變更Config.ini讀取的路徑，要與exe存放點相同

2.如果main.spec不在專案目錄內,加入編譯spec (只需做一次)
```cmd
python -m PyInstaller --onefile main.py
```

3.main.spec 加入以下程式碼 (只需做一次)
```python
from PyInstaller.utils.hooks import copy_metadata
from PyInstaller.utils.hooks import collect_data_files
extra_files = copy_metadata('google-api-python-client')
extra_files+= copy_metadata('google-cloud-speech')
extra_files+= collect_data_files('grpc')
```

4.如果找不到Google api套件 (只需做一次)

> 免費版
```cmd
pip install google-api-python-client
```
> 付費版
```cmd
pip install google-cloud-speech
pip install google-cloud-core
```


5.藉由main.spec產生執行檔
```cmd
python -m PyInstaller main.spec
```

6.main.exe即會出現在dist資料夾內

7.將Config.ini放入對應資料夾內


### 設定檔注意事項
FFmpeg路徑請與exe相同
DependenFolder = '\\192.XXX.X.XX\pyTranscriberSTT\ffmpeg.exe'

## 若要使用雲端STT API
至GCP的API憑證和服務申請憑證，並新增服務帳戶，下載Json，格式如下
將檔案放置Config中指定位置

```json
{
  "type": "service_account",
  "project_id": "{your project_id}",
  "private_key_id": "{your private_key_id}",
  "private_key": "-----BEGIN PRIVATE KEY-----\n{your private_key}\n-----END PRIVATE KEY-----\n",
  "client_email": "{your client_email}",
  "client_id": "{your client_id}",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "{your client_x509_cert_url}"
}
```

### 其它
1.autoSub 是執行 __init__.py 非 __init__-0.4.0.py

2.因為有多執行緒,有設定一核跑幾個 cpus的設定目前只有傳給google時依據電腦幾核心決定,切割FLAC目前還是寫死為1,因防毒會讓CPU升高(詳情可見ctr_autosub.py)

### License
GPL v3







