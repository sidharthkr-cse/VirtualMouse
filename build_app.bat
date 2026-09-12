@echo off
echo Installing required build tools (PyInstaller)...
python -m pip install pyinstaller

echo.
echo Building VirtualMouse Application into a single .EXE file...
echo This might take a few minutes as it bundles AI libraries...
"C:\Users\siddh\AppData\Roaming\Python\Python314\Scripts\pyinstaller.exe" --name VirtualMouseApp --onefile --collect-all mediapipe --icon website\assets\logo.ico app\main.py

echo.
echo =======================================================
echo BUILD COMPLETE! 
echo You can find your App inside the "dist" folder.
echo Copy the dist/VirtualMouseApp.exe file anywhere you want.
echo =======================================================
pause
