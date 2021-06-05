import datetime
import pathlib
import sys
import time
import configparser
import random
import string
import io

# Selenium.
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from msedge.selenium_tools import Edge, EdgeOptions

# Notify user and get MOTP number from user.
import telepot
from telepot.loop import MessageLoop

# Mail the result.
from exchangelib import Account, Credentials, Message, Mailbox, FileAttachment, DELEGATE, Configuration

# Schedule clock in process.
# from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

# RecovertVPN
from RecoveryVpnWithPy import RecoverVpnConnection

# Current working path.
PathOfCurrent = pathlib.Path(__file__).parent.absolute()

#
# Parse Configuration.ini
#
PrivateConfig = configparser.ConfigParser()
PrivateConfig.read('Configuration.ini')

MotpGettingOption = PrivateConfig['Options']['GetMotpNumberBy']

# Telegram parameters.
TelegramNotifySwitch = int(PrivateConfig['Telegram']['EnableTelegramNotify'])
FixedChatID = PrivateConfig['Telegram']['ChatID']
TelegramBot = telepot.Bot(PrivateConfig['Telegram']['BotToken'])
StopTelepotBot = False

# User settings
UserName = PrivateConfig['Uesr']['Account']
UserPassword = PrivateConfig['Uesr']['Password']
UserVpnName = PrivateConfig['Uesr']['VpnName']
UserDomain = PrivateConfig['Uesr']['Domain']

# VPN settings
VpnTestServer1 = PrivateConfig['Server']['VpnTestServer1']
VpnTestServer2 = PrivateConfig['Server']['VpnTestServer2']
VpnTestServer3 = PrivateConfig['Server']['VpnTestServer3']

# Email settings
EmailNotifySwitch = int(PrivateConfig['Mail']['EnableEmailNotify'])
UserMailAddress = PrivateConfig['Mail']['Email']
UserMailServer = PrivateConfig['Mail']['ExchangeServer']

# Clock in server
ClockInServer = PrivateConfig['Server']['ClockInServer']

# How many times of VPN retry.
VpnRetryLimit = 10


# Recover VPN connection by using RecoveryVpnWithPy
def RecoverVpn(UserMotpNum):
  print("[Action] Trying to recover VPN.")
  # Using the MOTP number to recover the VPN.
  Status = RecoverVpnConnection(UserVpnName, UserName, UserPassword, UserMotpNum, UserDomain, VpnTestServer1, VpnTestServer2, VpnTestServer3)
  print("[Info] RecoverVpnConnection return code:", str(Status))
  return Status


# Marco for sending message.
def SendMsgToTelegram(msg):
  if TelegramNotifySwitch == 1:
    TelegramBot.sendMessage(FixedChatID, str(msg), disable_notification=False)


# Telebot callback function.
def TelebotMsgCallback(msg):
  global StopTelepotBot

  # MOTP number from user.
  MotpNum = msg['text']
  SendMsgToTelegram("MOTP: " + MotpNum + ", Got it!")

  # Using the MOTP number to recover the VPN.
  Status = RecoverVpn(MotpNum)

  # Stop the Telebot listener if VPN on-line.
  if Status == 0:
    SendMsgToTelegram("[Info] VPN on-line.")
    StopTelepotBot = True
  else:
    SendMsgToTelegram("[Failure] Batch return: " + str(Status))
    SendMsgToTelegram("Need your attention.")
    SendMsgToTelegram("MOTP?")


# Start the Telepot to get the MOTP number from user.
def GetMotpFromTelebot():
  global StopTelepotBot

  SendMsgToTelegram("Need your attention.")
  SendMsgToTelegram("MOTP?")
  print("[Action] Telegram BOT is listening...")
  
  StopTelepotBot = False
  MessageLoop(TelegramBot, TelebotMsgCallback).run_as_thread()
  while StopTelepotBot == False:
    time.sleep(5)


# Get MOTP number from command prompt.
def GetMotpFromUser():
  MotpNum = input("Need your attention.\nMOTP? ")

  # Using the MOTP number to recover the VPN.
  Status = RecoverVpn(MotpNum)
  return Status

