@echo off
chcp 65001 >nul
title Bank CRM

echo Запуск CRM...
call .venv\Scripts\activate

:: Запускаем агент в отдельном окне
start "Outlook Agent" /min cmd /c "python tools\outlook_agent.py"
timeout /t 2 >nul

:: Открываем браузер и запускаем CRM
start http://127.0.0.1:5000
python app.py

pause