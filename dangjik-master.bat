@echo off
title dangjik-master v1.0 (Duty Management System)
cls

echo ======================================================
echo    당직 마스터 자동 배정 시스템을 시작합니다.
echo    창을 닫으면 프로그램이 종료됩니다.
echo ======================================================
echo.

:: 1. 백그라운드에서 파이썬 서버 실행 (start /b)
start /b .\python.exe server.py

echo 서버가 가동 중입니다...
timeout /t 3 /nobreak > nul

:: 2. 기본 브라우저로 접속 주소 실행
start http://localhost:8000

echo.
echo [알림] 브라우저가 자동으로 열리지 않는다면 
echo        주소창에 http://localhost:8000 을 입력하세요.
echo.
echo ======================================================

:: 서버 로그를 실시간으로 확인하기 위해 프로세스를 유지합니다.
pause