# Get MOTP number from E-Mail
def GetMotpFromMail():
  print("[Action] Setup E-Mail Account")
  my_credentials = Credentials(username=UserMailAddress, password=UserPassword)
  my_config = Configuration(server=UserMailServer, credentials=my_credentials)
  my_account = Account(primary_smtp_address=UserMailAddress, config=my_config,
                        autodiscover=False, access_type=DELEGATE)

  # Mail title & Body.
  RandomString = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
  TitleStr = "[Test] Need your attention. " + RandomString
  BodyString = "MOTP?"

  print("[Action] Create a new mail item")
  # Create mail item
  item = Message(
      account=my_account,
      folder=my_account.sent,
      subject=TitleStr,
      body=BodyString,
      to_recipients=[Mailbox(email_address=UserMailAddress)]
  )

  print("[Action] Send")
  item.send()

  print("[Info] Done, E-Mail Subject: [", TitleStr, "]")

  WaitingForIt = True
  while WaitingForIt == True:
    # Delay
    print("[Action] Waiting for the mail response.", end='\r', flush=True)
    time.sleep(10)

    # Include the mail contains specific subject.
    UnreadMailBuffer = my_account.inbox.filter(subject__contains=TitleStr)

    for MailBuffer in UnreadMailBuffer:
      # Get first of line from mail
      StringBuffer = io.StringIO(MailBuffer.text_body)
      FirstLineOfMailBody = StringBuffer.readline()

      # Exclude notify mail that has the same string.
      if FirstLineOfMailBody != BodyString:
        # Try to convert first of line to Integer, break loop if success.
        try: 
          MotpNum = int(FirstLineOfMailBody)
          print("\nMOTP = ", MotpNum, ", Got it!")
          WaitingForIt = False
          break
        except ValueError:
          pass

  # Using the MOTP number to recover the VPN.
  Status = RecoverVpn(MotpNum)
  return Status

# Function for mailing.
def MailMe(BodyString, Attachment):
  with open(Attachment, 'rb') as InputFileBuffer:

    print("[Action] Setup mail configurations.")
    my_credentials = Credentials(username=UserMailAddress, password=UserPassword)
    my_config = Configuration(server=UserMailServer, credentials=my_credentials)
    my_account = Account(primary_smtp_address=UserMailAddress, config=my_config,
                          autodiscover=False, access_type=DELEGATE)

    # Mail title.
    TitleStr = "Clock In Report " + datetime.datetime.now().strftime('%H:%M')

    print("[Action] Create a mail with an attachment.")
    # Create mail item
    item = Message(
        account=my_account,
        folder=my_account.sent,
        subject=TitleStr,
        body=BodyString,
        to_recipients=[Mailbox(email_address=UserMailAddress)]
    )

    # Add attachment
    binary_file_content = InputFileBuffer.read()
    my_file = FileAttachment(name=Attachment.name, content=binary_file_content)
    item.attach(my_file)
    item.save()

    print("[Action] Send")
    item.send()

    print("[Action] Done, E-Mail Subject: [", TitleStr, "]")


