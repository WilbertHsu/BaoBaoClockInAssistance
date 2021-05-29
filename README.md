# BaoBaoClockInAssistance (寶寶懶得上線打卡)
寶寶心裡苦，但寶寶要等三個禮拜才會說。  
  
### Step 0
安裝 Python，目前只測過 Python 3.9.4。  
* `Add Python xxx to PATH` 記得選。  
  
### Step 1
寶寶有擋 PIP server，我想你知道該怎麼做  
`pip install -r PipRequirements.txt`  
  
### Step 2
把 `Configuration.ini` 的每一個格子填好。  
* 可參考 Configuration_Sample.ini 或以內部寶寶信箱來信洽詢。  
  
#### Step 2.1
Account  = 帳號  
Password = 密碼  
Domain   = VPN Domain  
Email    = E-Mail 地址  
VpnName  = 自訂的 VPN 名稱 (英文 only，不要空格，不要特殊字元)  
  
ClockInServer  = 打卡網站  
ExchangeServer = E-Mail Server  
VpnTestServer1 = 用來測試 VPN 連線的 server #1  
VpnTestServer2 = 用來測試 VPN 連線的 server #2  
VpnTestServer3 = 用來測試 VPN 連線的 server #3  
  
BotToken = Token from BotFather  
ChatID   = Telegram 的 User ID  
![image](https://github.com/WilbertHsu/BaoBaoClockInAssistance/blob/main/img/TelegramBotAndId.png)  
  
### Step 3
把寶寶餵給你吃的 VPN 連線檔複製一份到這裡。  
把檔案名稱改成自訂的 VPN 名稱。  
再用文字編輯器打開 VPN 連線檔 (*.PBK) 把第一行改成自訂的 VPN 名稱。  
![image](https://github.com/WilbertHsu/BaoBaoClockInAssistance/blob/main/img/ChangePkbName.png)  
  
### Step 4
建立 Selenium 環境，目前用的是 Portable Edge (Chromium) 喜歡用其它瀏覽器的寶寶可以自行修改。  
* 注意版本一致性  
![image](https://github.com/WilbertHsu/BaoBaoClockInAssistance/blob/main/img/SetupSelenium.png)  
  
#### Step 4.1
找微軟拿 Microsoft Edge Driver  
[Link to Microsoft Edge Driver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)  
  
#### Step 4.2
下載 Portable Edge (Chromium)  
[Link to PorEdgeUpd by UndertakerBen](https://github.com/UndertakerBen/PorEdgeUpd/releases)  
  
#### Step 4.3
把前兩步的東西放到對的地方，目錄結構參考：  
![image](https://github.com/WilbertHsu/BaoBaoClockInAssistance/blob/main/img/FolderStruct.png)  


### Step 5
用文字編輯器打開 BaoBaoClockInAssistance.py 改一下打卡時間。  
* 至少改一下 end_date  
![image](https://github.com/WilbertHsu/BaoBaoClockInAssistance/blob/main/img/ChnageClockInSchedule.png)  
  
### Step 6
`python BaoBaoClockInAssistance.py`  
  
### TA-DA
![image](https://github.com/WilbertHsu/BaoBaoClockInAssistance/blob/main/img/TelegramClockInResult.jpg)  
