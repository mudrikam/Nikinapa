@echo off
setlocal enabledelayedexpansion

REM =====================================================================
REM Nikinapa Launcher Script
REM Author: Mudrikul Hikam
REM Last Updated: May 8, 2025
REM 
REM This script performs the following tasks:
REM 1. If Python folder exists, directly runs main.py
REM 2. If Python folder doesn't exist:
REM    - Downloads Python 3.12.10 embedded distribution
REM    - Sets up pip in the embedded distribution
REM    - Updates application files from GitHub repository
REM    - Installs required packages from requirements.txt
REM    - Runs main.py
REM =====================================================================

REM Set base directory to the location of this batch file (removes trailing backslash)
set "BASE_DIR=%~dp0"
set "BASE_DIR=%BASE_DIR:~0,-1%"
set "PYTHON_DIR=%BASE_DIR%\python"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
set "MAIN_PY=%BASE_DIR%\main.py"

REM =====================================================================
REM Check if Python directory exists
REM If it exists, we can directly run the main.py file without setup
REM If not, we need to set up the environment first
REM =====================================================================
if exist "%PYTHON_DIR%" (
    echo Python installation found. Checking requirements...
    
    REM Check for requirements.txt and install if it exists
    if exist "%BASE_DIR%\requirements.txt" (
        echo Installing requirements from requirements.txt...
        "%PYTHON_EXE%" -m pip install -r "%BASE_DIR%\requirements.txt" --no-warn-script-location
    ) else (
        echo Warning: requirements.txt not found. Skipping package installation.
    )
    "%PYTHON_EXE%" "%MAIN_PY%"
    goto :eof
)

echo Python installation not found. Setting up environment...

REM =====================================================================
REM Define variables for setup process
REM =====================================================================
set "PYTHON_ZIP=%TEMP%\python-3.12.10-embed-amd64.zip"
set "PYTHON_URL=https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip"
set "REQUIREMENTS_FILE=%BASE_DIR%\requirements.txt"

REM =====================================================================
REM Create Python directory
REM =====================================================================
echo Creating Python directory...
mkdir "%PYTHON_DIR%"

REM =====================================================================
REM Download and extract Python embedded distribution
REM Uses PowerShell to download the file and extract it
REM =====================================================================
echo Downloading Python embedded distribution...
powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_ZIP%'"

echo Extracting Python...
powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force"

REM =====================================================================
REM Set up pip in the embedded Python distribution
REM 1. Check if requirements.txt exists, create if not
REM 2. Enable site-packages by modifying the _pth file
REM 3. Download and run get-pip.py to install pip
REM 4. Install required packages from requirements.txt
REM =====================================================================
echo Setting up pip...

REM Create requirements.txt if it doesn't exist
if not exist "%REQUIREMENTS_FILE%" (
    echo Creating empty requirements.txt file...
    echo. > "%REQUIREMENTS_FILE%"
)

REM Enable site-packages in embedded Python by modifying python*._pth file
REM This is required for pip to work in embedded distribution
for %%F in ("%PYTHON_DIR%\python*._pth") do (
    type "%%F" > "%%F.tmp"
    echo import site >> "%%F.tmp"
    move /y "%%F.tmp" "%%F"
)

REM Download get-pip.py and install pip
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PYTHON_DIR%\get-pip.py'"
"%PYTHON_DIR%\python.exe" "%PYTHON_DIR%\get-pip.py" --no-warn-script-location

REM Check if requirements.txt exists and install required packages
if exist "%REQUIREMENTS_FILE%" (
    echo Installing required packages from requirements.txt...
    "%PYTHON_DIR%\python.exe" -m pip install -r "%REQUIREMENTS_FILE%" --no-warn-script-location
) else (
    echo Warning: requirements.txt not found. Skipping package installation.
)

REM =====================================================================
REM Update application files from GitHub repository
REM This section creates a temporary batch file to handle the GitHub
REM update process, which avoids syntax issues with special characters.
REM 
REM The update process:
REM 1. Gets the latest release information from GitHub API
REM 2. Extracts the download URL
REM 3. Downloads the latest version
REM 4. Extracts the files
REM 5. Updates the application files
REM 6. Cleans up temporary files
REM
REM This approach uses a separate batch file to avoid issues with
REM complex PowerShell commands and special characters like { and }.
REM =====================================================================
echo Checking for updates from GitHub repository...