# Clock in, Clock out.
def ClockInClockOut(TypeOfClockIn):
  print("[Info] Start clock in process, ClockIntype: ", str(TypeOfClockIn))

  # Launch Microsoft Edge (Chromium)
  EdgeOption = EdgeOptions()
  EdgeOption.binary_location = str(PathOfCurrent.joinpath('Edge/msedge.exe'))
  EdgeOption.use_chromium = True
  EdgeOption.add_argument('headless')
  EdgeOption.add_argument('disable-gpu')
  EdgeOption.add_experimental_option('excludeSwitches', ['enable-logging'])
  Browser = Edge(options = EdgeOption, executable_path=str(PathOfCurrent.joinpath('msedgedriver.exe')))
  Browser.implicitly_wait(3)

  # Check VPN status by trying the target site.
  VpnRetryError = True
  for x in range(0, VpnRetryLimit):
    try:
      Browser.set_page_load_timeout(10)
      Browser.get(ClockInServer)
      VpnRetryError = None
    except:
      if MotpGettingOption == "Telegram":
        print("[Action] Start TelegramBot to recover VPN")
        GetMotpFromTelebot()
      elif MotpGettingOption == "Email":
        print("[Action] Sending E-Mail to recover VPN")
        GetMotpFromMail()
      else:
        GetMotpFromUser()
      pass

    # Wait for 3 seconds before trying to fetch the data again
    if VpnRetryError:
        time.sleep(3)
    else:
        break

  if VpnRetryError == True:
    print("[Failure] Cannot recover VPN, process ternimate.")
    return

  # Store main window in order to switch back when alert window pop up.
  MainWindow = Browser.current_window_handle

  # Try to get the web time from target site.
  try:
    print("[Action] Check if element is located.")
    WebDriverWait(Browser, 1800, 1).until(EC.presence_of_element_located((By.XPATH, './/span[@class = "Hour"]')))
  except:
    pass  # Temporary ignore, maybe there will be another way to recovery this failure.
  finally:
    # Again, prevent it will sometime return exception when getting the H/M/S elements.
    WebDriverWait(Browser, 1800, 1).until(EC.presence_of_element_located((By.XPATH, './/span[@class = "Hour"]')))
    WebHour = Browser.find_element_by_xpath('.//span[@class = "Hour"]')
    WebMin = Browser.find_element_by_xpath('.//span[@class = "Min"]')
    WebSec = Browser.find_element_by_xpath('.//span[@class = "Second"]')
    print("[Info] Web Time -", WebHour.text, ":", WebMin.text, ":", WebSec.text)

    TimeOfWeb = datetime.time(int(WebHour.text), int(WebMin.text), int(WebSec.text))

  # Xpath depend on different type of clock in.
  if (TypeOfClockIn == 1):
    ClockInBtnIdByXpath = "//*[@id='Type1']"
  elif (TypeOfClockIn == 2):
    ClockInBtnIdByXpath = "//*[@id='Type2']"
  elif (TypeOfClockIn == 3):
    ClockInBtnIdByXpath = "//*[@id='Type3']"
  elif (TypeOfClockIn == 4):
    ClockInBtnIdByXpath = "//*[@id='Type4']"
  else:
    print("[Failure] Not support.")
    return

  # Try to click clock in button.
  try:
    print("[Action] Try if clock in button is clickable.")
    WebDriverWait(Browser, 1800, 1).until(EC.element_to_be_clickable((By.XPATH, ClockInBtnIdByXpath)))
  except:
    pass  # Temporary ignore, maybe there will be another way to recovery this failure.
  finally:
    # Capture a screenshot as one of the result.
    StrOfCurrentTime = time.strftime("%m%d_%H-%M-%S_") + TimeOfWeb.strftime("%H-%M-%S") + ".png"
    CaptureFile = PathOfCurrent.joinpath(StrOfCurrentTime)
    Browser.get_screenshot_as_file(CaptureFile.as_posix())
    print("[Info] Capture ScreenShot:", str(CaptureFile.as_posix()))

    # clock in!
    print("[Action] Click.")
    Browser.find_element_by_xpath(ClockInBtnIdByXpath).click()

    # Wait for the alert to be displayed
    try:
      WebDriverWait(Browser, 1800, 1).until(EC.alert_is_present())
    finally:
      # Store the alert in a variable for reuse
      BrowserAlert = Browser.switch_to.alert

      # Store the alert text in a variable
      AlertText = BrowserAlert.text

      # Press the Cancel button
      BrowserAlert.accept()

      ResultString = "[Web Time]" + TimeOfWeb.strftime("%H-%M-%S") + ", TypeOfClockIn: " + str(TypeOfClockIn) + ", Result: " + AlertText
      print("[Info] Clock in success\n" + ResultString)
      
      # Mail the result
      if EmailNotifySwitch == 1:
        print("[Action] Notify user through E-Mail.")
        MailMe(ResultString, CaptureFile)

      # Notify telegram user
      if TelegramNotifySwitch == 1:
        print("[Action] Notify user through Telegram.")
        SendMsgToTelegram("[Info] Clock in success\n" + ResultString)
        TelegramBot.sendPhoto(FixedChatID, photo=open(CaptureFile, 'rb'), disable_notification=False)

  #Close browser
  Browser.switch_to.window(MainWindow)
  Browser.close()


# For testing or one time clock in.
def testmain(argv):
  ClockInClockOut(1)
  # pass

# Main
def main(argv):
  # Add clock in schedules to scheduler
  # TODO: Change to BackgroundScheduler with listener and an interactive menu (re-schedule or something...)
  while True:
    try:
      print("[Action] Add jobs to schecduler.")
      scheduler = BlockingScheduler()
      scheduler.add_job(ClockInClockOut, 'cron', day_of_week='mon-fri', hour = 8, minute = 5, end_date = '2021-05-30', args=(1,))
      scheduler.add_job(ClockInClockOut, 'cron', day_of_week='mon-fri', hour = 12, minute = 10, end_date = '2021-05-30', args=(2,))
      scheduler.add_job(ClockInClockOut, 'cron', day_of_week='mon-fri', hour = 12, minute = 50, end_date = '2021-05-30', args=(3,))
      scheduler.add_job(ClockInClockOut, 'cron', day_of_week='mon-fri', hour = 18, minute = 30, end_date = '2021-05-30', args=(4,))
      print("[Action] Start schecduler.")
      scheduler.start()
    except Exception as ErrMsg:
      print("[Failure] Throw out exception.")
      print("[Action] Stop schecduler.")
      SendMsgToTelegram("[Failure] clock in schedule error.")
      SendMsgToTelegram(ErrMsg)
      scheduler.shutdown()
      pass


if __name__ == "__main__":
  main(sys.argv[1:])
