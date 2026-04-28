@echo off
chcp 65001 >nul
title QHUN22 - Quản Lý Server

setlocal enabledelayedexpansion
cd /d "%~dp0"

set "PYTHON_EXE="
set "PYTHON_VERSION="
set "PY_MAJOR="
set "PY_MINOR="
set "TARGET_PYTHON_MINOR=10"
set "TARGET_PYTHON_DISPLAY=3.10"
set "IMPORTANT_PKGS=django allauth requests openpyxl dotenv"
set "AI_PKGS=numpy sklearn sentence_transformers faiss fastapi uvicorn pydantic"
set "VENV_DIR=.venv"

:: Tạo thư mục logs nếu chưa tồn tại
if not exist "logs" mkdir logs

:: ========================================
:: Tự động xin quyền Admin nếu chưa có
:: ========================================
net session >nul 2>&1
if errorlevel 1 (
    echo [i] Đang yêu cầu quyền Administrator...
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d \"%~dp0\" && \"%~f0\" %*' -Verb RunAs" >nul 2>&1
    exit /b
)

:main_menu
cls
echo ╔════════════════════════════════════════╗
echo ║       QHUN22 - Menu Quản Lý            ║
echo ╠════════════════════════════════════════╣
echo ║                                        ║
echo ║  [0] Setup Full Tự Động                ║
echo ║  ─────────────────────────────────     ║
echo ║  [1] Khởi động Server (Chạy Local)     ║
echo ║  [2] Khởi động Server (Production)     ║
echo ║                                        ║
echo ╚════════════════════════════════════════╝
echo.
set /p choice="Chọn chức năng [0-2]: "

if "%choice%"=="0" goto setup_full_auto
if "%choice%"=="1" goto start_server_local
if "%choice%"=="2" goto start_server_prod

echo.
echo [!] Lựa chọn không hợp lệ!
timeout /t 2 >nul
goto main_menu


:detect_python
py -%TARGET_PYTHON_DISPLAY% --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=py -%TARGET_PYTHON_DISPLAY%"
    goto detect_python_version
)

python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=python"
    goto detect_python_version
)

py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=py -3"
    goto detect_python_version
)

set "PYTHON_EXE="
goto :eof

:detect_python_version
for /f "tokens=*" %%v in ('%PYTHON_EXE% -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2^>nul') do set "PYTHON_VERSION=%%v"
for /f "tokens=*" %%v in ('%PYTHON_EXE% -c "import sys; print(sys.version_info.major)" 2^>nul') do set "PY_MAJOR=%%v"
for /f "tokens=*" %%v in ('%PYTHON_EXE% -c "import sys; print(sys.version_info.minor)" 2^>nul') do set "PY_MINOR=%%v"

if not "%PY_MAJOR%"=="3" (
    set "PYTHON_EXE="
    set "PYTHON_VERSION="
    set "PY_MAJOR="
    set "PY_MINOR="
    goto :eof
)

if not defined PY_MINOR (
    set "PYTHON_EXE="
    set "PYTHON_VERSION="
    set "PY_MAJOR="
    set "PY_MINOR="
    goto :eof
)

if %PY_MINOR% LSS 10 (
    set "PYTHON_EXE="
    set "PYTHON_VERSION="
    set "PY_MAJOR="
    set "PY_MINOR="
)
goto :eof


:activate_venv
:: Thử .venv trước, rồi venv
if exist "%VENV_DIR%\Scripts\activate.bat" (
    call %VENV_DIR%\Scripts\activate.bat >nul 2>&1
    if errorlevel 1 goto activate_venv_fail
    exit /b 0
)
if exist "venv\Scripts\activate.bat" (
    set "VENV_DIR=venv"
    call venv\Scripts\activate.bat >nul 2>&1
    if errorlevel 1 goto activate_venv_fail
    exit /b 0
)
echo [!] Không tìm thấy venv! Hãy chạy [0] Setup Full trước.
exit /b 1

:activate_venv_fail
echo [!] Không thể kích hoạt Virtual Environment.
echo     Venv có thể bị lỗi. Chạy [0] Setup Full để tạo lại.
exit /b 1


