@echo off
echo Construyendo ejecutable...
pyinstaller --onefile --windowed --name "AgentSocialWeb" --add-data "app/templates;app/templates" --add-data "app/static;app/static" --add-data "src;src" --add-data "config.json;." --add-data ".env;." main_web.py
pause