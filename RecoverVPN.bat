@echo off
setlocal EnableDelayedExpansion

set "VpnName=%1"
set "VpnUserName=%2"
set "VpnPassword=%3"
set "VpnMotpNum=%4"
set "VpnTestServer1=%5"
set "VpnTestServer2=%6"
set "VpnTestServer3=%7"

set "File_Of_VPN=%userprofile%\AppData\Roaming\Microsoft\Network\Connections\Pbk\!VpnName!.pbk"
set "WORKSPACE=%~dp0"
pushd "!WORKSPACE!"

:MainLoop
call :ReclaimVPN
call :TestConnection !VpnTestServer1!
if "!errorlevel!" neq "0" exit /b !errorlevel!
call :TestConnection !VpnTestServer2!
if "!errorlevel!" neq "0" exit /b !errorlevel!
call :TestConnection !VpnTestServer3!
if "!errorlevel!" neq "0" exit /b !errorlevel!

echo [Info] Good to go.
exit /b 0

:TestConnection
echo [Action] Testing %1
ping -n 1 %1 > NUL
if "!errorlevel!" neq "0" (
  echo [Info] Cannot access to "%1"
  if "!errorlevel!" neq "0" exit /b !errorlevel!
)
exit /b 0

:ReclaimVPN
copy /y "!WORKSPACE!\!VpnName!.pbk" "!File_Of_VPN!"

echo [Action] Check !VpnName! status.
ipconfig|find /I "!VpnName!" > NUL

if "!errorlevel!" equ "0" (
  echo [ACTION] Hang up current VPN
  call :HangUpVPN
  if "!errorlevel!" neq "0" exit /b !errorlevel!
)

echo [Action] Re-Connect VPN
call :ConnectVPN
exit /b !errorlevel!


:ConnectVPN
echo [Action] Connect VPN with "rasdial !VpnName! !VpnUserName! !VpnPassword!!VpnMotpNum!"
rasdial !VpnName! !VpnUserName! !VpnPassword!!VpnMotpNum!
exit /b !errorlevel!

:HangUpVPN
rasdial !VpnName! /disconnect
exit /b !errorlevel!