REM Create a temporary update batch file with detailed comments
set "UPDATE_SCRIPT=%TEMP%\update_nikinapa.bat"
echo @echo off > "%UPDATE_SCRIPT%"
echo setlocal enabledelayedexpansion >> "%UPDATE_SCRIPT%"
echo REM Define temporary directories and files >> "%UPDATE_SCRIPT%"
echo set "TEMP_DIR=%%TEMP%%" >> "%UPDATE_SCRIPT%"
echo set "RELEASE_INFO=%%TEMP_DIR%%\release_info.json" >> "%UPDATE_SCRIPT%"
echo set "DOWNLOAD_ZIP=%%TEMP_DIR%%\nikinapa_latest.zip" >> "%UPDATE_SCRIPT%"
echo set "EXTRACT_DIR=%%TEMP_DIR%%\nikinapa_update" >> "%UPDATE_SCRIPT%"
echo set "BASE_DIR=%BASE_DIR%" >> "%UPDATE_SCRIPT%"
echo. >> "%UPDATE_SCRIPT%"
echo REM Step 1: Get the latest release information from GitHub API >> "%UPDATE_SCRIPT%"
echo echo Fetching latest release info... >> "%UPDATE_SCRIPT%"
echo powershell -Command "Invoke-RestMethod -Uri 'https://api.github.com/repos/mudrikam/Nikinapa/releases/latest' -OutFile '%%RELEASE_INFO%%'" >> "%UPDATE_SCRIPT%"
echo. >> "%UPDATE_SCRIPT%"
echo REM Step 2: Extract the download URL from the release information >> "%UPDATE_SCRIPT%"
echo echo Getting download URL... >> "%UPDATE_SCRIPT%"
echo for /f "tokens=2 delims=:, " %%%%A in ('findstr "zipball_url" "%%RELEASE_INFO%%"') do ( >> "%UPDATE_SCRIPT%"
echo   set "DOWNLOAD_URL=%%%%~A" >> "%UPDATE_SCRIPT%"
echo   set "DOWNLOAD_URL=!DOWNLOAD_URL:~1,-1!" >> "%UPDATE_SCRIPT%"
echo ) >> "%UPDATE_SCRIPT%"
echo. >> "%UPDATE_SCRIPT%"
echo REM Check if a download URL was found >> "%UPDATE_SCRIPT%"
echo if not defined DOWNLOAD_URL ( >> "%UPDATE_SCRIPT%"
echo   echo No download URL found. >> "%UPDATE_SCRIPT%"
echo   goto cleanup >> "%UPDATE_SCRIPT%"
echo ) >> "%UPDATE_SCRIPT%"
echo. >> "%UPDATE_SCRIPT%"
echo REM Step 3: Download the latest version >> "%UPDATE_SCRIPT%"
echo echo Downloading latest version... >> "%UPDATE_SCRIPT%"
echo powershell -Command "Invoke-WebRequest -Uri '!DOWNLOAD_URL!' -OutFile '%%DOWNLOAD_ZIP%%'" >> "%UPDATE_SCRIPT%"
echo. >> "%UPDATE_SCRIPT%"
echo REM Step 4: Extract the downloaded files >> "%UPDATE_SCRIPT%"
echo echo Extracting files... >> "%UPDATE_SCRIPT%"
echo if exist "%%EXTRACT_DIR%%" rmdir /s /q "%%EXTRACT_DIR%%" >> "%UPDATE_SCRIPT%"
echo powershell -Command "Expand-Archive -Path '%%DOWNLOAD_ZIP%%' -DestinationPath '%%EXTRACT_DIR%%' -Force" >> "%UPDATE_SCRIPT%"
echo. >> "%UPDATE_SCRIPT%"
echo REM Step 5: Update the application files >> "%UPDATE_SCRIPT%"
echo echo Updating application files... >> "%UPDATE_SCRIPT%"
echo REM Get the directory name inside the extracted folder (GitHub adds a unique folder name) >> "%UPDATE_SCRIPT%"
echo for /f "tokens=*" %%%%G in ('dir /b /a:d "%%EXTRACT_DIR%%"') do ( >> "%UPDATE_SCRIPT%"
echo   set "RELEASE_DIR=%%EXTRACT_DIR%%\%%%%G" >> "%UPDATE_SCRIPT%"
echo ) >> "%UPDATE_SCRIPT%"
echo. >> "%UPDATE_SCRIPT%"
echo REM Copy all files from the release directory to the base directory >> "%UPDATE_SCRIPT%"
echo xcopy "!RELEASE_DIR!\*" "%%BASE_DIR%%" /e /y /i >> "%UPDATE_SCRIPT%"
echo. >> "%UPDATE_SCRIPT%"
echo REM Step 6: Clean up temporary files >> "%UPDATE_SCRIPT%"
echo :cleanup >> "%UPDATE_SCRIPT%"
echo echo Cleaning up... >> "%UPDATE_SCRIPT%"
echo if exist "%%RELEASE_INFO%%" del "%%RELEASE_INFO%%" >> "%UPDATE_SCRIPT%"
echo if exist "%%DOWNLOAD_ZIP%%" del "%%DOWNLOAD_ZIP%%" >> "%UPDATE_SCRIPT%"
echo if exist "%%EXTRACT_DIR%%" rmdir /s /q "%%EXTRACT_DIR%%" >> "%UPDATE_SCRIPT%"
echo. >> "%UPDATE_SCRIPT%"
echo echo Update process completed. >> "%UPDATE_SCRIPT%"
echo endlocal >> "%UPDATE_SCRIPT%"

REM Run the temporary update script
call "%UPDATE_SCRIPT%"

REM Delete the temporary update script
del "%UPDATE_SCRIPT%"

REM =====================================================================
REM Clean up temporary files from the Python installation
REM =====================================================================
if exist "%PYTHON_ZIP%" del "%PYTHON_ZIP%"
if exist "%PYTHON_DIR%\get-pip.py" del "%PYTHON_DIR%\get-pip.py"

REM =====================================================================
REM Launch the application
REM =====================================================================
echo Setup complete. Running main.py...
"%PYTHON_EXE%" "%MAIN_PY%"

endlocal