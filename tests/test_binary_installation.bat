@echo on

set "installer_file=%1"
set "installation_loc=%2"

call "%installation_loc%\Scripts\activate.bat"
if errorlevel 1 exit 1

conda.exe info -a
conda.exe list
conda.exe list --explicit

call tests\run_tests.bat
if errorlevel 1 exit 1

set "BASH_EXE=C:\Program Files\Git\bin\bash.exe"

"%BASH_EXE%" -c "bash tests/run_prog_tests.sh"
if errorlevel 1 exit 1