:verify_package
set "PKG_NAME=%~1"
python -c "import importlib, sys; importlib.import_module('%PKG_NAME%')" >nul 2>&1
if errorlevel 1 (
    echo    [THIẾU] %PKG_NAME%
    set /a MISSING_COUNT+=1
) else (
    echo    [OK] %PKG_NAME%
)
goto :eof


:start_server_local
cls
echo ==========================================
echo   Khởi Động Server (Chạy Local)
echo ==========================================
echo.
echo [i] Đang cấu hình biến môi trường cho Local...
echo     - DEBUG=True
echo     - ALLOWED_HOSTS=127.0.0.1, localhost
echo     - CLOUDFLARE TURNSTILE = Bypass (Test Key)
echo.
set "DEBUG=True"
set "ALLOWED_HOSTS=127.0.0.1,localhost,*"
set "CLOUDFLARE_TURNSTILE_SITE_KEY=1x00000000000000000000AA"
set "CLOUDFLARE_TURNSTILE_SECRET_KEY=1x0000000000000000000000000000000AA"
set "VNPAY_RETURN_URL=http://127.0.0.1:8000/vnpay/return/"
set "VNPAY_IPN_URL=http://127.0.0.1:8000/vnpay/ipn/"
set "MOMO_RETURN_URL=http://127.0.0.1:8000/momo/return/"
set "MOMO_IPN_URL=http://127.0.0.1:8000/momo/ipn/"
goto start_server_common

:start_server_prod
cls
echo ==========================================
echo   Khởi Động Server (Production / Hosting)
echo ==========================================
echo.
echo [i] Đang sử dụng cấu hình gốc từ file .env...
goto start_server_common

:start_server_common
call :activate_venv
if errorlevel 1 (
    echo.
    echo [!] Không thể kích hoạt Virtual Environment!
    echo    Đảm bảo thư mục venv tồn tại.
    timeout /t 3 >nul
    goto main_menu
)

echo.
echo [i] Đang kiểm tra database...
python manage.py migrate --run-syncdb

echo.
echo [OK] Database sẵn sàng!
echo.
if "%DEBUG%"=="True" (
    echo [i] Đang khởi động server LOCAL tại http://127.0.0.1:8000/
) else (
    echo [i] Đang khởi động server PRODUCTION theo cấu hình .env
)
echo [i] Log server se hien thi truc tiep tren terminal
echo [i] Log chatbot: logs\chatbot.log
echo [i] Bấm Ctrl+C để dừng server
echo.
set "DJANGO_LOG_LEVEL=INFO"
set "QH_CHATBOT_LOG_LEVEL=INFO"
python manage.py runserver
goto main_menu


:setup_full_auto
cls
echo ╔════════════════════════════════════════╗
echo ║   SETUP FULL TỰ ĐỘNG - QHUN22          ║
echo ╠════════════════════════════════════════╣
echo ║                                        ║
echo ║  Script sẽ tự động:                    ║
echo ║  1. Kiểm tra Python                    ║
echo ║  2. Xóa venv lỗi + tạo venv mới        ║
echo ║  3. Cài tất cả thư viện                ║
echo ║  4. Chạy database migration            ║
echo ║  5. Kiểm tra .env                      ║
echo ║                                        ║
echo ║  Không cần thao tác thêm — chờ xong!   ║
echo ║                                        ║
echo ╚════════════════════════════════════════╝
echo.

set "MISSING_COUNT=0"
set "SETUP_ERRORS=0"

:: ──── BƯỚC 1: Kiểm tra Python ────
echo ────────────────────────────────────────
echo  [1/6] Kiểm tra Python...
echo ────────────────────────────────────────
call :detect_python
if "%PYTHON_EXE%"=="" (
    echo.
    echo  [THẤT BẠI] Không tìm thấy Python phù hợp!
    echo.
    echo  Vui lòng cài Python 3.10+ từ:
    echo     https://www.python.org/downloads/
    echo.
    echo  QUAN TRỌNG: Khi cài, tick ☑ "Add Python to PATH"
    echo             và tick ☑ "Install py launcher"
    echo.
    echo  Sau khi cài xong, đóng cửa sổ này và chạy lại bat.
    echo.
    pause
    goto main_menu
)
for /f "tokens=*" %%v in ('%PYTHON_EXE% --version 2^>^&1') do echo  Phiên bản: %%v
echo  [OK] Python hợp lệ!
if not "%PY_MINOR%"=="%TARGET_PYTHON_MINOR%" (
    echo  [CẢNH BÁO] Máy đang dùng Python %PYTHON_VERSION%.
    echo           Khuyến nghị dùng Python %TARGET_PYTHON_DISPLAY% để ổn định nhất.
)
echo.

