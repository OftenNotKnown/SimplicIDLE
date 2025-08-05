@echo off
setlocal

:: Set paths
set "INSTALL_DIR=%LOCALAPPDATA%\SimplicEditor"
set "ZIP_PATH=%TEMP%\simplic.zip"
set "EXTRACT_DIR=%TEMP%\simplic_extracted"
set "VBS_FILE=%TEMP%\create_shortcut.vbs"
set "SHORTCUT_NAME=SimplicEditor.lnk"
set "EXE_PATH=%INSTALL_DIR%\main\main.exe"

:: Clean previous temp
rd /s /q "%EXTRACT_DIR%" >nul 2>&1
mkdir "%EXTRACT_DIR%"

:: Download repo
echo ⬇️ Downloading SimplicEditor...
powershell -Command "Invoke-WebRequest -Uri https://github.com/OftenNotKnown/SimplicIDLE/archive/refs/heads/main.zip -OutFile '%ZIP_PATH%'"

:: Extract it
echo 📦 Extracting...
tar -xf "%ZIP_PATH%" -C "%EXTRACT_DIR%"
del "%ZIP_PATH%"

:: Move main/ folder into install dir
echo 🚚 Moving files...
mkdir "%INSTALL_DIR%" >nul 2>&1
xcopy /E /I /Y "%EXTRACT_DIR%\SimplicIDLE-main\main" "%INSTALL_DIR%\main"
rd /s /q "%EXTRACT_DIR%"

:: Run SSD to install dependencies
echo 🧠 Running setup script (SSD)...
pushd "%INSTALL_DIR%\main\utils"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -Command "Start-Process python SSD.py -Wait"
popd

:: Create desktop shortcut
echo 🔗 Creating shortcut on Desktop...
> "%VBS_FILE%" echo Set oWS = WScript.CreateObject("WScript.Shell")
>> "%VBS_FILE%" echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\%SHORTCUT_NAME%"
>> "%VBS_FILE%" echo Set oLink = oWS.CreateShortcut(sLinkFile)
>> "%VBS_FILE%" echo oLink.TargetPath = "%EXE_PATH%"
>> "%VBS_FILE%" echo oLink.WorkingDirectory = "%INSTALL_DIR%\main"
>> "%VBS_FILE%" echo oLink.IconLocation = "%EXE_PATH%, 0"
>> "%VBS_FILE%" echo oLink.Save
cscript //nologo "%VBS_FILE%"
del "%VBS_FILE%"

:: Launch the app
echo 🚀 Launching SimplicEditor...
start "" "%EXE_PATH%"

echo ✅ Install complete!
pause
