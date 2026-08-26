@echo off
setlocal 
    REM 區域環境

set "PROJECT_ROOT=%~dp0.." 
    REM %~dp0 取得 Batch 檔所在目錄
    REM return from scripts directory to project root
set "SERVER=%PROJECT_ROOT%\runtime\llama.cpp\llama-server.exe"
set "MODEL=%PROJECT_ROOT%\models\qwen3-vl-8b\Qwen3-VL-8B-Instruct-abliterated-v2.0.Q4_K_M.gguf"

REM 檢查 server 必要檔案
if not exist "%SERVER%" (
    echo [ERROR] llama-server.exe not found:
    echo %SERVER%
    exit /b 1
)

REM 檢查 model 必要檔案
if not exist "%MODEL%" (
    echo [ERROR] GGUF model not found:
    echo %MODEL%
    exit /b 1
)

echo Starting Local Qwen Model API
echo Model: qwen3-vl-8b
echo URL: http://127.0.0.1:8080
echo. 
    REM echo. 空行

REM 核心指令
"%SERVER%" ^
    -m "%MODEL%" ^
    --alias qwen3-vl-8b ^
    --host 127.0.0.1 ^
    --port 8080 ^
    -c 16384 ^
    -np 1 ^
    -ngl 99 ^
    --jinja

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo llama-server stopped with exit code %EXIT_CODE%.
exit /b %EXIT_CODE%