:: ──── BƯỚC 2: Kiểm tra + Tạo venv ────
echo ────────────────────────────────────────
echo  [2/6] Kiểm tra Virtual Environment...
echo ────────────────────────────────────────

set "VENV_NEED_CREATE=0"

:: Kiểm tra venv có tồn tại không
if not exist "%VENV_DIR%\Scripts\python.exe" (
    if not exist "venv\Scripts\python.exe" (
        echo  [i] Chưa có venv — sẽ tạo mới.
        set "VENV_NEED_CREATE=1"
    ) else (
        set "VENV_DIR=venv"
    )
)

:: Kiểm tra venv có bị lỗi user khác không (lỗi phổ biến nhất!)
if "%VENV_NEED_CREATE%"=="0" (
    %VENV_DIR%\Scripts\python.exe --version >nul 2>&1
    if errorlevel 1 (
        echo  [!] Venv bị lỗi (Python path không khớp máy hiện tại^)
        echo      Đây là lỗi phổ biến khi copy project giữa các máy.
        echo      Đang xóa venv cũ và tạo lại...
        set "VENV_NEED_CREATE=1"
    ) else (
        echo  [OK] Venv hoạt động bình thường.
    )
)

:: Tạo venv mới nếu cần
if "%VENV_NEED_CREATE%"=="1" (
    echo.
    echo  [i] Đang dọn dẹp venv cũ...
    if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%" >nul 2>&1
    if exist "venv" rmdir /s /q "venv" >nul 2>&1
    set "VENV_DIR=.venv"
    echo  [i] Đang tạo venv mới bằng %PYTHON_EXE%...
    %PYTHON_EXE% -m venv %VENV_DIR% >nul 2>&1
    if errorlevel 1 (
        echo  [THẤT BẠI] Không thể tạo venv!
        echo             Thử chạy thủ công: %PYTHON_EXE% -m venv .venv
        set /a SETUP_ERRORS+=1
        pause
        goto main_menu
    )
    echo  [OK] Đã tạo venv mới tại %VENV_DIR%\
)
echo.

:: ──── BƯỚC 3: Kích hoạt venv + nâng cấp pip ────
echo ────────────────────────────────────────
echo  [3/6] Kích hoạt venv + nâng cấp pip...
echo ────────────────────────────────────────
call :activate_venv
if errorlevel 1 (
    set /a SETUP_ERRORS+=1
    pause
    goto main_menu
)
python -m pip install --upgrade pip setuptools wheel --quiet --disable-pip-version-check --no-warn-script-location
if errorlevel 1 (
    echo  [CẢNH BÁO] Không thể cập nhật pip — tiếp tục cài thư viện.
) else (
    echo  [OK] pip/setuptools/wheel đã cập nhật.
)
echo.

:: ──── BƯỚC 4: Cài thư viện ────
echo ────────────────────────────────────────
echo  [4/6] Cài đặt thư viện...
echo ────────────────────────────────────────
echo.

:: 4a: Core requirements
if not exist "requirements.txt" (
    echo  [THẤT BẠI] Không tìm thấy requirements.txt
    set /a SETUP_ERRORS+=1
    pause
    goto main_menu
)

echo  [i] Đang cài core packages (requirements.txt)...
pip install -r requirements.txt --disable-pip-version-check --no-warn-script-location
if errorlevel 1 (
    echo.
    echo  [THẤT BẠI] Cài đặt core requirements gặp lỗi!
    echo  Kiểm tra kết nối mạng rồi chạy lại [0].
    set /a SETUP_ERRORS+=1
) else (
    echo  [OK] Core packages đã cài xong.
)
echo.

