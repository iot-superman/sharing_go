Set-Location $PSScriptRoot
if (!(Test-Path .venv)) { py -m venv .venv }
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
Start-Process 'http://127.0.0.1:8000'
python manage.py runserver 0.0.0.0:8000
