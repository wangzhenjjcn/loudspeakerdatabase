set "SCRIPT_DIR=%~dp0"
python -m pip install --upgrade pip
pip install  -r requirements.txt  -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install pyinstaller  -i https://pypi.tuna.tsinghua.edu.cn/simple
python -O -m PyInstaller -y -F -w -n APP  %SCRIPT_DIR%\app.py 
@pause
@pause