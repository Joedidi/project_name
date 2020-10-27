@ECHO OFF
cd %~dp0
set PATH=.\venv;.\venv\Scripts;%PATH%
python manage.py runserver 0.0.0.0:8080