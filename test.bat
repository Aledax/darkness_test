@echo off

start cmd /k "call server.bat"
timeout /t 2 /nobreak >nul
start cmd /k "call client.bat"
start cmd /k "call client.bat"