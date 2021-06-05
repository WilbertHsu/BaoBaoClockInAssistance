import subprocess
import pathlib
import shutil
import os

PathOfCurrent = pathlib.Path(__file__).parent.absolute()


def TestVpnConnection(TargetSite):
  print("[Action] Testing connection:", TargetSite)
  # ping -n 1 %1 > NUL
  BatchProcess = subprocess.run("ping -n 1 {0} >NUL".format(TargetSite),
                                cwd=PathOfCurrent,
                                shell=True
                            )
  return BatchProcess.returncode


def CheckIfVpnAlreadyConnect(VpnName):
  print("[Action] Checking the existence of VPN:", VpnName)
  # ipconfig|find /I "!VpnName!" > NUL
  BatchProcess = subprocess.run('ipconfig|find /i "{0}" >NUL'.format(VpnName),
                                cwd=PathOfCurrent,
                                shell=True
                            )
  print(BatchProcess.returncode)
  return BatchProcess.returncode


def ConnectToVpn(VpnName, VpnAccount, VpnPassword, MotpNumber, VpnDomain):
  print("[Action] Connecting to the VPN.")
  # Using the MOTP number to recover the VPN.
  VpnPassword = "{0}{1}".format(VpnPassword, MotpNumber)
  VpnDomain = "/domain:{0}".format(VpnDomain)
  BatchProcess = subprocess.run(["rasdial", VpnName, VpnAccount, VpnPassword, VpnDomain],
                                cwd=PathOfCurrent,
                                shell=True
                            )
  return BatchProcess.returncode


def HangUpVpn(VpnName):
  print("[Action] Hanging up current VPN.")
  # By rasdial /disconnect command
  BatchProcess = subprocess.run(["call", "rasdial", VpnName, "/disconnect"],
                                cwd=PathOfCurrent,
                                shell=True
                            )
  return BatchProcess.returncode


def RecoverVpnConnection(UserVpnName, UserName, UserPassword, UserMotpNum, UserDomain, VpnTestServer1, VpnTestServer2, VpnTestServer3):
  # Copy .\UserVpnName.pbk to %userprofile%\AppData\Roaming\Microsoft\Network\Connections\Pbk\UserVpnName.pbk
  PathOfOsPbk = pathlib.Path(os.path.expandvars(r"%userprofile%\AppData\Roaming\Microsoft\Network\Connections\Pbk"))
  PathOfOsPbk.mkdir(parents=True, exist_ok=True)
  VpnFileName = UserVpnName + ".pbk"
  shutil.copy2(PathOfCurrent.joinpath(VpnFileName).as_posix(), PathOfOsPbk.joinpath(VpnFileName).as_posix())

  # Hang up currect VPN connection if possible.
  if CheckIfVpnAlreadyConnect(UserVpnName) == 0:
    Status = HangUpVpn(UserVpnName)
    if Status != 0:
      return Status
  
  # Connect VPN
  Status = ConnectToVpn(UserVpnName, UserName, UserPassword, UserMotpNum, UserDomain)
  if Status != 0:
      return Status

  # Testing connection with VpnTestSserver
  Status = TestVpnConnection(VpnTestServer1)
  if Status != 0:
      return Status

  Status = TestVpnConnection(VpnTestServer2)
  if Status != 0:
      return Status

  Status = TestVpnConnection(VpnTestServer3)
  if Status != 0:
      return Status
  
  return Status