:: 4b: Packages thường thiếu (không có trong requirements.txt nhưng cần)
echo  [i] Đang cài packages bổ sung (Pillow, PyJWT, cryptography)...
pip install Pillow PyJWT cryptography --disable-pip-version-check --no-warn-script-location --quiet
if errorlevel 1 (
    echo  [CẢNH BÁO] Một số package bổ sung cài lỗi — có thể cần cài thủ công.
) else (
    echo  [OK] Packages bổ sung đã cài xong.
)
echo.

:: 4c: AI requirements (tùy chọn)
if exist "ai\ai_requirements.txt" (
    echo  [i] Phát hiện ai\ai_requirements.txt — đang cài thư viện AI...
    pip install -r ai\ai_requirements.txt --disable-pip-version-check --no-warn-script-location
    if errorlevel 1 (
        echo  [CẢNH BÁO] Cài AI packages có lỗi — web app vẫn chạy được.
    ) else (
        echo  [OK] AI packages đã cài xong.
    )
) else (
    echo  [i] Không có ai\ai_requirements.txt — bỏ qua AI.
)
echo.

:: 4d: Kiểm tra packages quan trọng
echo  [i] Kiểm tra nhanh packages quan trọng...
for %%p in (%IMPORTANT_PKGS%) do call :verify_package %%p

echo.
echo  [i] Packages bổ sung...
for %%p in (PIL jwt cryptography) do call :verify_package %%p

if exist "ai\ai_requirements.txt" (
    echo.
    echo  [i] Packages AI...
    for %%p in (%AI_PKGS%) do call :verify_package %%p
)

echo.
if "%MISSING_COUNT%"=="0" (
    echo  [OK] Tất cả packages đều sẵn sàng!
) else (
    echo  [CẢNH BÁO] Còn %MISSING_COUNT% package chưa import được.
    echo           Nếu lỗi thuộc nhóm AI, app web vẫn chạy bình thường.
)
echo.

:: ──── BƯỚC 5: Database migration ────
echo ────────────────────────────────────────
echo  [5/6] Chạy database migration...
echo ────────────────────────────────────────
echo.
python manage.py migrate --run-syncdb
if errorlevel 1 (
    echo.
    echo  [CẢNH BÁO] Migration gặp vấn đề — có thể cần cấu hình .env trước.
    set /a SETUP_ERRORS+=1
) else (
    echo.
    echo  [OK] Database sẵn sàng.
)
echo.

:: ──── BƯỚC 6: Kiểm tra .env ────
echo ────────────────────────────────────────
echo  [6/6] Kiểm tra file .env...
echo ────────────────────────────────────────
echo.
if not exist ".env" (
    echo  [CẢNH BÁO] Chưa có file .env!
    echo.
    echo  Tạo file .env trong thư mục gốc với nội dung tối thiểu:
    echo.
    echo    SECRET_KEY=your-secret-key
    echo    DEBUG=True
    echo    ALLOWED_HOSTS=127.0.0.1,localhost
    echo    ANTHROPIC_API_KEY=your-api-key  (cho chatbot)
    echo.
    echo  Xem đầy đủ trong SETUP.md hoặc README.md
) else (
    echo  [OK] File .env đã có sẵn.
)
echo.

:: ──── TỔNG KẾT ────
echo.
if "%SETUP_ERRORS%"=="0" (
    echo ╔════════════════════════════════════════╗
    echo ║   SETUP HOÀN TẤT THÀNH CÔNG!           ║
    echo ╠════════════════════════════════════════╣
    echo ║                                        ║
    echo ║  Bước tiếp theo:                       ║
    echo ║    Chọn [1] để khởi động server        ║
    echo ║    Truy cập: http://127.0.0.1:8000/    ║
    echo ║                                        ║
    echo ║                                        ║
    echo ╚════════════════════════════════════════╝
) else (
    echo ╔════════════════════════════════════════╗
    echo ║   HOÀN TẤT (có %SETUP_ERRORS% cảnh báo)║
    echo ╠════════════════════════════════════════╣
    echo ║                                        ║
    echo ║  Có một số lỗi nhỏ, kiểm tra lại:      ║
    echo ║    - File .env đã tạo chưa?            ║
    echo ║    - Kết nối Internet ổn không?        ║
    echo ║    - Thử chạy lại [0] sau khi fix      ║
    echo ║                                        ║
    echo ╚════════════════════════════════════════╝
)
echo.
pause
goto main_menu
